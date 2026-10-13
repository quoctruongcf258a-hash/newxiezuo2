"""collab_auto.py — 程序二 全自动串跑（复用 auto_pipeline 骨架，作用于 LINKS）。

与程序一 auto_pipeline 逻辑一致：从当前环节顺序跑到最后，失败重试 +
等待落盘 + 超时补发。区别：阶段源为 stage_board.LINKS，落盘判定用 check_link，
发送走 pipeline_runner.execute_stage 的 assigned action（支持 dry-run 模拟）。
"""
import os
import sys
import time
import threading

import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导
sys.path.insert(0, paths.WINDOWS_USE)

from stage_board import (load_links, get_current_key, set_current_key,
                         find_link_index, check_link, refresh_index)
from pipeline_runner import execute_stage, set_dry_run

STEP_TIMEOUT_MIN = 40
POLL_SEC = 15
RESEND_AFTER_MIN = 15
SEND_RETRY = 3
RETRY_WAIT_SEC = 20


def _ts():
    return time.strftime("%H:%M:%S")


class CollabAuto:
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
        links = load_links()
        refresh_index(links)
        total = len(links)
        if total == 0:
            self.log_fn("⚠ 无环节，结束")
            return
        idx = find_link_index(get_current_key(), links)
        self.log_fn(f"🚀 程序二全自动开始 [{_ts()}]，从环节 {idx+1}/{total} 起")

        done_count = 0
        for i in range(idx, total):
            if self._stop:
                self.log_fn("⏸ 收到停止信号，结束")
                return
            link = links[i]
            key = link["key"]
            set_current_key(key)
            self.log_fn(f"\n===== [{i+1}/{total}] {link['name']} [{_ts()}] =====")

            ok, t, done = check_link(link)
            if done:
                self.log_fn(f"✅ 已达标 ({ok}/{t})，跳过执行")
                done_count += 1
            else:
                sent = False
                for attempt in range(1, SEND_RETRY + 1):
                    try:
                        self.log_fn(f"📤 执行中... 当前 {ok}/{t}（第 {attempt}/{SEND_RETRY} 次）")
                        execute_stage(link, self.log_fn)
                        sent = True
                        break
                    except Exception as e:
                        self.log_fn(f"❌ 第 {attempt} 次执行失败: {e}")
                        if attempt < SEND_RETRY:
                            time.sleep(RETRY_WAIT_SEC)
                if not sent:
                    self.log_fn("⚠ 多次执行失败，标记异常后继续")

                finished = self._wait_until_done(link)
                if not finished:
                    self.log_fn(f"⚠ {link['name']} 超时未完成，末次补发后推进")
                    try:
                        execute_stage(link, self.log_fn)
                    except Exception as e:
                        self.log_fn(f"  末次补发失败: {e}")
                    if check_link(link)[2]:
                        done_count += 1
                else:
                    done_count += 1

            if i + 1 < total:
                set_current_key(links[i + 1]["key"])
                self.log_fn(f"→ 推进到 [{i+2}/{total}] {links[i+1]['name']}")
            time.sleep(2)

        incomplete = total - done_count
        self.log_fn(f"\n🎉 程序二跑完：{done_count}/{total} 环节达标"
                    + (f"，{incomplete} 个环节未齐（需人工补发）" if incomplete else "，全部完成！"))

    def _wait_until_done(self, link):
        start = time.time()
        last_log = 0
        last_resend = 0
        while True:
            if self._stop:
                return False
            el = time.time() - start
            if el > STEP_TIMEOUT_MIN * 60:
                self.log_fn(f"⚠ 超时 {STEP_TIMEOUT_MIN} 分钟")
                return False

            ok, total, done = check_link(link)
            if done:
                self.log_fn(f"✅ {link['name']} 落盘完成 ({ok}/{total})")
                return True

            if time.time() - last_log > 30:
                self.log_fn(f"  [{int(el // 60)}分] {link['name']} 进度 {ok}/{total}")
                last_log = time.time()

            if el > RESEND_AFTER_MIN * 60 and time.time() - last_resend > RESEND_AFTER_MIN * 60:
                self.log_fn(f"🔁 超 {RESEND_AFTER_MIN} 分钟未齐，自动补发（只发未达标）")
                try:
                    execute_stage(link, self.log_fn)
                except Exception as e:
                    self.log_fn(f"  补发失败: {e}")
                last_resend = time.time()

            time.sleep(POLL_SEC)
