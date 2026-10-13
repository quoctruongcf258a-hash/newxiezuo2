"""全自动流水线：从当前阶段一路跑到最后"""
import os, sys, time, threading
import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导
sys.path.insert(0, paths.WINDOWS_USE)

from pipeline import STAGES, KEY2STAGE, get_current_key, set_current_key, find_stage_index, check_stage
from pipeline_runner import execute_stage, rerun_stage

# 每步最大等待分钟
STEP_TIMEOUT_MIN = 40
# 落盘轮询间隔（秒）
POLL_SEC = 15
# 自动补发：超过这么久还没齐，就重发一次
RESEND_AFTER_MIN = 15
# 阶段广播失败重试次数与间隔
SEND_RETRY = 3
RETRY_WAIT_SEC = 20


def _ts():
    return time.strftime("%H:%M:%S")


class AutoPipeline:
    def __init__(self, log_fn, done_fn=None):
        self.log_fn = log_fn
        self.done_fn = done_fn
        self._stop = False
        self._thread = None

    def stop(self):
        self._stop = True
        self.log_fn("⏸ 收到停止信号")

    def start(self):
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        try:
            self._loop()
        except Exception as e:
            self.log_fn(f"❌ 异常: {e}")
        finally:
            if self.done_fn:
                self.done_fn()

    def _loop(self):
        stages = STAGES
        total = len(stages)
        idx = find_stage_index(get_current_key())
        self.log_fn(f"🚀 全自动开始 [{_ts()}]，从阶段 {idx+1}/{total} 起")

        done_count = 0
        for i in range(idx, total):
            if self._stop:
                self.log_fn("⏸ 收到停止信号，结束")
                return
            stage = stages[i]
            key = stage["key"]
            set_current_key(key)
            self.log_fn(f"\n===== [{i+1}/{total}] {stage['name']} [{_ts()}] =====")

            # 1. 已完成则跳过
            ok, t, done = check_stage(stage)
            if done:
                self.log_fn(f"✅ 已 100% ({ok}/{t})，跳过执行")
                done_count += 1
            else:
                # 2. 执行（失败重试 + 退避）
                sent = False
                for attempt in range(1, SEND_RETRY + 1):
                    try:
                        self.log_fn(f"📤 广播中... 当前 {ok}/{t}（第 {attempt}/{SEND_RETRY} 次）")
                        execute_stage(key, self.log_fn)
                        sent = True
                        break
                    except Exception as e:
                        self.log_fn(f"❌ 第 {attempt} 次执行失败: {e}")
                        if attempt < SEND_RETRY:
                            time.sleep(RETRY_WAIT_SEC)
                if not sent:
                    self.log_fn("⚠ 多次执行失败，标记本阶段异常后继续")

                # 3. 等待落盘（中途 15min 自动补发未达标家）
                finished = self._wait_until_done(stage)
                if not finished:
                    # 超时未齐：末次补发一次本阶段，仍不齐也推进（避免卡死）
                    self.log_fn(f"⚠ {stage['name']} 超时未完成，末次补发后推进")
                    try:
                        rerun_stage(key, self.log_fn)
                    except Exception as e:
                        self.log_fn(f"  末次补发失败: {e}")
                    if check_stage(stage)[2]:
                        done_count += 1
                else:
                    done_count += 1

            # 4. 推进
            if i + 1 < total:
                set_current_key(stages[i + 1]["key"])
                self.log_fn(f"→ 推进到 [{i+2}/{total}] {stages[i+1]['name']}")
            time.sleep(2)

        incomplete = total - done_count
        self.log_fn(f"\n🎉 全自动跑完：{done_count}/{total} 阶段达标"
                    + (f"，{incomplete} 个阶段未齐（需人工补发）" if incomplete else "，全部完成！"))

    def _wait_until_done(self, stage):
        start = time.time()
        last_log = 0
        last_resend = 0
        while True:
            if self._stop: return False
            el = time.time() - start
            if el > STEP_TIMEOUT_MIN * 60:
                self.log_fn(f"⚠ 超时 {STEP_TIMEOUT_MIN} 分钟")
                return False

            ok, total, done = check_stage(stage)
            if done:
                self.log_fn(f"✅ {stage['name']} 落盘完成 ({ok}/{total})")
                return True

            # 每 30 秒打一次
            if time.time() - last_log > 30:
                el_min = int(el // 60)
                self.log_fn(f"  [{el_min}分] {stage['name']} 进度 {ok}/{total}")
                last_log = time.time()

            # 15 分钟没齐 → 自动补发一次
            if el > RESEND_AFTER_MIN * 60 and time.time() - last_resend > RESEND_AFTER_MIN * 60:
                self.log_fn(f"🔁 超 {RESEND_AFTER_MIN} 分钟未齐，自动补发（只发未达标）")
                try:
                    execute_stage(stage["key"], self.log_fn)
                except Exception as e:
                    self.log_fn(f"  补发失败: {e}")
                last_resend = time.time()

            time.sleep(POLL_SEC)
