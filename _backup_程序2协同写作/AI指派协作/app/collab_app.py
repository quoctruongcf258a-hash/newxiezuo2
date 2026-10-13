"""collab_app.py — 程序二·协同写作独立主窗口。"""
import sys
import time
import os
import json
import shutil

import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导
sys.path.insert(0, paths.APP_ROOT)

from phase_runner import run_phase, generate, set_call_ai  # 通用环节/子环执行引擎

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter, QApplication,
    QTextEdit, QLabel, QComboBox, QPushButton, QGroupBox, QLineEdit,
    QToolBar, QTabWidget, QSizePolicy, QStackedWidget, QFormLayout,
    QScrollArea, QSpinBox, QButtonGroup, QRadioButton, QCheckBox,
    QFileDialog,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt as _Qt, QEvent, QThread, Signal

from ui_base import ConsoleBase, apply_dark, sb, AssignPanel
from assign_panel import BTN_3D_QSS
from ruler_overlay import RulerOverlay


class _WBFileWorker(QThread):
    """后台监听步骤0产出目录：直接让 WorkBuddy 把结果写成文件（参考 v0.8
    判定机制，提示词 no0tisc.md 已要求 AI 落盘到该目录），通过文件大小是否
    稳定来判定 AI 是否生成完毕；稳定即视为完成，发出 done 信号进入下一步。"""
    log = Signal(str)
    done = Signal(str)

    POLL_SEC = 4            # 轮询间隔（秒）
    MAX_ROUNDS = 600        # 最多轮次（约 40 分钟）
    MIN_BYTES = 200         # 低于此大小视为尚未写完整
    STABLE_NEED = 3         # 连续 N 次大小不变即判定完成

    def __init__(self, watch_dir, start_time, proj_name="", min_bytes=None):
        super().__init__()
        self.watch_dir = watch_dir
        self.start_time = start_time   # 仅统计此时间之后新建/修改的文件
        self.proj_name = proj_name
        self.min_bytes = min_bytes if min_bytes is not None else self.MIN_BYTES

    def _candidates(self):
        import os
        exts = (".json", ".md", ".txt")
        out = []
        try:
            names = os.listdir(self.watch_dir)
        except Exception:
            return out
        for f in names:
            if not f.lower().endswith(exts):
                continue
            fp = os.path.join(self.watch_dir, f)
            try:
                st = os.stat(fp)
            except Exception:
                continue
            if st.st_mtime < self.start_time:   # 跳过本次发送之前就存在的旧文件
                continue
            out.append((fp, st.st_size))
        return out

    def run(self):
        import os, time
        os.makedirs(self.watch_dir, exist_ok=True)
        last_size = -1
        stable = 0
        target = None
        self.log.emit(f"⏳ 开始监听产出目录：{self.watch_dir}")
        for _ in range(self.MAX_ROUNDS):
            try:
                cands = self._candidates()
                if cands:
                    cands.sort(key=lambda x: os.stat(x[0]).st_mtime, reverse=True)
                    fp, sz = cands[0]
                    target = fp
                    if sz >= self.min_bytes:
                        if sz == last_size:
                            stable += 1
                        else:
                            stable = 0
                            last_size = sz
                        if stable >= self.STABLE_NEED:
                            self.log.emit(f"✅ 文件大小已稳定，判定生成完成：{fp}")
                            self.done.emit(fp)
                            return
                    else:
                        last_size = sz
                        stable = 0
            except Exception as e:
                self.log.emit(f"⚠ 监听产出目录失败：{e}")
            time.sleep(self.POLL_SEC)
        self.log.emit("⏱ 监听超时（约40分钟）未判定完成")
        if target:
            self.log.emit(f"⚠ 超时但已检测到文件：{target}，仍标记为完成")
            self.done.emit(target)


class _WebCaptureWorker(QThread):
    """网页端 AI：发送后用 CDP 从页面抓取回复并落盘（网页端无法自写文件，
    不能走目录监听）。轮询 mix_send.capture_with_meta 直到「真实助手消息气泡」
    文本稳定，才写入产出目录——避免把整页回退文本（n==0，如网页原有内容/欢迎语）
    误判为完成而生成假的「完工文件」。"""
    log = Signal(str)
    done = Signal(str)

    POLL_SEC = 4
    MAX_ROUNDS = 600
    MIN_BYTES = 100
    STABLE_NEED = 2

    def __init__(self, ai_name, out_dir, proj_name=""):
        super().__init__()
        self.ai_name = ai_name
        self.out_dir = out_dir
        self.proj_name = proj_name

    def run(self):
        import os, time, sys
        sys.path.insert(0, paths.WINDOWS_USE)
        from mix_send import capture_with_meta as _cap
        os.makedirs(self.out_dir, exist_ok=True)
        target = os.path.join(self.out_dir, "故事梗概.md")
        prev = ""
        stable = 0
        ever_real = False
        self.log.emit("网页端：从页面抓取回复并落盘（仅认助手气泡，忽略整页回退）…")
        for _ in range(self.MAX_ROUNDS):
            try:
                meta = _cap(self.ai_name) or {}
                txt = (meta.get("text", "") or "").strip()
                n = meta.get("n", 0)
            except Exception as e:
                self.log.emit(f"抓取异常：{e}")
                txt, n = "", 0
            if txt and n > 0:
                ever_real = True
                if txt == prev:
                    stable += 1
                else:
                    stable = 0
                    prev = txt
                self.log.emit(f"抓取中（助手气泡 {n} 个，{len(prev)} 字符，稳定 {stable}）")
                if stable >= self.STABLE_NEED:
                    try:
                        with open(target, "w", encoding="utf-8") as f:
                            f.write(prev)
                        self.log.emit(f"✅ 已抓到真实回复并保存（{len(prev)} 字符）-> {target}")
                        self.done.emit(target)
                        return
                    except Exception as e:
                        self.log.emit(f"写文件失败：{e}")
            elif txt and n == 0:
                self.log.emit("· 本轮仅抓到整页回退文本（无助手气泡），继续等待 AI 回复…")
            else:
                self.log.emit("· 本轮未抓到文本，继续等待…")
            time.sleep(self.POLL_SEC)
        if ever_real and prev.strip():
            try:
                with open(target, "w", encoding="utf-8") as f:
                    f.write(prev)
                self.log.emit(f"⚠ 抓取超时，已保存最后抓到的回复（{len(prev)} 字符）-> {target}")
                self.done.emit(target)
                return
            except Exception:
                pass
        elif not ever_real:
            self.log.emit("❌ 网页端始终未出现助手回复（n==0，可能粘贴未成功或页面结构变化）")
        else:
            self.log.emit("❌ 网页端未能抓取到回复（请确认已登录且 CDP 端口正确）")


class _PlanGenWorker(QThread):
    """环节0 规划：把提示词发给 WorkBuddy，抓取一整块文本输出（不让 AI 写文件），
    再按两个标记拆成 故事梗概.md / AI建议调整方向.md。"""
    progress = Signal(str)
    done = Signal(bool, str)   # (成功?, 失败信息/空)

    GENERATING_JS = (
        "(() => {"
        "  const ags = [...document.querySelectorAll('.cr-agent')];"
        "  if (!ags.length) return 'no-agent';"
        "  const last = ags[ags.length-1];"
        "  const cls = last.className.toString();"
        "  const stop = [...document.querySelectorAll('button')]"
        "     .some(b => (b.getAttribute('aria-label')||'') === '停止');"
        "  return (cls.indexOf('processing') >= 0 || stop) ? 'gen' : 'done';"
        "})()"
    )
    READ_AGENT_JS = (
        "(() => {"
        "  const ags = [...document.querySelectorAll('.cr-agent')];"
        "  if (!ags.length) return '';"
        "  const last = ags[ags.length-1];"
        "  const c = last.querySelector('.cr-agent__content');"
        "  return c ? c.innerText : last.innerText;"
        "})()"
    )
    MARKER1 = "===文件1：故事梗概.md==="
    MARKER2 = "===文件2：AI建议调整方向.md==="

    def __init__(self, prompt, out_dir, proj_name=""):
        super().__init__()
        self.prompt = prompt
        self.out_dir = out_dir
        self.proj_name = proj_name

    def _ensure_wb(self):
        import sys, time
        sys.path.insert(0, paths.WINDOWS_USE)
        try:
            from players import launch as _launch, load_players as _load_players
        except Exception as e:
            self.progress.emit(f"⚠ 导入 players 失败：{e}")
            return
        port = 9227
        if not _cdp_alive(port):
            self.progress.emit("🚀 WorkBuddy 未运行，正在启动…")
            try:
                cfg = _load_players()
                wb = next((x for x in cfg if x.get("名字") == "WorkBuddy"), None)
                if wb:
                    _launch(wb)
            except Exception as e:
                self.progress.emit(f"⚠ 启动 WorkBuddy 失败：{e}")
            for _ in range(25):
                if _cdp_alive(port):
                    break
                time.sleep(1)

    def _capture(self):
        import sys, time
        sys.path.insert(0, paths.WINDOWS_USE)
        from mix_send import CDPTab
        port = 9227
        last_len = -1
        stable = 0
        for _ in range(600):   # 最多约 30 分钟
            try:
                t = CDPTab(port, "")
                status = t.js(self.GENERATING_JS)
                content = t.js(self.READ_AGENT_JS) or ""
            except Exception as e:
                self.progress.emit(f"⚠ 轮询 WorkBuddy 失败：{e}")
                time.sleep(3)
                continue
            if status == "gen":
                self.progress.emit(f"⏳ WorkBuddy 生成中…（当前 {len(content)} 字）")
                stable = 0
                time.sleep(3)
                continue
            if len(content) == last_len:
                stable += 1
            else:
                stable = 0
                last_len = len(content)
            if stable >= 2 and len(content) > 0:
                return content
            if status == "no-agent":
                self.progress.emit("⏳ 尚未检测到对话，继续等待…")
            time.sleep(3)
        try:
            t = CDPTab(port, "")
            return t.js(self.READ_AGENT_JS) or ""
        except Exception:
            return ""

    def run(self):
        import os
        try:
            self._ensure_wb()
            self.progress.emit("📤 正在发送提示词到 WorkBuddy…")
            from mix_send import send as cdp_send
            r = cdp_send("WorkBuddy", self.prompt)
            self.progress.emit(f"📨 发送结果：{r}")
            self.progress.emit("⏳ 等待 WorkBuddy 生成…")
            text = self._capture()
        except Exception as e:
            self.done.emit(False, f"调用 WorkBuddy 失败：{e}")
            return
        if not text.strip():
            self.done.emit(False, "未取到 WorkBuddy 输出")
            return
        # 步骤5：按两个标记拆分
        i1 = text.find(self.MARKER1)
        i2 = text.find(self.MARKER2)
        if i1 == -1 or i2 == -1:
            err_path = os.path.join(self.out_dir, "ERROR.md")
            try:
                with open(err_path, "w", encoding="utf-8") as f:
                    f.write(text.strip() + "\n")
            except Exception:
                pass
            self.done.emit(False, "生成格式异常，请重试")
            return
        part1 = text[i1 + len(self.MARKER1):i2].strip()
        part2 = text[i2 + len(self.MARKER2):].strip()
        try:
            with open(os.path.join(self.out_dir, "故事梗概.md"), "w", encoding="utf-8") as f:
                f.write(part1 + "\n")
            with open(os.path.join(self.out_dir, "AI建议调整方向.md"), "w", encoding="utf-8") as f:
                f.write(part2 + "\n")
        except Exception as e:
            self.done.emit(False, f"写入产出文件失败：{e}")
            return
        self.done.emit(True, "")


def _cdp_alive(port):
    """检查某个 CDP 端口是否可访问（即对应 AI 应用是否已启动）。"""
    import urllib.request
    if not port:
        return False
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3) as f:
            return f.status == 200
    except Exception:
        return False


def _wb_generate(prompt, log_fn=print):
    """发送 prompt 到 WorkBuddy 并等待生成，返回整块文本（不让 AI 写文件）。"""
    import sys as _sys, time as _t
    _sys.path.insert(0, paths.WINDOWS_USE)
    try:
        from players import launch as _launch, load_players as _load_players
    except Exception as e:
        log_fn(f"⚠ 导入 players 失败：{e}")
        return ""
    port = 9227
    if not _cdp_alive(port):
        log_fn("🚀 WorkBuddy 未运行，正在启动…")
        try:
            cfg = _load_players()
            wb = next((x for x in cfg if x.get("名字") == "WorkBuddy"), None)
            if wb:
                _launch(wb)
        except Exception as e:
            log_fn(f"⚠ 启动 WorkBuddy 失败：{e}")
        for _ in range(25):
            if _cdp_alive(port):
                break
            _t.sleep(1)
    log_fn("📤 正在发送提示词到 WorkBuddy…")
    from mix_send import send as cdp_send
    r = cdp_send("WorkBuddy", prompt)
    log_fn(f"📨 发送结果：{r}")
    log_fn("⏳ 等待 WorkBuddy 生成…")
    return _wb_capture(log_fn)


def _wb_capture(log_fn=print):
    """轮询 WorkBuddy 最后一个 agent 的输出，稳定后返回整块文本。"""
    import sys as _sys, time as _t
    _sys.path.insert(0, paths.WINDOWS_USE)
    from mix_send import CDPTab
    port = 9227
    last_len = -1
    stable = 0
    for _ in range(600):   # 最多约 30 分钟
        try:
            t = CDPTab(port, "")
            status = t.js(_PlanGenWorker.GENERATING_JS)
            content = t.js(_PlanGenWorker.READ_AGENT_JS) or ""
        except Exception as e:
            log_fn(f"⚠ 轮询 WorkBuddy 失败：{e}")
            _t.sleep(3)
            continue
        if status == "gen":
            log_fn(f"⏳ WorkBuddy 生成中…（当前 {len(content)} 字）")
            stable = 0
            _t.sleep(3)
            continue
        if len(content) == last_len:
            stable += 1
        else:
            stable = 0
            last_len = len(content)
        if stable >= 2 and len(content) > 0:
            return content
        if status == "no-agent":
            log_fn("⏳ 尚未检测到对话，继续等待…")
        _t.sleep(3)
    try:
        t = CDPTab(port, "")
        return t.js(_PlanGenWorker.READ_AGENT_JS) or ""
    except Exception:
        return ""


class _PhaseRunWorker(QThread):
    """环节1（及其他大环节）后台运行：调 run_phase，逐子环日志，结束发 done。"""
    progress = Signal(str)
    done = Signal(bool, str)

    def __init__(self, phase_name, project_dir, proj_name, finalize):
        super().__init__()
        self.phase_name = phase_name
        self.project_dir = project_dir
        self.proj_name = proj_name
        self.finalize = finalize

    def _log(self, msg):
        self.progress.emit(msg)

    def run(self):
        try:
            # 把 phase_runner 的 AI 调用换成真实 WorkBuddy（忽略角色名，统一走 WorkBuddy）
            set_call_ai(
                lambda role, ai_name, prompt, log_fn=None: _wb_generate(prompt, log_fn or self._log))
            run_phase(self.phase_name, log_fn=self._log,
                      project_dir=self.project_dir, finalize=self.finalize)
            self.done.emit(True, "")
        except Exception as e:
            import traceback
            self._log(f"❌ 环节运行异常：{e}\n{traceback.format_exc()}")
            self.done.emit(False, f"环节运行异常：{e}")


class _StageRunWorker(QThread):
    """auto_stage.run_stage 后台线程：运行单个大环节，避免冻结 UI。"""
    progress = Signal(str)
    refresh = Signal()
    done = Signal(bool, str)

    def __init__(self, stage_key, dry=False, chapter=None):
        super().__init__()
        self.stage_key = stage_key
        self.dry = dry
        self.chapter = chapter

    def run(self):
        try:
            import collab_exec as _ce
            _ce.start_run()
            _ce.resume()
            ok = _ce.run_stage(self.stage_key, self.progress.emit, self.dry,
                               self.refresh.emit, chapter=self.chapter)
            if ok:
                self.done.emit(True, "")
            else:
                self.done.emit(False, "环节未全部通过，请检查指派与结果")
        except Exception as e:
            import traceback
            self.progress.emit(f"❌ 环节运行异常：{e}\n{traceback.format_exc()}")
            self.done.emit(False, f"环节运行异常：{e}")


class _StageNextWorker(QThread):
    """手动模式：只发送一个大环节中下一个子项（块/审核/调整），避免冻结 UI。"""
    progress = Signal(str)
    refresh = Signal()
    done = Signal(bool, str)

    def __init__(self, stage_key, dry=False, chapter=None):
        super().__init__()
        self.stage_key = stage_key
        self.dry = dry
        self.chapter = chapter

    def run(self):
        try:
            import collab_exec as _ce
            _ce.start_run()
            _ce.resume()
            ok = _ce.run_next_item(self.stage_key, self.progress.emit, self.dry,
                                   self.refresh.emit, chapter=self.chapter)
            self.done.emit(bool(ok), "")
        except Exception as e:
            import traceback
            self.progress.emit(f"❌ 手动发送异常：{e}\n{traceback.format_exc()}")
            self.done.emit(False, f"手动发送异常：{e}")


class CollabApp(ConsoleBase):
    auto_refresh = Signal()
    auto_log = Signal(str)

    GENRE_SUBS = {
        "都市": ["都市生活", "都市异能", "职场商战", "娱乐明星", "游戏竞技", "豪门世家", "重生都市"],
        "玄幻": ["东方玄幻", "奇幻冒险", "洪荒神话", "魔法学院", "异界大陆", "龙族", "神族", "无敌流",
                "凡人修仙", "仙侠修真", "重生修仙", "仙尊归来", "废柴逆袭", "长生流", "道祖", "剑修"],
        "历史": ["架空历史", "穿越三国", "唐朝风云", "宋朝风流", "军事历史", "明朝那些事", "民国风云"],
        "科幻": ["星际战争", "末世生存", "机甲武装", "无限流", "赛博朋克", "时空穿梭", "进化变异", "外星文明"],
        "悬疑": ["推理探案", "灵异鬼怪", "惊悚恐怖", "盗墓探险", "克苏鲁", "悬疑推理", "密室逃脱", "心理惊悚"],
        "游戏": ["电子竞技", "游戏异界", "网游竞技", "全职高手流", "虚拟现实", "游戏制作人"],
        "体育": ["篮球", "足球", "体育竞技", "运动热血", "乒乓球", "格斗"],
        "军事": ["战争烽火", "特战军旅", "谍战特工", "雇佣兵", "军事科幻"],
        "二次元": ["动漫同人", "二次元", "轻小说", "日常喜剧", "声优", "漫画"],
        "奇幻": ["西方奇幻", "史诗奇幻", "骑士与魔法", "龙与地下城", "巫师流"],
        "武侠": ["传统武侠", "江湖恩怨", "武林争霸", "侠客行", "新派武侠"],
    }
    PERSONALITY_TRAITS = [
        "冷傲", "腹黑", "温柔", "霸道", "沙雕", "高冷", "暖男", "御姐",
        "甜妹", "女强人", "草根崛起", "天才流", "搞笑", "温馨", "治愈", "黑暗",
        "冷静", "理智", "疯狂", "偏执", "病娇", "元气", "软萌", "霸气",
        "温润", "狡黠", "直爽", "隐忍", "果断", "优柔", "傲慢", "谦逊",
    ]
    EMOTION_TAGS = [
        "无CP", "1V1", "双女主", "多女主", "后宫", "百合", "甜宠", "虐文",
        "大女主", "年上", "年下", "青梅竹马", "破镜重圆", "先婚后爱", "欢喜冤家", "暗恋成真",
        "替身", "追妻火葬场", "双向奔赴", "虐恋情深", "治愈系", "BE美学", "重生", "穿越",
        "系统", "无限流", "快穿", "种田", "宫斗", "宅斗", "爽文", "无敌流",
        "日常文", "马甲文", "空间", "预知", "读心", "电竞", "直播", "网红",
        "娱乐圈", "修仙",
    ]
    GOLDEN_FINGER_TAGS = [
        "炼气", "筑基", "金丹", "大女主", "金手指", "异能", "科技", "魔法", "商城", "签到",
        "抽奖", "加点", "面板", "图鉴", "合成", "召唤", "契约", "变身", "隐藏身份", "系统流",
        "穿书", "重生复仇", "天才流", "废柴逆袭", "扮猪吃虎", "基建", "经营", "美食", "医术", "玄学",
    ]
    CHAR_TEMPLATES = ["师父型", "伙伴型", "对手型", "宠物型", "系统精灵", "路人甲"]
    STORY_TONES = ["热血燃", "轻松日常", "虐心催泪", "治愈温暖", "悬疑烧脑"]
    STORY_ATMOS = ["轻松", "紧张", "温馨", "黑暗", "神秘"]
    STORY_PACES = ["快节奏（每章爆点）", "标准节奏", "慢节奏（铺垫细腻）"]

    def __init__(self):
        super().__init__("程序二 · 协同写作控制台")

        if hasattr(self, "log_dock"):
            self.log_dock.close()
        for tb in self.findChildren(QToolBar):
            tb.setVisible(False)

        self.reference_outline = ""
        self._current_init_data = {}

        self._build_collab_central()
        self._build_left_run()
        self._sync_ais_to_players()
        self.auto_refresh.connect(self._on_auto_refresh)
        self.auto_log.connect(self.log_line)

        self.setFixedWidth(670)
        self.setMinimumHeight(595)
        self.resize(670, 935)

        self.ruler = RulerOverlay(self)
        self.ruler.resize(self.size())
        self.ruler.setVisible(False)
        self.ruler.raise_()
        self.shot_dir = os.path.join(paths.APP_DIR, "screenshots")
        QApplication.instance().installEventFilter(self)

    def _toggle_ruler(self):
        vis = not self.ruler.isVisible()
        self.ruler.setVisible(vis)
        self.ruler_btn.setText("📏" if not vis else "✕")
        self.ruler_btn.setToolTip("尺子" if not vis else "关尺")
        self.shot_btn.setVisible(vis)
        if not vis:
            self.ruler.clear_cursor()
            self.ruler.clear_measure()

    def _take_screenshot(self, region):
        try:
            os.makedirs(self.shot_dir, exist_ok=True)
            stamp = time.strftime("%Y%m%d_%H%M%S")
            if region:
                rect = self.ruler.measure_rect()
                if rect is None or rect.width() < 2 or rect.height() < 2:
                    self.log_line("📸 截图：请先左键点选起点并移动鼠标")
                    return
                pix = self.grab(rect)
                path = os.path.join(self.shot_dir, f"ruler_{stamp}.png")
                kind = f"测量区域 {rect.width()}×{rect.height()}"
            else:
                pix = self.grab()
                path = os.path.join(self.shot_dir, f"window_{stamp}.png")
                kind = "整个窗口"
            if pix.save(path):
                self.log_line(f"📸 截图已保存({kind})：{path}")
            else:
                self.log_line(f"❌ 截图保存失败：{path}")
        except Exception as e:
            self.log_line(f"❌ 截图失败：{e}")

    def eventFilter(self, obj, event):
        if not self.ruler.isVisible():
            return super().eventFilter(obj, event)
        et = event.type()
        if et == QEvent.MouseMove:
            gp = event.globalPos()
            if self.geometry().contains(gp):
                self.ruler.set_cursor(self.mapFromGlobal(gp))
        elif et == QEvent.MouseButtonPress:
            gp = event.globalPos()
            if self.geometry().contains(gp):
                pos = self.mapFromGlobal(gp)
                if event.button() == _Qt.RightButton:
                    self.ruler.clear_measure()
                else:
                    self.ruler.set_measure_start(pos)
        elif et == QEvent.KeyPress:
            if (event.key() == _Qt.Key_S
                    and event.modifiers() & _Qt.ControlModifier
                    and event.modifiers() & _Qt.ShiftModifier):
                self._take_screenshot(True)
                return True
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if getattr(self, "ruler", None):
            self.ruler.resize(self.size())
            self.ruler.update()
        # Stage0.5 展示框随窗口高度按比例放大（最小 600）
        edit = getattr(self, "summary_edit", None)
        if edit is not None and self.stack.currentIndex() == 1:
            h = max(600, int(self.height() * 0.62))
            edit.setMinimumHeight(h)


    def _build_collab_central(self):
        self.stage_panels = []
        self.tabs = QTabWidget()
        self.tabs.tabBar().hide()
        for i, st in enumerate(sb.PIPELINE, 1):
            panel = AssignPanel(with_runner=False, stages=[st["key"]])
            panel.run_callback = lambda sk=st["key"]: self._run_collab_stage(sk)
            panel.manual_next_callback = lambda sk=st["key"]: self._run_collab_next_item(sk)
            panel.stop_callback = self.on_stop
            panel.pause_callback = self._on_pause
            panel.gate_changed_callback = self._refresh_all_panels
            panel.release_advance_callback = lambda nxt=None: self._advance_and_run_next(nxt)
            panel._log = self.log_line
            panel.open_plan_callback = self._open_plan_file
            panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.stage_panels.append(panel)

            self.proj_name_labels = getattr(self, "proj_name_labels", [])
            container = QWidget()
            cv = QVBoxLayout(container)
            cv.setContentsMargins(6, 3, 6, 6)
            cv.setSpacing(2)
            desc = QLabel(st.get("desc", ""))
            desc.setWordWrap(True)
            desc.setAlignment(_Qt.AlignHCenter)
            desc.setStyleSheet("color:#aaaaaa; padding:2px 0px;")
            cv.addWidget(desc)
            # 当前项目名称（环节窗口上方红框位置）；项目创建后由 set_project_name 更新
            proj_lbl = QLabel("")
            proj_lbl.setAlignment(_Qt.AlignHCenter)
            proj_lbl.setStyleSheet("color:#00e5ff; font-weight:bold; font-size:13px;")
            cv.addWidget(proj_lbl)
            self.proj_name_labels.append(proj_lbl)
            cv.addWidget(panel, 1, _Qt.AlignTop)
            cv.addStretch(1)
            self.tabs.addTab(container, f"环节{i} {st['label']}")

        nav = QWidget()
        nh = QHBoxLayout(nav)
        nh.setContentsMargins(0, 4, 0, 4)
        nh.setSpacing(12)

        btn_prev = QPushButton("← 上一步")
        btn_next = QPushButton("下一步 →")
        btn_next.setToolTip("本环节所有子步都通过(✔)才能进入下一环节；点 ✖ 可从断点重新推进")
        self.btn_next = btn_next

        btn_prev.clicked.connect(self._on_prev)
        btn_next.clicked.connect(self._on_next)

        self.stage_indicator = QLabel()
        self.stage_indicator.setAlignment(_Qt.AlignCenter)
        self.stage_indicator.setStyleSheet("font-size:14px; font-weight:bold;")

        nh.addWidget(btn_prev)
        nh.addStretch(1)
        nh.addWidget(self.stage_indicator)
        nh.addStretch(1)
        nh.addWidget(btn_next)

        self.tabs.currentChanged.connect(self._update_nav)

        self.top = QWidget()
        tv = QVBoxLayout(self.top)
        tv.setContentsMargins(0, 0, 0, 0)
        tv.setSpacing(4)
        tv.addWidget(nav)
        tv.addWidget(self.tabs, 1)

        self.log_chat = QGroupBox("日志 · 单聊")
        self.log_chat.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lc = QVBoxLayout(self.log_chat)
        lc.setContentsMargins(6, 6, 6, 6)
        lc.setSpacing(4)

        self.run_log = QTextEdit()
        self.run_log.setReadOnly(True)
        self.run_log.setFont(QFont("Consolas", 9))
        lc.addWidget(self.run_log, 1)

        chat = QWidget()
        ch = QHBoxLayout(chat)
        ch.setContentsMargins(0, 0, 0, 0)
        ch.addWidget(QLabel("单聊:"))
        self.chat_ai = QComboBox()
        self.chat_ai.setMinimumWidth(120)
        self.chat_in = QLineEdit()
        self.chat_in.setPlaceholderText("输入消息，回车或点发送…")
        self.chat_btn = QPushButton("发送")
        self.chat_btn.setMaximumWidth(80)
        ch.addWidget(self.chat_ai)
        ch.addWidget(self.chat_in, 1)
        ch.addWidget(self.chat_btn)
        lc.addWidget(chat)

        self.top.setFixedHeight(460)

        central = QWidget()
        cv = QVBoxLayout(central)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(0)
        cv.addWidget(self.top)
        cv.addWidget(self.log_chat, 1)

        self.stage0_widget = self._build_stage0_widget()
        self.summary_widget = self._build_summary_widget()
        self.stack = QStackedWidget()
        self.stack.addWidget(self.stage0_widget)
        self.stack.addWidget(self.summary_widget)
        self.stack.addWidget(central)
        self.setCentralWidget(self.stack)
        self.setMinimumHeight(660)

        self._update_nav()

    # ------------------------------------------------- 环节1 · 子环角色指派
    def _ai_app_names(self):
        try:
            from players import load_players
            return [p.get("名字") for p in load_players() if p.get("名字")]
        except Exception:
            return []

    def _build_stage1_assign(self):
        """环节1（规划）页面：7 个子环 + _审核者 + _调整者，每个一行三下拉。
        值从 rules/assignments.json 读，改动即时写回。"""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)

        title = QLabel("环节1 · 规划 — 子环角色指派")
        title.setStyleSheet("font-size:15px; font-weight:bold; color:#00e5ff;")
        v.addWidget(title)
        hint = QLabel("每个子环指派 执行者 / 审核者 / 调整者；改动自动写回 rules/assignments.json。")
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#aaaaaa; font-size:11px;")
        v.addWidget(hint)

        # 表头
        hdr = QHBoxLayout()
        hdr.setSpacing(6)
        for txt, wd in (("子环 / 角色组", 150), ("执行者", 120), ("审核者", 120), ("调整者", 120)):
            h = QLabel(txt)
            h.setFixedWidth(wd)
            h.setStyleSheet("color:#888; font-size:11px;")
            hdr.addWidget(h)
        v.addLayout(hdr)

        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception:
            data = {}
        stage = data.get("环节", {}).get("01_规划", {})
        sub_rings = list(stage.get("子环", [])) + ["_审核者", "_调整者"]
        detail = stage.get("明细", {})
        exec_def = stage.get("执行", "")
        audit_def = stage.get("审核", "")
        adj_def = stage.get("调整", "")
        app_names = self._ai_app_names()

        for name in sub_rings:
            d = detail.get(name, {}) or {}
            ev = d.get("执行") or exec_def
            av = d.get("审核") or audit_def
            tv = d.get("调整") or adj_def
            row = QHBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(name)
            lbl.setFixedWidth(150)
            lbl.setStyleSheet("color:#ccc; font-size:12px;")
            row.addWidget(lbl)
            for val, role in ((ev, "执行"), (av, "审核"), (tv, "调整")):
                cb = QComboBox()
                opts = [""] + app_names
                if val and val not in opts:
                    opts = ["", val] + app_names
                cb.addItems(opts)
                cb.setCurrentText(val or "")
                cb.setFixedWidth(120)
                cb.setProperty("sub", name)
                cb.setProperty("role", role)
                cb.currentTextChanged.connect(self._on_stage1_assign_changed)
                row.addWidget(cb)
            v.addLayout(row)

        # 运行控制
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        run_btn = QPushButton("▶ 开始运行")
        run_btn.setMinimumHeight(30)
        run_btn.setStyleSheet("background:#1e88e5; color:#fff; font-weight:bold; border-radius:4px;")
        run_btn.clicked.connect(self._stage1_run)
        rel_btn = QPushButton("⏸ 放行")
        rel_btn.setMinimumHeight(30)
        rel_btn.setStyleSheet("background:#43a047; color:#fff; font-weight:bold; border-radius:4px;")
        rel_btn.clicked.connect(self._stage1_release)
        btn_row.addWidget(run_btn)
        btn_row.addWidget(rel_btn)
        btn_row.addStretch(1)
        v.addLayout(btn_row)

        v.addStretch(1)
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setStyleSheet("QScrollArea{border:none;}")
        sc.setWidget(w)
        return sc

    def _on_stage1_assign_changed(self, text):
        cb = self.sender()
        if not cb:
            return
        name = cb.property("sub")
        role = cb.property("role")
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception as e:
            self.log_line(f"⚠ 读取 assignments.json 失败：{e}")
            return
        stage = data.setdefault("环节", {}).setdefault("01_规划", {})
        detail = stage.setdefault("明细", {})
        d = detail.setdefault(name, {})
        d[role] = text
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log_line(f"💾 已保存指派：{name} / {role} = {text or '（空）'}")
        except Exception as e:
            self.log_line(f"❌ 写回 assignments.json 失败：{e}")

    def _build_stage0_widget(self):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 4, 0, 4)
        v.setSpacing(3)

        title = QLabel("环节 0 · 项目初始化")
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#00e5ff;")
        v.addWidget(title)

        hint = QLabel("请先填写项目基础信息，确认后进入协同写作流程。")
        hint.setWordWrap(True)
        v.addWidget(hint)

        tabs = QTabWidget()

        # ---- 基础信息 ----
        bscroll = QScrollArea()
        bscroll.setWidgetResizable(True)
        bscroll.setHorizontalScrollBarPolicy(_Qt.ScrollBarAlwaysOff)
        bscroll.setVerticalScrollBarPolicy(_Qt.ScrollBarAlwaysOff)
        bscroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        form_w = QWidget()
        form = QVBoxLayout(form_w)
        form.setContentsMargins(0, 2, 0, 2)
        form.setSpacing(2)

        self.init_name = self._stage0_line("项目名称", "请输入项目名称")
        form.addWidget(self.init_name)

        self.init_channel = self._stage0_combo("频道", ["男频", "女频"])
        form.addWidget(self.init_channel)

        self.init_genre = self._stage0_combo("题材", list(self.GENRE_SUBS.keys()))
        self.init_genre.findChild(QComboBox).currentTextChanged.connect(self._on_genre_changed)
        form.addWidget(self.init_genre)

        self.init_sub = self._stage0_combo("细分", self.GENRE_SUBS.get(self.init_genre.findChild(QComboBox).currentText(), []))
        form.addWidget(self.init_sub)

        chapters_row = self._stage0_spin("章节数", 1, 99999, 100)
        self.init_chapters = chapters_row.findChild(QSpinBox)
        form.addWidget(chapters_row)

        self.init_gender = self._stage0_combo("主角性别", ["男主", "女主", "双主角"])
        form.addWidget(self.init_gender)

        support_row = self._stage0_spin("配角数量", 0, 100, 3)
        self.init_support = support_row.findChild(QSpinBox)
        form.addWidget(support_row)

        templates_row = QHBoxLayout()
        templates_row.setSpacing(6)
        templates_row.setContentsMargins(0, 0, 0, 0)
        templates_label = QLabel("角色模板")
        templates_label.setStyleSheet("color:#aaaaaa;")
        templates_label.setFixedWidth(64)
        templates_row.addWidget(templates_label)
        self.init_templates = self._make_toggle_grid(self.CHAR_TEMPLATES, 2)
        self.init_templates.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.init_templates.setMaximumWidth(220)
        templates_row.addWidget(self.init_templates, 1)
        templates_row.addStretch(1)
        form.addLayout(templates_row)

        core_box = QGroupBox("故事核心")
        core_v = QVBoxLayout(core_box)
        core_v.setSpacing(2)
        core_v.setContentsMargins(2, 4, 2, 4)

        self.init_tone = self._make_radio_group(self.STORY_TONES, "tone", cols=3)
        core_v.addLayout(self._labeled_wrap("基调", self.init_tone))

        self.init_atmo = self._make_radio_group(self.STORY_ATMOS, "atmo", cols=3)
        core_v.addLayout(self._labeled_wrap("氛围", self.init_atmo))

        self.init_pace = self._make_radio_group(self.STORY_PACES, "pace", cols=3)
        core_v.addLayout(self._labeled_wrap("节奏", self.init_pace))

        form.addWidget(core_box)

        desc_row = QHBoxLayout()
        desc_row.setSpacing(6)
        desc_row.setContentsMargins(0, 0, 0, 0)
        desc_label = QLabel("额外想法")
        desc_label.setStyleSheet("color:#aaaaaa;")
        desc_label.setFixedWidth(64)
        desc_row.addWidget(desc_label)
        self.init_desc = QTextEdit()
        self.init_desc.setPlaceholderText("项目简介、世界观、风格要求、额外想法等…")
        self.init_desc.setMinimumHeight(32)
        self.init_desc.setMaximumHeight(36)
        self.init_desc.setMaximumWidth(220)
        self.init_desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        desc_row.addWidget(self.init_desc, 1)
        form.addLayout(desc_row)

        bscroll.setWidget(form_w)
        tabs.addTab(bscroll, "基础信息")

        # ---- 性格 / 感情线 / 金手指：子页标签，按钮多选 ----
        self.init_personality = self._make_toggle_grid(self.PERSONALITY_TRAITS, 3)
        tabs.addTab(self._wrap_scroll(self.init_personality), "性格")

        self.init_emotion = self._make_toggle_grid(self.EMOTION_TAGS, 3)
        tabs.addTab(self._wrap_scroll(self.init_emotion), "感情线")

        self.init_golden = self._make_toggle_grid(self.GOLDEN_FINGER_TAGS, 3)
        tabs.addTab(self._wrap_scroll(self.init_golden), "金手指")

        v.addWidget(tabs, 1)

        # 上传 / 随机生成 并排放
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.setContentsMargins(0, 0, 0, 0)
        upload_btn = QPushButton("📄 上传参考大纲")
        upload_btn.setMinimumHeight(24)
        upload_btn.setStyleSheet("""
                QPushButton{
                    padding:4px 12px;
                    font-size:13px;
                    color:#cfcfcf;
                    border:1px solid #3a3a3a;
                    border-radius:4px;
                    background-color:#1e1e1e;
                }
                QPushButton:hover{border-color:#5a5a5a;}
                QPushButton:pressed{border-color:#1a73e8; color:#fff;}
            """)
        upload_btn.clicked.connect(self._on_upload_outline)
        btn_row.addWidget(upload_btn)
        random_btn = QPushButton("🎲 随机生成")
        random_btn.setMinimumHeight(24)
        random_btn.setToolTip("随机填充项目设定并直接进入梗概确认")
        random_btn.setStyleSheet("""
                QPushButton{
                    padding:4px 12px;
                    font-size:13px;
                    color:#fff;
                    border:1px solid #5a5a5a;
                    border-radius:4px;
                    background-color:#2d5a27;
                }
                QPushButton:hover{background-color:#3a7a32;}
                QPushButton:pressed{background-color:#1e3e1a;}
            """)
        random_btn.clicked.connect(self._on_random_generate)
        btn_row.addWidget(random_btn)
        btn_row.addStretch(1)
        v.addLayout(btn_row)

        self.outline_label = QLabel("")
        self.outline_label.setStyleSheet("color:#888;font-size:11px;")
        self.outline_label.setWordWrap(True)
        v.addWidget(self.outline_label)

        btn = QPushButton("开始规划")
        btn.setMinimumHeight(28)
        btn.setMinimumWidth(120)
        btn.setStyleSheet("""
            QPushButton{
                padding:6px 16px;
                font-size:14px;
                font-weight:bold;
                color:#fff;
                background-color:#1a73e8;
                border-radius:5px;
            }
            QPushButton:hover{background-color:#2b7de9;}
            QPushButton:pressed{background-color:#1557b0;}
        """)
        btn.clicked.connect(self._on_stage0_confirm)
        v.addWidget(btn, 0, _Qt.AlignCenter)

        # 规划结果展示区（步骤6 动态填充，默认隐藏）
        self.stage0_result = QWidget()
        self.stage0_result.setVisible(False)
        _rl = QVBoxLayout(self.stage0_result)
        _rl.setContentsMargins(0, 10, 0, 0)
        _rl.setSpacing(8)
        v.addWidget(self.stage0_result)

        # ---- 脏标记：已手动输入/选择的字段不会被随机生成覆盖 ----
        self._name_dirty = False
        self._channel_dirty = False
        self._genre_dirty = False
        self._sub_dirty = False
        self._chapters_dirty = False
        self._gender_dirty = False
        self._support_dirty = False
        self._templates_dirty = False
        self._tone_dirty = False
        self._atmo_dirty = False
        self._pace_dirty = False
        self._personality_dirty = False
        self._emotion_dirty = False
        self._golden_dirty = False
        self._desc_dirty = False

        self.init_name.findChild(QLineEdit).textChanged.connect(lambda: setattr(self, '_name_dirty', True))
        self.init_channel.findChild(QComboBox).currentTextChanged.connect(lambda: setattr(self, '_channel_dirty', True))
        self.init_genre.findChild(QComboBox).currentTextChanged.connect(lambda: setattr(self, '_genre_dirty', True))
        self.init_sub.findChild(QComboBox).currentTextChanged.connect(lambda: setattr(self, '_sub_dirty', True))
        self.init_chapters.valueChanged.connect(lambda: setattr(self, '_chapters_dirty', True))
        self.init_gender.findChild(QComboBox).currentTextChanged.connect(lambda: setattr(self, '_gender_dirty', True))
        self.init_support.valueChanged.connect(lambda: setattr(self, '_support_dirty', True))
        self.init_desc.textChanged.connect(lambda: setattr(self, '_desc_dirty', True))
        for b in self.init_templates.findChildren(QPushButton):
            b.toggled.connect(lambda _=None: setattr(self, '_templates_dirty', True))
        for b in self.init_personality.findChildren(QPushButton):
            b.toggled.connect(lambda _=None: setattr(self, '_personality_dirty', True))
        for b in self.init_emotion.findChildren(QPushButton):
            b.toggled.connect(lambda _=None: setattr(self, '_emotion_dirty', True))
        for b in self.init_golden.findChildren(QPushButton):
            b.toggled.connect(lambda _=None: setattr(self, '_golden_dirty', True))
        for group_name, flag in (("tone", "_tone_dirty"), ("atmo", "_atmo_dirty"), ("pace", "_pace_dirty")):
            group = getattr(self, f"init_{group_name}").button_group
            for rb in group.buttons():
                rb.toggled.connect(lambda _=None, f=flag: setattr(self, f, True))

        return self._wrap_scroll(w)

    def _wrap_scroll(self, widget):
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setHorizontalScrollBarPolicy(_Qt.ScrollBarAlwaysOff)
        sc.setStyleSheet("QScrollArea{border:none;}")
        sc.setWidget(widget)
        return sc

    def _on_genre_changed(self, genre):
        self.init_sub.findChild(QComboBox).clear()
        self.init_sub.findChild(QComboBox).addItems(self.GENRE_SUBS.get(genre, []))

    def _stage0_field(self, label_text):
        box = QWidget()
        h = QHBoxLayout(box)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color:#aaaaaa;")
        lbl.setFixedWidth(80)
        h.addWidget(lbl)
        return box

    def _stage0_line(self, label_text, placeholder):
        box = self._stage0_field(label_text)
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        edit.setMaximumWidth(220)
        box.layout().addWidget(edit, 1)
        return box

    def _stage0_combo(self, label_text, items):
        box = self._stage0_field(label_text)
        cb = QComboBox()
        cb.addItems(items)
        cb.setMaximumWidth(220)
        cb.setMinimumWidth(90)
        cb.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # 下拉列表不宽过控件本身
        cb.view().setMaximumWidth(220)
        box.layout().addWidget(cb)
        box.layout().addStretch(1)
        return box

    def _stage0_spin(self, label_text, min_v, max_v, val):
        box = self._stage0_field(label_text)
        sp = QSpinBox()
        sp.setRange(min_v, max_v)
        sp.setValue(val)
        sp.setMaximumWidth(220)
        sp.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        box.layout().addWidget(sp)
        box.layout().addStretch(1)
        return box

    def _make_toggle_grid(self, items, cols):
        w = QWidget()
        grid = QGridLayout(w)
        grid.setContentsMargins(1, 1, 1, 1)
        grid.setSpacing(4)
        for c in range(cols):
            grid.setColumnStretch(c, 1)
        for i, text in enumerate(items):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setStyleSheet("""
                QPushButton{
                    padding:4px 4px;
                    font-size:12px;
                    color:#cfcfcf;
                    border:1px solid #3a3a3a;
                    border-radius:4px;
                    background-color:#1e1e1e;
                }
                QPushButton:checked{
                    color:#ffffff;
                    background-color:#1a73e8;
                    border-color:#1a73e8;
                }
                QPushButton:hover{ border-color:#5a5a5a; }
            """)
            grid.addWidget(btn, i // cols, i % cols)
        return w

    def _collect_toggle_texts(self, widget):
        return [b.text() for b in widget.findChildren(QPushButton) if b.isChecked()]

    def _make_radio_group(self, items, group_name, cols=3):
        group = QButtonGroup(self)
        group.setObjectName(group_name)
        w = QWidget()
        grid = QGridLayout(w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(2)
        grid.setVerticalSpacing(2)
        for c in range(cols):
            grid.setColumnStretch(c, 1)
        for i, text in enumerate(items):
            rb = QRadioButton(text)
            rb.setStyleSheet("QRadioButton{color:#ccc; spacing:2px; padding:1px 0px;} QRadioButton::indicator{width:12px;height:12px;}")
            rb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            group.addButton(rb)
            grid.addWidget(rb, i // cols, i % cols)
        if group.buttons():
            group.buttons()[0].setChecked(True)
        w.button_group = group
        return w

    def _selected_radio_text(self, widget):
        group = getattr(widget, "button_group", None)
        if not group:
            return ""
        btn = group.checkedButton()
        return btn.text() if btn else ""

    def _labeled_hbox(self, label, widget):
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)
        h.addWidget(QLabel(label))
        h.addWidget(widget, 1)
        return h

    def _labeled_wrap(self, label, widget):
        v = QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet("color:#aaaaaa;")
        v.addWidget(lbl)
        v.addWidget(widget)
        return v

    # ------------------------------------------------- 环节0 开始规划（步骤1-6）
    # 所有产出/提示词路径均由 paths 模块按程序位置推导，不再写死绝对路径
    @staticmethod
    def _safe_name(name):
        """把项目名变成安全的文件夹名（去除 Windows 非法字符、压缩空白）。"""
        import re
        s = (name or "").strip()
        s = re.sub(r'[\\/:*?"<>|]', "_", s)
        s = re.sub(r"\s+", "_", s)
        if not s:
            s = "未命名项目"
        return s[:60]

    # 产出目录下的项目文件树：步骤0=初始化目录，其后依次对应每个环节（步骤）名称。
    # 每个环节目录里再由 auto_stage 直接落该环节的块产物；本步骤规划/下一步建议也在此目录。
    TREE = [
        "00_初始化",
        "01_规划",
        "02_写作",
        "03_去AI",
        "04_审核",
        "05_出厂",
        "_logs",
    ]

    def _normalize_init_info(self, info):
        """把中文键的 UI 数据转换为梗概页 / CDP 发送所需的英文键结构。"""
        sc = info.get("故事核心") or {}
        return {
            "name": info.get("项目名称") or "未命名项目",
            "channel": info.get("频道", ""),
            "genre": info.get("题材", ""),
            "sub_genre": info.get("细分", ""),
            "chapters": info.get("章节数", 0),
            "protagonist": {
                "gender": info.get("主角性别", ""),
                "personality": info.get("主角性格") or [],
            },
            "supporting_roles": {
                "count": info.get("配角数量", 0),
                "templates": info.get("角色模板") or [],
            },
            "story_core": {
                "tone": sc.get("基调", ""),
                "atmosphere": sc.get("氛围", ""),
                "pace": sc.get("节奏", ""),
            },
            "emotion_line": info.get("感情线") or [],
            "golden_finger": info.get("金手指") or [],
            "extra_ideas": info.get("额外想法", ""),
        }

    def _collect_init_info(self):
        """步骤1：读取 UI 所有标签控件，返回中文键字典（与 UI 标签一一对应）。"""
        return {
            "项目名称": self.init_name.findChild(QLineEdit).text().strip() or "未命名项目",
            "频道": self.init_channel.findChild(QComboBox).currentText(),
            "题材": self.init_genre.findChild(QComboBox).currentText(),
            "细分": self.init_sub.findChild(QComboBox).currentText(),
            "章节数": self.init_chapters.value(),
            "主角性别": self.init_gender.findChild(QComboBox).currentText(),
            "主角性格": self._collect_toggle_texts(self.init_personality),
            "感情线": self._collect_toggle_texts(self.init_emotion),
            "金手指": self._collect_toggle_texts(self.init_golden),
            "配角数量": self.init_support.value(),
            "角色模板": self._collect_toggle_texts(self.init_templates),
            "故事核心": {
                "基调": self._selected_radio_text(self.init_tone),
                "氛围": self._selected_radio_text(self.init_atmo),
                "节奏": self._selected_radio_text(self.init_pace),
            },
            "额外想法": self.init_desc.toPlainText().strip(),
            "参考大纲": getattr(self, "reference_outline", "") or "",
        }

    def _on_stage0_confirm(self):
        """环节0·开始规划：收集基础信息 → 进入下一级界面（环节0.5 故事梗概确认）。
        真正的 WorkBuddy 生成放在梗概确认页的「下一步 → 进入环节1」（流程0.5）。"""
        info = self._collect_init_info()
        norm = self._normalize_init_info(info)
        self._current_init_data = norm          # 梗概页 / CDP 发送共用（英文键结构）

        项目名 = info.get("项目名称") or "未命名项目"
        safe = self._safe_name(项目名)

        # 产出目录根：OUTPUT\<项目名>\（按项目名建目录，无日期）
        proj_ws = paths.output_path(safe)
        init_dir = os.path.join(proj_ws, "00_初始化")
        os.makedirs(init_dir, exist_ok=True)
        with open(os.path.join(init_dir, "项目信息.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        # 按清单建步骤文件树（已存在则跳过，不删除）
        for rel in self.TREE:
            os.makedirs(os.path.join(proj_ws, rel), exist_ok=True)
        with open(os.path.join(init_dir, "文件树清单.json"), "w", encoding="utf-8") as f:
            json.dump(self.TREE, f, ensure_ascii=False, indent=2)

        # 记录本项目根目录（产出目录下的项目目录），供后续流程使用
        self._proj_ws = proj_ws
        self._proj_name = safe
        self.set_project_name(safe)

        # 建立『按项目』工作区：生成协作蓝图（规划文件树）+ 拷贝提示词 + 预指派本地AI
        try:
            paths.set_active_project_workspace(paths.workspace_project_path(safe))
            self._generate_project_plan(safe, info, norm)
        except Exception as e:
            self.log_line(f"⚠ 生成工作区/协作蓝图失败：{e}")

        # 同步章节数给自动执行引擎（逐章循环用）
        try:
            import auto_stage as _as
            _as.set_chapter_count(info.get("章节数") or 1)
            _as.set_current_chapter(1)
            _as.set_project_workspace(proj_ws)
            _as.save_chapter_progress()
            total = _as.get_chapter_total()
            self.log_line(f"📚 计划章节数：{total} 章（章为核心循环，从「写作」环节开始；当前第 001 章）")
        except Exception as e:
            self.log_line(f"⚠ 同步章节数失败：{e}")

        # 新项目：重置环节运行状态（保留 AI 指派），避免旧项目残留导致全部显示通过
        try:
            import stage_board as _sb
            current_state, _ = _sb.load()
            _sb.save(current_state, _sb.new_run_state())
            self._refresh_all_panels()
            self.log_line("🔄 已重置环节运行状态，新项目从头开始")
        except Exception as e:
            self.log_line(f"⚠ 重置环节运行状态失败：{e}")

        # 进入下一级界面：环节0.5 故事梗概确认（不直接调 WorkBuddy）
        summary_text = self._generate_summary(norm, self.reference_outline)
        self.summary_edit.setPlainText(summary_text)
        # 第0步梗概文件：把步骤0（初始化）的梗概内容另存为文件放入初始化文件夹
        try:
            init_dir = os.path.join(proj_ws, "00_初始化")
            os.makedirs(init_dir, exist_ok=True)
            with open(os.path.join(init_dir, "第0步梗概.md"), "w", encoding="utf-8") as f:
                f.write("# 第0步 · 故事梗概\n\n")
                f.write(summary_text + "\n")
            self.log_line("📄 已保存第0步梗概文件：00_初始化/第0步梗概.md")
        except Exception as e:
            self.log_line(f"⚠ 保存第0步梗概文件失败：{e}")
        try:
            self.summary_chat.clear()
        except Exception:
            pass
        self.log_line("✅ 已进入「故事梗概确认」页：确认/调整后点「下一步 → 进入环节1」")
        self.stack.setCurrentIndex(1)

    # ---------------------------------------------------------------- 工作区 / 协作蓝图
    def _generate_project_plan(self, safe, info, norm):
        """初始化增强：建『按项目』工作区，生成协作蓝图（规划文件树），拷贝提示词，预指派本地AI。

        产出目录（output/<项目名>/）保持不变；规划与提示词落在独立的工作区
        （workspace/<项目名>/），二者分开放，便于按项目回溯。
        """
        import stage_board as _sb
        import auto_stage as _as

        ws_root = paths.workspace_project_path(safe)
        plan_dir = os.path.join(ws_root, "规划")
        prompt_dir = os.path.join(ws_root, "提示词")
        os.makedirs(plan_dir, exist_ok=True)
        os.makedirs(prompt_dir, exist_ok=True)

        # 1) 拷贝提示词到工作区（仅首次，目录已有内容则跳过）
        try:
            if not any(os.scandir(prompt_dir)):
                shutil.copytree(paths.PROMPTS_DIR, prompt_dir, dirs_exist_ok=True)
                self.log_line("📂 已拷贝提示词到工作区：workspace/%s/提示词/" % safe)
        except Exception as e:
            self.log_line("⚠ 拷贝提示词失败：%s" % e)

        # 2) 预指派 AI（本地优先，无本地则回退『已选 AI 池』）
        local = _sb.local_ais()
        pool = local or _sb.available_ais() or ["（未配置AI）"]
        state, rstate = _sb.load()
        idx = 0
        for st in _sb.PIPELINE:
            sk = st["key"]
            for step in st["steps"]:
                sn = step["name"]
                sstep = state.setdefault(sk, {}).setdefault("steps", {}).setdefault(sn, {})
                sstep.setdefault("blocks", {})
                for b in (step.get("blocks") or []):
                    sstep["blocks"][b] = pool[idx % len(pool)]
                    idx += 1
                if step.get("final"):
                    sstep["reviewer"] = pool[idx % len(pool)]
                    idx += 1
                else:
                    sstep["reviewer"] = pool[idx % len(pool)]
                    idx += 1
                    sstep["adjuster"] = pool[idx % len(pool)]
                    idx += 1
        _sb.save(state, rstate)
        if local:
            self.log_line("🤖 已按本地AI预指派：%s" % "、".join(pool))
        else:
            self.log_line("⚠ 未检测到本地(非web)AI，已回退到已选AI池预指派：%s" % "、".join(pool))

        # 3) 生成规划文件树（总览 + 每子步一个文件）
        chapter_aware = _as.CHAPTER_AWARE_STAGES
        order = _sb.STAGE_ORDER

        # 总览
        ov = ["# 协作蓝图 · 总览", "", "项目：%s" % safe,
              "产出目录（交付物）：output/%s/" % safe,
              "工作区（规划+提示词）：workspace/%s/" % safe, "",
              "## 环节顺序（大环节 → 子步）", ""]
        for i, st in enumerate(_sb.PIPELINE, 1):
            steps = "、".join(s["name"] for s in st["steps"])
            ov.append("%d. 【%s】%s" % (i, st["key"], st.get("desc", "")))
            ov.append("   - 子步：%s" % steps)
        ov.append("")
        ov.append("## 默认预指派 AI 池")
        ov.append("、".join(pool) + ("（本地优先；当前无本地AI，已回退已选池）" if not local else "（本地优先）"))
        ov.append("")
        ov.append("> 每个子步的『任务说明 / 输入资料 / 产出要求 / 指派AI』见同目录 规划_<环节>_<子步>.md；")
        ov.append("> 用户可在指派面板随时修改 AI 指派。")
        with open(os.path.join(plan_dir, "00_总览.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(ov) + "\n")

        # 每子步规划
        for st in _sb.PIPELINE:
            sk = st["key"]
            for step in st["steps"]:
                sn = step["name"]
                content = self._build_step_plan(sk, sn, step, st.get("desc", ""),
                                               sk in chapter_aware, norm)
                with open(os.path.join(plan_dir, "规划_%s_%s.md" % (sk, sn)), "w", encoding="utf-8") as f:
                    f.write(content + "\n")
        self.log_line("📄 已生成协作蓝图：workspace/%s/规划/（总览 + 每子步规划）" % safe)

    def _build_step_plan(self, sk, sn, step, stage_desc, chapter_aware, norm):
        """构造单个子步的规划文件内容（四块：任务说明 / 输入资料 / 产出要求 / 指派AI）。"""
        import stage_board as _sb
        import auto_stage as _as
        L = []
        L.append("# 规划 · %s / %s" % (sk, sn))
        L.append("")
        L.append("## 一、任务说明")
        L.append(stage_desc or "（见总览）")
        if step.get("final"):
            L.append("（终审子步：仅送审核者做最终审核，不调整、不新增执行块。）")
        if chapter_aware:
            L.append("（本章为核心循环：每章先读上一章再生成，产出文件名带章号。）")
        L.append("")

        # 二、输入资料
        L.append("## 二、输入资料（运行前读取的文件）")
        order = _sb.STAGE_ORDER
        pos = order.index(sk)
        if pos == 0:
            L.append("- `00_初始化/故事梗概.md`（步骤0 生成的梗概）")
            L.append("- `00_初始化/项目信息.json`（项目基础设定）")
        else:
            for prev in order[:pos]:
                L.append("- 上游环节【%s】产出目录：`%02d_%s/`（含已通过子项产物）"
                         % (prev, order.index(prev) + 1, prev))
            if sk == "写作":
                L.append("- `00_初始化/故事梗概.md`、`00_初始化/项目信息.json`")
            if chapter_aware:
                L.append("- 上一章定稿：`%02d_%s/第{章-1}章_*.md`" % (order.index(sk) + 1, sk))
        L.append("")

        # 三、产出要求
        L.append("## 三、产出要求（完成后按文件是否就位严格校验）")
        items = _as._step_items_of(sk, step)

        def _bname(it):
            ch = 1 if chapter_aware else None
            if it == "reviewer":
                p = _as._review_path(sk, sn, ch)
            elif it == "adjuster":
                p = _as._adjust_path(sk, sn, ch)
            else:
                p = _as._produce_path(sk, sn, it, ch)
            b = os.path.basename(p)
            if chapter_aware:
                b = b.replace("第001章_", "第{N}章_")
            return b

        for it in items:
            b = _bname(it)
            if it == "reviewer":
                L.append("- 审核意见：`%s`（以审核状态为准，不强制落盘文件）" % b)
            elif it == "adjuster":
                L.append("- 调整稿：`%s`" % b)
            else:
                L.append("- 执行产出：`%s`" % b)
        if chapter_aware:
            L.append("（章意识环节文件名前缀 `第{N}章_`，N 为当前章号）")
        L.append("")

        # 四、指派AI
        L.append("## 四、指派AI（默认预选，可在指派面板修改）")
        state, _ = _sb.load()
        sstep = (state.get(sk, {}).get("steps", {}) or {}).get(sn, {}) or {}
        for it in items:
            if it == "reviewer":
                L.append("- 审核者：%s" % (sstep.get("reviewer") or "（未指派）"))
            elif it == "adjuster":
                L.append("- 调整者：%s" % (sstep.get("adjuster") or "（未指派）"))
            else:
                L.append("- 执行块【%s】：%s" % (it, (sstep.get("blocks") or {}).get(it) or "（未指派）"))
        L.append("")
        return "\n".join(L)

    def _open_plan_file(self, sk, sn):
        """打开某子步的规划文件（协作蓝图）；不存在则提示（老项目无规划属正常）。"""
        import subprocess
        safe = getattr(self, "_proj_name", None) or "未命名项目"
        p = paths.workspace_project_path(safe, "规划", "规划_%s_%s.md" % (sk, sn))
        if not os.path.exists(p):
            self.log_line("⚠ 规划文件不存在：%s（请先确认本项目已初始化生成规划；老项目无规划属正常）" % p)
            return
        try:
            os.startfile(p)
        except Exception:
            try:
                subprocess.Popen(["notepad", p])
            except Exception as e:
                self.log_line("⚠ 无法打开规划文件：%s" % e)

    def _deliver(self, src_root, block_key, log_fn=None):
        """AI 已直接把产物写到产出目录的项目步骤树里；此处仅核对关键交付物是否就位。"""
        log_fn = log_fn or self.log_line
        out_dir = paths.output_path(getattr(self, "_proj_name", "未命名项目"))
        try:
            with open(os.path.join(paths.RULES_DIR, "deliverables.json"), encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception as e:
            log_fn(f"⚠ 读取 deliverables.json 失败：{e}")
            return
        for entry in (data.get(block_key) or []):
            dst_rel = (entry.get("产出区") or "").strip()
            if not dst_rel:
                continue
            dst = os.path.join(out_dir, *dst_rel.split("/"))
            if os.path.exists(dst) and os.path.getsize(dst) >= 1:
                log_fn(f"📦 产出已就位：{dst_rel}")
            else:
                log_fn(f"⚠ 产出缺失（AI 未生成）：{dst_rel}")

    def _deliver_00(self):
        """步骤6：按 deliverables.json 的 00_初始化 块交付。"""
        init_dir = os.path.join(getattr(self, "_proj_ws", paths.WORKSPACE), "00_初始化")
        self._deliver(init_dir, "00_初始化")

    # ------------------------------------------------- 环节1 运行 / 放行
    def _stage1_run(self):
        proj_ws = getattr(self, "_proj_ws", None)
        proj_name = getattr(self, "_proj_name", "")
        if not proj_ws or not os.path.isdir(proj_ws):
            self.log_line("⚠ 尚未完成环节0（无工作区），请先开始规划")
            return
        # 读 rules/assignments.json 的"环节1"块（01_规划）
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                ad = json.load(f) or {}
            blk = ad.get("环节", {}).get("01_规划", {})
            self.log_line(f"环节1 角色：执行={blk.get('执行')} 审核={blk.get('审核')} 调整={blk.get('调整')}")
        except Exception as e:
            self.log_line(f"⚠ 读取 assignments 失败：{e}")
        # 后台运行
        if getattr(self, "_phase_worker", None) and self._phase_worker.isRunning():
            self.log_line("⚠ 上一轮环节1 仍在运行")
            return
        self._phase_worker = _PhaseRunWorker(
            "01_规划", proj_ws, proj_name, self._finalize_phase1)
        self._phase_worker.progress.connect(self.log_line)
        self._phase_worker.done.connect(self._on_phase1_done)
        self._phase_worker.start()
        self.log_line("⏳ 环节1 运行中（后台调用 WorkBuddy，逐子环输出）…")

    def _finalize_phase1(self, phase_dir, subs, finals, log_fn=print):
        """环节1 收尾：八方向审核 → 调整 → 汇总 章纲_锁定版.md → 交付产出区。"""
        log_fn("== 环节1 收尾：八方向审核 → 调整 → 章纲_锁定版 ==")
        parts = []
        for sub, fp in finals:
            if fp and os.path.exists(fp):
                try:
                    parts.append(f"# {sub}\n" + open(fp, encoding="utf-8").read())
                except Exception:
                    pass
        draft = "\n\n".join(parts)
        if not draft.strip():
            log_fn("⚠ 没有可用的子环产出，无法汇总 章纲_锁定版")
            return
        # 八方向审核（_审核者 → review.md）
        review_text = generate(phase_dir, "_审核者", draft, "审核",
                               out_name="_审核者/review.md", log_fn=log_fn)
        # 调整（_调整者 → adjusted.md）
        base = draft
        if review_text:
            base = draft + "\n\n## 评审意见\n" + review_text
        adj_text = generate(phase_dir, "_调整者", base, "调整",
                            out_name="_调整者/adjusted.md", log_fn=log_fn)
        locked = (adj_text or review_text or draft)
        locked_path = os.path.join(phase_dir, "章纲_锁定版.md")
        with open(locked_path, "w", encoding="utf-8") as f:
            f.write(locked + "\n")
        log_fn(f"✔ 章纲_锁定版.md 已汇总：{locked_path}")
        # 交付产出区（deliverables.json 01_规划 块）
        self._deliver(phase_dir, "01_规划", log_fn)

    def _on_phase1_done(self, ok, msg):
        if ok:
            self.log_line("✅ 环节1 运行完成：章纲_锁定版.md 已生成并交付产出区")
            self.log_line("⏸ 请在核对后点击【放行】按钮（放行.json confirmed=true）")
        else:
            self.log_line(f"❌ 环节1 运行失败：{msg}")

    def _stage1_release(self):
        proj_ws = getattr(self, "_proj_ws", None)
        if not proj_ws:
            self.log_line("⚠ 尚无工作区，无法放行")
            return
        rel_path = os.path.join(proj_ws, "01_规划", "放行.json")
        try:
            data = {}
            if os.path.exists(rel_path):
                with open(rel_path, encoding="utf-8") as f:
                    data = json.load(f) or {}
            data["confirmed"] = True
            data["by"] = "human"
            data["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(rel_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log_line(f"✅ 已放行环节1（confirmed=true）：{rel_path}")
        except Exception as e:
            self.log_line(f"❌ 写放行.json 失败：{e}")

    # ------------------------------------------------- 环节2 · 子环角色指派 + 运行/放行
    def _build_stage2_assign(self):
        """环节2（写作）页面：2-1~2-5 子环 + 2-2 六段复合正文，每行三下拉；开始运行/放行。"""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)

        title = QLabel("环节2 · 写作 — 子环角色指派")
        title.setStyleSheet("font-size:15px; font-weight:bold; color:#00e5ff;")
        v.addWidget(title)
        hint = QLabel("2-2 为正文复合子环（始→显→通→动→成→终 六段拼接）。"
                      "改动自动写回 rules/assignments.json。")
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#aaaaaa; font-size:11px;")
        v.addWidget(hint)

        hdr = QHBoxLayout()
        hdr.setSpacing(6)
        for txt, wd in (("子环 / 角色组", 150), ("执行者", 120), ("审核者", 120), ("调整者", 120)):
            h = QLabel(txt)
            h.setFixedWidth(wd)
            h.setStyleSheet("color:#888; font-size:11px;")
            hdr.addWidget(h)
        v.addLayout(hdr)

        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception:
            data = {}
        stage = data.get("环节", {}).get("02_写作", {})
        sub_rings = list(stage.get("子环", []))
        detail = stage.get("明细", {})
        exec_def = stage.get("执行", "")
        audit_def = stage.get("审核", "")
        adj_def = stage.get("调整", "")
        app_names = self._ai_app_names()

        for name in sub_rings:
            d = detail.get(name, {}) or {}
            ev = d.get("执行") or exec_def
            av = d.get("审核") or audit_def
            tv = d.get("调整") or adj_def
            row = QHBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(name)
            lbl.setFixedWidth(150)
            lbl.setStyleSheet("color:#ccc; font-size:12px;")
            row.addWidget(lbl)
            for val, role in ((ev, "执行"), (av, "审核"), (tv, "调整")):
                cb = QComboBox()
                opts = [""] + app_names
                if val and val not in opts:
                    opts = ["", val] + app_names
                cb.addItems(opts)
                cb.setCurrentText(val or "")
                cb.setFixedWidth(120)
                cb.setProperty("sub", name)
                cb.setProperty("role", role)
                cb.currentTextChanged.connect(self._on_stage2_assign_changed)
                row.addWidget(cb)
            v.addLayout(row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        run_btn = QPushButton("▶ 开始运行")
        run_btn.setMinimumHeight(30)
        run_btn.setStyleSheet("background:#1e88e5; color:#fff; font-weight:bold; border-radius:4px;")
        run_btn.clicked.connect(self._stage2_run)
        rel_btn = QPushButton("⏸ 放行")
        rel_btn.setMinimumHeight(30)
        rel_btn.setStyleSheet("background:#43a047; color:#fff; font-weight:bold; border-radius:4px;")
        rel_btn.clicked.connect(self._stage2_release)
        btn_row.addWidget(run_btn)
        btn_row.addWidget(rel_btn)
        btn_row.addStretch(1)
        v.addLayout(btn_row)

        v.addStretch(1)
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setStyleSheet("QScrollArea{border:none;}")
        sc.setWidget(w)
        return sc

    def _on_stage2_assign_changed(self, text):
        cb = self.sender()
        if not cb:
            return
        name = cb.property("sub")
        role = cb.property("role")
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception as e:
            self.log_line(f"⚠ 读取 assignments.json 失败：{e}")
            return
        stage = data.setdefault("环节", {}).setdefault("02_写作", {})
        detail = stage.setdefault("明细", {})
        d = detail.setdefault(name, {})
        d[role] = text
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log_line(f"💾 已保存指派：{name} / {role} = {text or '（空）'}")
        except Exception as e:
            self.log_line(f"❌ 写回 assignments.json 失败：{e}")

    def _stage2_run(self):
        proj_ws = getattr(self, "_proj_ws", None)
        proj_name = getattr(self, "_proj_name", "")
        if not proj_ws or not os.path.isdir(proj_ws):
            self.log_line("⚠ 尚未完成环节0（无工作区），请先开始规划")
            return
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                ad = json.load(f) or {}
            blk = ad.get("环节", {}).get("02_写作", {})
            self.log_line(f"环节2 角色：执行={blk.get('执行')} 审核={blk.get('审核')} 调整={blk.get('调整')}")
        except Exception as e:
            self.log_line(f"⚠ 读取 assignments 失败：{e}")
        if getattr(self, "_phase_worker", None) and self._phase_worker.isRunning():
            self.log_line("⚠ 上一轮环节仍在运行")
            return
        self._phase_worker = _PhaseRunWorker(
            "02_写作", proj_ws, proj_name, self._finalize_phase2)
        self._phase_worker.progress.connect(self.log_line)
        self._phase_worker.done.connect(self._on_phase2_done)
        self._phase_worker.start()
        self.log_line("⏳ 环节2 运行中（后台调用 WorkBuddy，含 2-2 六段正文）…")

    def _finalize_phase2(self, phase_dir, subs, finals, log_fn=print):
        """环节2 收尾：把 第001章_正文.md 按 deliverables.json 交付产出区。"""
        log_fn("== 环节2 收尾：交付 第001章_正文.md 到产出区 ==")
        self._deliver(phase_dir, "02_写作", log_fn)

    def _on_phase2_done(self, ok, msg):
        if ok:
            self.log_line("✅ 环节2 运行完成：第001章_正文.md 已生成并交付产出区")
            self.log_line("⏸ 请在核对后点击【放行】按钮（放行.json confirmed=true）")
        else:
            self.log_line(f"❌ 环节2 运行失败：{msg}")

    def _stage2_release(self):
        proj_ws = getattr(self, "_proj_ws", None)
        if not proj_ws:
            self.log_line("⚠ 尚无工作区，无法放行")
            return
        rel_path = os.path.join(proj_ws, "02_写作", "放行.json")
        try:
            data = {}
            if os.path.exists(rel_path):
                with open(rel_path, encoding="utf-8") as f:
                    data = json.load(f) or {}
            data["confirmed"] = True
            data["by"] = "human"
            data["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(rel_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log_line(f"✅ 已放行环节2（confirmed=true）：{rel_path}")
        except Exception as e:
            self.log_line(f"❌ 写放行.json 失败：{e}")

    # ------------------------------------------------- 环节3 · 子环角色指派 + 运行/放行
    def _build_stage3_assign(self):
        """环节3（去AI）页面：3-1~3-5 五步链式，每行三下拉；开始运行/放行。"""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)

        title = QLabel("环节3 · 去AI — 子环角色指派")
        title.setStyleSheet("font-size:15px; font-weight:bold; color:#00e5ff;")
        v.addWidget(title)
        hint = QLabel("3-1~3-5 五步链式润色（前步 final 作后步输入）。"
                      "全部完成后跑 阶段 _审核者 + _调整者 汇总润色定稿。改动自动写回 assignments.json。")
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#aaaaaa; font-size:11px;")
        v.addWidget(hint)

        hdr = QHBoxLayout()
        hdr.setSpacing(6)
        for txt, wd in (("子环 / 角色组", 150), ("执行者", 120), ("审核者", 120), ("调整者", 120)):
            h = QLabel(txt)
            h.setFixedWidth(wd)
            h.setStyleSheet("color:#888; font-size:11px;")
            hdr.addWidget(h)
        v.addLayout(hdr)

        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception:
            data = {}
        stage = data.get("环节", {}).get("03_去AI", {})
        sub_rings = list(stage.get("子环", []))
        detail = stage.get("明细", {})
        exec_def = stage.get("执行", "")
        audit_def = stage.get("审核", "")
        adj_def = stage.get("调整", "")
        app_names = self._ai_app_names()

        for name in sub_rings:
            d = detail.get(name, {}) or {}
            ev = d.get("执行") or exec_def
            av = d.get("审核") or audit_def
            tv = d.get("调整") or adj_def
            row = QHBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(name)
            lbl.setFixedWidth(150)
            lbl.setStyleSheet("color:#ccc; font-size:12px;")
            row.addWidget(lbl)
            for val, role in ((ev, "执行"), (av, "审核"), (tv, "调整")):
                cb = QComboBox()
                opts = [""] + app_names
                if val and val not in opts:
                    opts = ["", val] + app_names
                cb.addItems(opts)
                cb.setCurrentText(val or "")
                cb.setFixedWidth(120)
                cb.setProperty("sub", name)
                cb.setProperty("role", role)
                cb.currentTextChanged.connect(self._on_stage3_assign_changed)
                row.addWidget(cb)
            v.addLayout(row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        run_btn = QPushButton("▶ 开始运行")
        run_btn.setMinimumHeight(30)
        run_btn.setStyleSheet("background:#1e88e5; color:#fff; font-weight:bold; border-radius:4px;")
        run_btn.clicked.connect(self._stage3_run)
        rel_btn = QPushButton("⏸ 放行")
        rel_btn.setMinimumHeight(30)
        rel_btn.setStyleSheet("background:#43a047; color:#fff; font-weight:bold; border-radius:4px;")
        rel_btn.clicked.connect(self._stage3_release)
        btn_row.addWidget(run_btn)
        btn_row.addWidget(rel_btn)
        btn_row.addStretch(1)
        v.addLayout(btn_row)

        v.addStretch(1)
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setStyleSheet("QScrollArea{border:none;}")
        sc.setWidget(w)
        return sc

    def _on_stage3_assign_changed(self, text):
        cb = self.sender()
        if not cb:
            return
        name = cb.property("sub")
        role = cb.property("role")
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception as e:
            self.log_line(f"⚠ 读取 assignments.json 失败：{e}")
            return
        stage = data.setdefault("环节", {}).setdefault("03_去AI", {})
        detail = stage.setdefault("明细", {})
        d = detail.setdefault(name, {})
        d[role] = text
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log_line(f"💾 已保存指派：{name} / {role} = {text or '（空）'}")
        except Exception as e:
            self.log_line(f"❌ 写回 assignments.json 失败：{e}")

    def _stage3_run(self):
        proj_ws = getattr(self, "_proj_ws", None)
        proj_name = getattr(self, "_proj_name", "")
        if not proj_ws or not os.path.isdir(proj_ws):
            self.log_line("⚠ 尚未完成环节0（无工作区），请先开始规划")
            return
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                ad = json.load(f) or {}
            blk = ad.get("环节", {}).get("03_去AI", {})
            self.log_line(f"环节3 角色：执行={blk.get('执行')} 审核={blk.get('审核')} 调整={blk.get('调整')}")
        except Exception as e:
            self.log_line(f"⚠ 读取 assignments 失败：{e}")
        if getattr(self, "_phase_worker", None) and self._phase_worker.isRunning():
            self.log_line("⚠ 上一轮环节仍在运行")
            return
        self._phase_worker = _PhaseRunWorker(
            "03_去AI", proj_ws, proj_name, self._finalize_phase3)
        self._phase_worker.progress.connect(self.log_line)
        self._phase_worker.done.connect(self._on_phase3_done)
        self._phase_worker.start()
        self.log_line("⏳ 环节3 运行中（后台调用 WorkBuddy，5 步链式润色）…")

    def _finalize_phase3(self, phase_dir, subs, finals, log_fn=print):
        """环节3 收尾：八方向审核 → 调整 → 汇总 第001章_润色定稿.md → 交付产出区。"""
        log_fn("== 环节3 收尾：去AI审核 → 调整 → 第001章_润色定稿 ==")
        parts = []
        for sub, fp in finals:
            if fp and os.path.exists(fp):
                try:
                    parts.append(f"# {sub}\n" + open(fp, encoding="utf-8").read())
                except Exception:
                    pass
        draft = "\n\n".join(parts)
        if not draft.strip():
            log_fn("⚠ 没有可用的子环产出，无法汇总 第001章_润色定稿")
            return
        review_text = generate(phase_dir, "_审核者", draft, "审核",
                               out_name="_审核者/review.md", log_fn=log_fn)
        base = draft
        if review_text:
            base = draft + "\n\n## 评审意见\n" + review_text
        adj_text = generate(phase_dir, "_调整者", base, "调整",
                            out_name="_调整者/adjusted.md", log_fn=log_fn)
        polished = (adj_text or review_text or draft)
        polished_path = os.path.join(phase_dir, "第001章_润色定稿.md")
        with open(polished_path, "w", encoding="utf-8") as f:
            f.write(polished + "\n")
        log_fn(f"✔ 第001章_润色定稿.md 已汇总：{polished_path}")
        # 交付产出区（deliverables.json 03_去AI 块）
        self._deliver(phase_dir, "03_去AI", log_fn)

    def _on_phase3_done(self, ok, msg):
        if ok:
            self.log_line("✅ 环节3 运行完成：第001章_润色定稿.md 已生成并交付产出区")
            self.log_line("⏸ 请在核对后点击【放行】按钮（放行.json confirmed=true）")
        else:
            self.log_line(f"❌ 环节3 运行失败：{msg}")

    def _stage3_release(self):
        proj_ws = getattr(self, "_proj_ws", None)
        if not proj_ws:
            self.log_line("⚠ 尚无工作区，无法放行")
            return
        rel_path = os.path.join(proj_ws, "03_去AI", "放行.json")
        try:
            data = {}
            if os.path.exists(rel_path):
                with open(rel_path, encoding="utf-8") as f:
                    data = json.load(f) or {}
            data["confirmed"] = True
            data["by"] = "human"
            data["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(rel_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log_line(f"✅ 已放行环节3（confirmed=true）：{rel_path}")
        except Exception as e:
            self.log_line(f"❌ 写放行.json 失败：{e}")

    # ------------------------------------------------- 环节4 · 子环角色指派 + 运行/放行
    def _build_stage4_assign(self):
        """环节4（审核）页面：4-1~4-5 五维质检（共享润色定稿），每行三下拉；开始运行/放行。"""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)

        title = QLabel("环节4 · 审核 — 子环角色指派")
        title.setStyleSheet("font-size:15px; font-weight:bold; color:#00e5ff;")
        v.addWidget(title)
        hint = QLabel("4-1~4-5 五维质检，输入都是 03_去AI 润色定稿。各子环产出 8 字段质检报告，"
                      "S 级问题只在报告标「返修目标=环节X」，不自动回改。改动自动写回 assignments.json。")
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#aaaaaa; font-size:11px;")
        v.addWidget(hint)

        hdr = QHBoxLayout()
        hdr.setSpacing(6)
        for txt, wd in (("子环 / 角色组", 150), ("执行者", 120), ("审核者", 120), ("调整者", 120)):
            h = QLabel(txt)
            h.setFixedWidth(wd)
            h.setStyleSheet("color:#888; font-size:11px;")
            hdr.addWidget(h)
        v.addLayout(hdr)

        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception:
            data = {}
        stage = data.get("环节", {}).get("04_审核", {})
        sub_rings = list(stage.get("子环", []))
        detail = stage.get("明细", {})
        exec_def = stage.get("执行", "")
        audit_def = stage.get("审核", "") or stage.get("审核复核", "")
        adj_def = stage.get("调整", "")
        app_names = self._ai_app_names()

        for name in sub_rings:
            d = detail.get(name, {}) or {}
            ev = d.get("执行") or exec_def
            av = d.get("审核") or audit_def
            tv = d.get("调整") or adj_def
            row = QHBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(name)
            lbl.setFixedWidth(150)
            lbl.setStyleSheet("color:#ccc; font-size:12px;")
            row.addWidget(lbl)
            for val, role in ((ev, "执行"), (av, "审核"), (tv, "调整")):
                cb = QComboBox()
                opts = [""] + app_names
                if val and val not in opts:
                    opts = ["", val] + app_names
                cb.addItems(opts)
                cb.setCurrentText(val or "")
                cb.setFixedWidth(120)
                cb.setProperty("sub", name)
                cb.setProperty("role", role)
                cb.currentTextChanged.connect(self._on_stage4_assign_changed)
                row.addWidget(cb)
            v.addLayout(row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        run_btn = QPushButton("▶ 开始运行")
        run_btn.setMinimumHeight(30)
        run_btn.setStyleSheet("background:#1e88e5; color:#fff; font-weight:bold; border-radius:4px;")
        run_btn.clicked.connect(self._stage4_run)
        rel_btn = QPushButton("⏸ 放行")
        rel_btn.setMinimumHeight(30)
        rel_btn.setStyleSheet("background:#43a047; color:#fff; font-weight:bold; border-radius:4px;")
        rel_btn.clicked.connect(self._stage4_release)
        btn_row.addWidget(run_btn)
        btn_row.addWidget(rel_btn)
        btn_row.addStretch(1)
        v.addLayout(btn_row)

        v.addStretch(1)
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setStyleSheet("QScrollArea{border:none;}")
        sc.setWidget(w)
        return sc

    def _on_stage4_assign_changed(self, text):
        cb = self.sender()
        if not cb:
            return
        name = cb.property("sub")
        role = cb.property("role")
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception as e:
            self.log_line(f"⚠ 读取 assignments.json 失败：{e}")
            return
        stage = data.setdefault("环节", {}).setdefault("04_审核", {})
        detail = stage.setdefault("明细", {})
        d = detail.setdefault(name, {})
        d[role] = text
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log_line(f"💾 已保存指派：{name} / {role} = {text or '（空）'}")
        except Exception as e:
            self.log_line(f"❌ 写回 assignments.json 失败：{e}")

    def _stage4_run(self):
        proj_ws = getattr(self, "_proj_ws", None)
        proj_name = getattr(self, "_proj_name", "")
        if not proj_ws or not os.path.isdir(proj_ws):
            self.log_line("⚠ 尚未完成环节0（无工作区），请先开始规划")
            return
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                ad = json.load(f) or {}
            blk = ad.get("环节", {}).get("04_审核", {})
            self.log_line(f"环节4 角色：执行={blk.get('执行')} 审核={blk.get('审核', blk.get('审核复核'))} 调整={blk.get('调整')}")
        except Exception as e:
            self.log_line(f"⚠ 读取 assignments 失败：{e}")
        if getattr(self, "_phase_worker", None) and self._phase_worker.isRunning():
            self.log_line("⚠ 上一轮环节仍在运行")
            return
        self._phase_worker = _PhaseRunWorker(
            "04_审核", proj_ws, proj_name, self._finalize_phase4)
        self._phase_worker.progress.connect(self.log_line)
        self._phase_worker.done.connect(self._on_phase4_done)
        self._phase_worker.start()
        self.log_line("⏳ 环节4 运行中（后台调用 WorkBuddy，5 维质检共享润色定稿）…")

    def _finalize_phase4(self, phase_dir, subs, finals, log_fn=print):
        """环节4 收尾：汇总 5 份质检报告 → 质检报告_汇总.md → 交付产出区。"""
        log_fn("== 环节4 收尾：汇总质检报告 ==")
        parts = []
        for sub, fp in finals:
            if fp and os.path.exists(fp):
                try:
                    parts.append(f"# {sub}\n" + open(fp, encoding="utf-8").read())
                except Exception:
                    pass
        if not parts:
            log_fn("⚠ 没有可用的质检报告，无法汇总")
            return
        summary = "\n\n".join(parts)
        summary_path = os.path.join(phase_dir, "质检报告_汇总.md")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary + "\n")
        log_fn(f"✔ 质检报告_汇总.md 已汇总：{summary_path}")
        # 交付产出区（deliverables.json 04_审核 块）
        self._deliver(phase_dir, "04_审核", log_fn)

    def _on_phase4_done(self, ok, msg):
        if ok:
            self.log_line("✅ 环节4 运行完成：质检报告_汇总.md 已生成并交付产出区")
            self.log_line("⏸ 请在核对后点击【放行】按钮（放行.json confirmed=true）")
        else:
            self.log_line(f"❌ 环节4 运行失败：{msg}")

    def _stage4_release(self):
        proj_ws = getattr(self, "_proj_ws", None)
        if not proj_ws:
            self.log_line("⚠ 尚无工作区，无法放行")
            return
        rel_path = os.path.join(proj_ws, "04_审核", "放行.json")
        try:
            data = {}
            if os.path.exists(rel_path):
                with open(rel_path, encoding="utf-8") as f:
                    data = json.load(f) or {}
            data["confirmed"] = True
            data["by"] = "human"
            data["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(rel_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log_line(f"✅ 已放行环节4（confirmed=true）：{rel_path}")
        except Exception as e:
            self.log_line(f"❌ 写放行.json 失败：{e}")

    # ------------------------------------------------- 环节5 · 子环角色指派 + 运行/放行
    def _build_stage5_assign(self):
        """环节5（出厂）页面：5-1~5-3 子环，每行三下拉；开始运行/放行。"""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)

        title = QLabel("环节5 · 出厂 — 子环角色指派")
        title.setStyleSheet("font-size:15px; font-weight:bold; color:#00e5ff;")
        v.addWidget(title)
        hint = QLabel("5-1 低级错误机械修正 → 5-2 名称章号统一 → 5-3 定稿打包归档。"
                      "全完成后生成 OUTPUT/<项目>/07_番茄上架包/ 并归档到工作区 _library。")
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#aaaaaa; font-size:11px;")
        v.addWidget(hint)

        hdr = QHBoxLayout()
        hdr.setSpacing(6)
        for txt, wd in (("子环 / 角色组", 150), ("执行者", 120), ("审核者", 120), ("调整者", 120)):
            h = QLabel(txt)
            h.setFixedWidth(wd)
            h.setStyleSheet("color:#888; font-size:11px;")
            hdr.addWidget(h)
        v.addLayout(hdr)

        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception:
            data = {}
        stage = data.get("环节", {}).get("05_出厂", {})
        sub_rings = list(stage.get("子环", []))
        detail = stage.get("明细", {})
        exec_def = stage.get("执行", "")
        audit_def = stage.get("审核", "")
        adj_def = stage.get("调整", "")
        app_names = self._ai_app_names()

        for name in sub_rings:
            d = detail.get(name, {}) or {}
            ev = d.get("执行") or exec_def
            av = d.get("审核") or audit_def
            tv = d.get("调整") or adj_def
            row = QHBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(name)
            lbl.setFixedWidth(150)
            lbl.setStyleSheet("color:#ccc; font-size:12px;")
            row.addWidget(lbl)
            for val, role in ((ev, "执行"), (av, "审核"), (tv, "调整")):
                cb = QComboBox()
                opts = [""] + app_names
                if val and val not in opts:
                    opts = ["", val] + app_names
                cb.addItems(opts)
                cb.setCurrentText(val or "")
                cb.setFixedWidth(120)
                cb.setProperty("sub", name)
                cb.setProperty("role", role)
                cb.currentTextChanged.connect(self._on_stage5_assign_changed)
                row.addWidget(cb)
            v.addLayout(row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        run_btn = QPushButton("▶ 开始运行")
        run_btn.setMinimumHeight(30)
        run_btn.setStyleSheet("background:#1e88e5; color:#fff; font-weight:bold; border-radius:4px;")
        run_btn.clicked.connect(self._stage5_run)
        rel_btn = QPushButton("⏸ 放行")
        rel_btn.setMinimumHeight(30)
        rel_btn.setStyleSheet("background:#43a047; color:#fff; font-weight:bold; border-radius:4px;")
        rel_btn.clicked.connect(self._stage5_release)
        btn_row.addWidget(run_btn)
        btn_row.addWidget(rel_btn)
        btn_row.addStretch(1)
        v.addLayout(btn_row)

        v.addStretch(1)
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setStyleSheet("QScrollArea{border:none;}")
        sc.setWidget(w)
        return sc

    def _on_stage5_assign_changed(self, text):
        cb = self.sender()
        if not cb:
            return
        name = cb.property("sub")
        role = cb.property("role")
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception as e:
            self.log_line(f"⚠ 读取 assignments.json 失败：{e}")
            return
        stage = data.setdefault("环节", {}).setdefault("05_出厂", {})
        detail = stage.setdefault("明细", {})
        d = detail.setdefault(name, {})
        d[role] = text
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log_line(f"💾 已保存指派：{name} / {role} = {text or '（空）'}")
        except Exception as e:
            self.log_line(f"❌ 写回 assignments.json 失败：{e}")

    def _stage5_run(self):
        proj_ws = getattr(self, "_proj_ws", None)
        proj_name = getattr(self, "_proj_name", "")
        if not proj_ws or not os.path.isdir(proj_ws):
            self.log_line("⚠ 尚未完成环节0（无工作区），请先开始规划")
            return
        try:
            with open(os.path.join(paths.RULES_DIR, "assignments.json"), encoding="utf-8") as f:
                ad = json.load(f) or {}
            blk = ad.get("环节", {}).get("05_出厂", {})
            self.log_line(f"环节5 角色：执行={blk.get('执行')} 审核={blk.get('审核')} 调整={blk.get('调整')}")
        except Exception as e:
            self.log_line(f"⚠ 读取 assignments 失败：{e}")
        if getattr(self, "_phase_worker", None) and self._phase_worker.isRunning():
            self.log_line("⚠ 上一轮环节仍在运行")
            return
        self._phase_worker = _PhaseRunWorker(
            "05_出厂", proj_ws, proj_name, self._finalize_phase5)
        self._phase_worker.progress.connect(self.log_line)
        self._phase_worker.done.connect(self._on_phase5_done)
        self._phase_worker.start()
        self.log_line("⏳ 环节5 运行中（后台调用 WorkBuddy，5-1~5-3 出厂）…")

    def _finalize_phase5(self, phase_dir, subs, finals, log_fn=print):
        """环节5 收尾：定稿打包归档。
        - 按 deliverables 05_出厂 把 5-3 定稿复制到 OUTPUT/<项目>/07_番茄上架包/07_定稿.md
        - 生成上架包辅助文件：书名/简介/标签/封面brief/里程碑核对
        - 复制定稿到 WORKSPACE/<项目>/_library/第001章.md
        """
        log_fn("== 环节5 收尾：定稿打包归档 ==")
        # 仅当 5-3 已产出定稿才打包（先只跑 5-1/5-2 时跳过）
        dinggao_path = None
        for name, fp in finals:
            if name == "5-3_定稿打包归档" and fp and os.path.exists(fp):
                dinggao_path = fp
                break
        if dinggao_path is None:
            log_fn("⚠ 5-3_定稿打包归档 尚未产出，跳过打包（先只跑 5-1/5-2 时属正常）")
            return
        try:
            dinggao = open(dinggao_path, encoding="utf-8").read()
        except Exception:
            dinggao = ""

        # 1) 主定稿按 deliverables 复制到 07_番茄上架包/07_定稿.md
        self._deliver(phase_dir, "05_出厂", log_fn)

        proj_ws = getattr(self, "_proj_ws", None) or paths.workspace_path(getattr(self, "_proj_name", ""))
        proj_name = getattr(self, "_proj_name", "未命名项目")
        out_root = paths.output_path(proj_name)
        pkg = os.path.join(out_root, "07_番茄上架包")
        os.makedirs(pkg, exist_ok=True)

        # 2) 书名/简介/标签 来自 00_初始化/项目信息.json
        info = {}
        info_path = os.path.join(proj_ws, "00_初始化", "项目信息.json")
        if os.path.exists(info_path):
            try:
                info = json.load(open(info_path, encoding="utf-8")) or {}
            except Exception:
                info = {}
        书名 = info.get("项目名称") or proj_name or "未命名项目"
        简介 = (info.get("额外想法") or "").strip()
        核心 = info.get("故事核心") or {}
        标签 = [info.get("题材"), info.get("细分"), 核心.get("基调"), 核心.get("氛围"), 核心.get("节奏")]
        标签 = [t for t in 标签 if t]
        with open(os.path.join(pkg, "书名.md"), "w", encoding="utf-8") as f:
            f.write(书名 + "\n")
        with open(os.path.join(pkg, "简介.md"), "w", encoding="utf-8") as f:
            f.write((简介 or "（无）") + "\n")
        with open(os.path.join(pkg, "标签.md"), "w", encoding="utf-8") as f:
            f.write("、".join(标签) + "\n")
        brief = (f"书名：{书名}\n频道：{info.get('频道','')}  题材：{info.get('题材','')}  细分：{info.get('细分','')}\n"
                 f"基调：{核心.get('基调','')}  氛围：{核心.get('氛围','')}  节奏：{核心.get('节奏','')}\n"
                 f"一句话简介：{简介}\n标签：{'、'.join(标签)}\n"
                 f"封面需求：竖版封面，突出「{书名}」书名与核心情绪（{核心.get('氛围','')}），"
                 f"主角剪影 + 关键场景意象，避免文字过载。")
        with open(os.path.join(pkg, "封面brief.md"), "w", encoding="utf-8") as f:
            f.write(brief + "\n")
        # 里程碑核对：章纲_锁定版 各标题是否在定稿出现
        milestone = "# 里程碑核对\n\n"
        outline_path = os.path.join(proj_ws, "01_规划", "章纲_锁定版.md")
        if os.path.exists(outline_path):
            ol = open(outline_path, encoding="utf-8").read()
            points = [ln.lstrip("#").strip() for ln in ol.splitlines() if ln.strip().startswith("#")]
            for p in points:
                kw = p[:8]
                ok = (kw in dinggao)
                milestone += f"- [{'x' if ok else ' '}] {p}\n"
        else:
            milestone += "- 未找到 01_规划/章纲_锁定版.md，无法核对里程碑\n"
        with open(os.path.join(pkg, "里程碑核对.md"), "w", encoding="utf-8") as f:
            f.write(milestone + "\n")
        log_fn(f"✔ 上架包已生成：{pkg}（书名/简介/标签/封面brief/里程碑核对）")

        # 3) 复制定稿到 WORKSPACE/<项目>/_library/第001章.md
        lib_dir = os.path.join(proj_ws, "_library")
        os.makedirs(lib_dir, exist_ok=True)
        with open(os.path.join(lib_dir, "第001章.md"), "w", encoding="utf-8") as f:
            f.write(dinggao + "\n")
        log_fn(f"✔ 定稿已归档到工作区：{os.path.join(lib_dir, '第001章.md')}")

    def _on_phase5_done(self, ok, msg):
        if ok:
            self.log_line("✅ 环节5 运行完成：定稿已打包上架包并归档工作区 _library")
            self.log_line("⏸ 请在核对后点击【放行】按钮（放行.json confirmed=true）—— 全流程到此完成")
        else:
            self.log_line(f"❌ 环节5 运行失败：{msg}")

    def _stage5_release(self):
        proj_ws = getattr(self, "_proj_ws", None)
        if not proj_ws:
            self.log_line("⚠ 尚无工作区，无法放行")
            return
        rel_path = os.path.join(proj_ws, "05_出厂", "放行.json")
        try:
            data = {}
            if os.path.exists(rel_path):
                with open(rel_path, encoding="utf-8") as f:
                    data = json.load(f) or {}
            data["confirmed"] = True
            data["by"] = "human"
            data["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(rel_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log_line(f"✅ 已放行环节5（confirmed=true）：{rel_path} —— 全流程完成")
        except Exception as e:
            self.log_line(f"❌ 写放行.json 失败：{e}")

    def _on_plan_done(self, ok, msg):
        if ok:
            # 步骤6：把工作区文件复制到产出区（改名）
            self._deliver_00()
            self.log_line("✅ 步骤0 规划产出已生成：故事梗概.md / AI建议调整方向.md")
            self._show_stage0_result(error=False)
        else:
            self.log_line(f"❌ {msg}")
            self._show_stage0_result(error=True, error_msg=msg)

    def _show_stage0_result(self, error=False, error_msg="", status_text=None):
        rl = self.stage0_result.layout()
        while rl.count():
            it = rl.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()
        if error:
            lbl = QLabel(error_msg or "生成失败")
            lbl.setStyleSheet("color:#ff6b6b;font-weight:bold;font-size:13px;")
            rl.addWidget(lbl)
        else:
            lbl = QLabel(status_text or "已生成，请打开产出文件夹查看")
            lbl.setStyleSheet("color:#7CFC00;font-weight:bold;font-size:13px;")
            rl.addWidget(lbl)
            # 调整请求输入
            req_hint = QLabel("如需调整，在下方填写调整要求后点【发送调整】：")
            req_hint.setStyleSheet("color:#aaaaaa; font-size:11px;")
            rl.addWidget(req_hint)
            self.adjust_req = QTextEdit()
            self.adjust_req.setPlaceholderText("输入你的调整要求（可空，空则按当前版本微调）…")
            self.adjust_req.setMaximumHeight(54)
            rl.addWidget(self.adjust_req)
        open_btn = QPushButton("📂 打开产出文件夹")
        open_btn.setMinimumHeight(28)
        open_btn.clicked.connect(lambda: self._open_output_folder())
        rl.addWidget(open_btn)
        if not error:
            next_btn = QPushButton("下一步 → 进入环节1")
            next_btn.setMinimumHeight(28)
            next_btn.clicked.connect(self._plan_next)
            rl.addWidget(next_btn)
            adj_btn = QPushButton("发送调整")
            adj_btn.setMinimumHeight(28)
            adj_btn.clicked.connect(self._plan_send_adjust)
            rl.addWidget(adj_btn)
        self.stage0_result.setVisible(True)
        try:
            self.stage0_widget.ensureWidgetVisible(self.stage0_result, 0, 0)
        except Exception:
            pass

    def _open_output_folder(self, path=None):
        import os
        d = path or paths.output_path(getattr(self, "_proj_name", ""))
        try:
            os.makedirs(d, exist_ok=True)
            os.startfile(d)
        except Exception as e:
            self.log_line(f"打开文件夹失败：{e}")

    def _plan_next(self):
        # 写 放行.json
        init_dir = os.path.join(getattr(self, "_proj_ws", paths.WORKSPACE), "00_初始化")
        release = {"confirmed": True, "by": "human",
                   "time": time.strftime("%Y-%m-%d %H:%M:%S")}
        try:
            os.makedirs(init_dir, exist_ok=True)
            with open(os.path.join(init_dir, "放行.json"), "w", encoding="utf-8") as f:
                json.dump(release, f, ensure_ascii=False, indent=2)
            self.log_line(f"✅ 已写入放行.json：{init_dir}")
        except Exception as e:
            self.log_line(f"❌ 写入放行.json 失败：{e}")
        # 切到环节1 页面（中央大环节第 1 个 tab）
        self.stack.setCurrentIndex(2)
        self.tabs.setCurrentIndex(0)
        self._refresh_all_panels()
        self.log_line("已进入环节1（规划·子环角色指派）")

    def _plan_send_adjust(self):
        init_dir = os.path.join(getattr(self, "_proj_ws", paths.WORKSPACE), "00_初始化")
        syn_path = os.path.join(init_dir, "故事梗概.md")
        adv_path = os.path.join(init_dir, "AI建议调整方向.md")
        if not (os.path.exists(syn_path) and os.path.exists(adv_path)):
            self.log_line("❌ 工作区两份文件不存在，无法调整（请先开始规划）")
            return
        import auto_stage as _as
        if getattr(_as, "MOCK_PROMPTS", False):
            self.log_line("📤 [mock] 连通性模拟：跳过真实调整提示词，直接写入占位文件")
            for fn in ("故事梗概.md", "AI建议调整方向.md"):
                try:
                    with open(os.path.join(init_dir, fn), "w", encoding="utf-8") as f:
                        f.write("你好")
                except Exception as e:
                    self.log_line(f"⚠ 写入占位失败：{e}")
            self._deliver_00()
            self.log_line("✅ [mock] 调整占位已写入：故事梗概.md / AI建议调整方向.md（未消耗 AI）")
            return
        old_syn = open(syn_path, encoding="utf-8").read().strip()
        old_adv = open(adv_path, encoding="utf-8").read().strip()
        info = getattr(self, "_current_init_data", {})
        proj_json = json.dumps(info, ensure_ascii=False, indent=2)
        req = (getattr(self, "adjust_req", None)
               and self.adjust_req.toPlainText().strip()) or ""

        tpl_path = paths.prompt_path("00_初始化", "梗概调整.md")
        if not os.path.exists(tpl_path):
            self.log_line(f"❌ 调整提示词模板不存在：{tpl_path}")
            return
        tpl = open(tpl_path, encoding="utf-8").read()
        prompt = (tpl.replace("{{PROJECT_JSON}}", proj_json)
                      .replace("{{OLD_SYNOPSIS}}", old_syn)
                      .replace("{{OLD_ADVICE}}", old_adv)
                      .replace("{{ADJUST_REQUEST}}", req))
        if "{{" in prompt:
            self.log_line("❌ 调整提示词模板替换后仍残留占位符，已停止")
            return

        # 后台发给 WorkBuddy，抓文本并按标记拆文件（覆盖工作区两份）
        self._adjust_worker = _PlanGenWorker(prompt, init_dir, info.get("项目名称", ""))
        self._adjust_worker.progress.connect(self.log_line)
        self._adjust_worker.done.connect(self._on_adjust_done)
        self._adjust_worker.start()
        self.log_line(f"⏳ 已发送调整请求到 WorkBuddy，正在生成…（目录：{init_dir}）")

    def _on_adjust_done(self, ok, msg):
        init_dir = os.path.join(getattr(self, "_proj_ws", paths.WORKSPACE), "00_初始化")
        if ok:
            # 覆盖产出区两份
            self._deliver_00()
            # 追加调整记录
            rec_path = os.path.join(init_dir, "调整记录.md")
            req = (getattr(self, "adjust_req", None)
                   and self.adjust_req.toPlainText().strip()) or "（无具体请求，按当前版本微调）"
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            try:
                with open(rec_path, "a", encoding="utf-8") as f:
                    f.write(f"- [{ts}] 调整请求：{req}\n")
                self.log_line(f"📝 已追加调整记录：{rec_path}")
            except Exception as e:
                self.log_line(f"⚠ 追加调整记录失败：{e}")
            self.log_line("✅ 调整产出已更新：故事梗概.md / AI建议调整方向.md")
            self._show_stage0_result(error=False, status_text="已更新，请重新打开产出文件夹查看")
        else:
            self.log_line(f"❌ {msg}")
            self._show_stage0_result(error=True, error_msg=msg)

    def set_project_name(self, name):
        """把当前项目名称显示到每个环节页顶部（环节窗口上方）。"""
        for lbl in getattr(self, "proj_name_labels", []):
            lbl.setText(f"📁 当前项目：{name}" if name else "")

    def _on_prev(self):
        """上一步：Stage1~5 内切 tab；到环节1 则回 Stage0.5；Stage0.5 回 Stage0。"""
        idx = self.stack.currentIndex()
        if idx == 0:
            return
        if idx == 1:
            self.stack.setCurrentIndex(0)
            return
        # idx == 2: 中央大环节
        if self.tabs.currentIndex() > 0:
            self.tabs.setCurrentIndex(self.tabs.currentIndex() - 1)
        else:
            self.stack.setCurrentIndex(1)

    def _on_next(self):
        """下一步：仅在当前环节全通过时放行（按钮已 disabled 控制）。"""
        self.tabs.setCurrentIndex(
            min(self.tabs.count() - 1, self.tabs.currentIndex() + 1))


    def _build_left_run(self):
        grp = QGroupBox("")
        grp.setMinimumHeight(110)
        gv = QVBoxLayout(grp)

        top_row = QHBoxLayout()
        top_row.setSpacing(4)

        lbl = QLabel("串跑章数:")
        lbl.setStyleSheet("font-weight:bold; color:#4fc3f7; font-size:14px;")
        top_row.addWidget(lbl)

        btn_minus = QPushButton("◀")
        btn_plus = QPushButton("▶")
        for b in (btn_minus, btn_plus):
            b.setMinimumSize(30, 38)
            b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            b.setStyleSheet(BTN_3D_QSS)
            b.setToolTip("减少" if b.text() == "◀" else "增加")

        self.sb_auto_chapters = QSpinBox()
        self.sb_auto_chapters.setMinimum(1)
        self.sb_auto_chapters.setMaximum(9999)
        self.sb_auto_chapters.setValue(1)
        self.sb_auto_chapters.setToolTip("从当前章起连续跑多少章后停止")
        self.sb_auto_chapters.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.sb_auto_chapters.setAlignment(_Qt.AlignCenter)
        self.sb_auto_chapters.setMinimumHeight(38)
        self.sb_auto_chapters.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.sb_auto_chapters.setStyleSheet(
            "QSpinBox{font-weight:bold; color:#4fc3f7; font-size:16px; padding:2px 4px;}"
            "QSpinBox:focus{border:1px solid #4fc3f7;}"
        )
        top_row.addWidget(btn_minus)
        top_row.addWidget(self.sb_auto_chapters)
        top_row.addWidget(btn_plus)
        gv.addLayout(top_row)

        btn_minus.clicked.connect(self.sb_auto_chapters.stepDown)
        btn_plus.clicked.connect(self.sb_auto_chapters.stepUp)

        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)
        self.b_cauto = QPushButton("🚀 全自动串跑")
        self.b_cauto.setMinimumHeight(34)
        self.b_cauto.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.b_cauto.setStyleSheet(BTN_3D_QSS)
        self.b_cstop = QPushButton("⏹ 停止")
        self.b_cstop.setMinimumHeight(34)
        self.b_cstop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.b_cstop.setStyleSheet(BTN_3D_QSS)
        btn_col.addWidget(self.b_cauto)
        btn_col.addWidget(self.b_cstop)
        gv.addLayout(btn_col)

        self.b_cauto.clicked.connect(self._run_collab_auto)
        self.b_cstop.clicked.connect(self.on_stop)

        old = self.player_dock.widget()
        old_layout = old.layout()
        old_layout.removeWidget(self.table)
        self.table.setParent(None)
        bar_layout = old_layout.itemAt(0).layout()
        bar_layout.removeWidget(self.b_add)
        self.b_add.setParent(None)
        old.deleteLater()

        left_root = QWidget()
        lv = QVBoxLayout(left_root)
        lv.setContentsMargins(6, 6, 6, 6)
        lv.setSpacing(6)

        tool_col = QGridLayout()
        tool_col.setContentsMargins(0, 0, 0, 0)
        tool_col.setSpacing(4)
        tool_col.setColumnStretch(0, 1)
        tool_col.setColumnStretch(1, 1)

        b_all = QPushButton("▶ 启动全部AI")
        b_stop = QPushButton("⏹ 停止全部AI")
        b_refresh = QPushButton("🔄 刷新状态")
        b_restart = QPushButton("🔄 重启程序")
        b_open_ws = QPushButton("📂 工作区")
        b_open_out = QPushButton("📂 产出目录")
        for b in (b_all, b_stop, b_refresh, b_restart, b_open_ws, b_open_out):
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            b.setStyleSheet(BTN_3D_QSS)
        b_all.clicked.connect(self.a_all.trigger)
        b_stop.clicked.connect(self.a_stop.trigger)
        b_refresh.clicked.connect(self.a_refresh.trigger)
        b_restart.clicked.connect(self.a_restart.trigger)
        b_open_ws.clicked.connect(self.a_open_ws.trigger)
        b_open_out.clicked.connect(self.a_open_out.trigger)

        self.ruler_btn = QPushButton("📏")
        self.ruler_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ruler_btn.setToolTip("尺子")
        self.ruler_btn.setStyleSheet(
            "QPushButton{background:#2d2d30;color:#00e5ff;border:1px solid #00e5ff;}")
        self.ruler_btn.clicked.connect(self._toggle_ruler)
        self.shot_btn = QPushButton("📸")
        self.shot_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.shot_btn.setToolTip("截图")
        self.shot_btn.setStyleSheet(
            "QPushButton{background:#2d2d30;color:#00e5ff;border:1px solid #00e5ff;}")
        self.shot_btn.setVisible(False)
        self.shot_btn.clicked.connect(lambda: self._take_screenshot(False))

        tool_col.addWidget(b_all, 0, 0)
        tool_col.addWidget(b_stop, 0, 1)
        tool_col.addWidget(b_refresh, 1, 0)
        tool_col.addWidget(b_restart, 1, 1)
        tool_col.addWidget(b_open_ws, 2, 0)
        tool_col.addWidget(b_open_out, 2, 1)
        tool_col.addWidget(self.ruler_btn, 3, 0)
        tool_col.addWidget(self.shot_btn, 3, 1)
        lv.addLayout(tool_col)

        self.cb_dry.setVisible(False)
        self.lbl_mode.setVisible(False)

        bar = QWidget()
        bh = QHBoxLayout(bar)
        bh.setContentsMargins(0, 0, 0, 0)
        bh.addWidget(self.b_add)

        table_box = QWidget()
        tbv = QVBoxLayout(table_box)
        tbv.setContentsMargins(0, 0, 0, 0)
        tbv.setSpacing(4)
        tbv.addWidget(bar)
        self.table.setMinimumHeight(200)
        tbv.addWidget(self.table)

        split = QSplitter(_Qt.Vertical)
        split.setHandleWidth(6)
        grp.setMinimumHeight(80)
        split.addWidget(grp)
        split.addWidget(table_box)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        lv.addWidget(split, 1)

        for p in self.players:
            self.chat_ai.addItem(p.get("名字", "?"))

        self.chat_btn.clicked.connect(self.quick_send)
        self.chat_in.returnPressed.connect(self.quick_send)

        self.player_dock.setWidget(left_root)
        self.player_dock.setWindowTitle("工具 / 选手 / 运行")
        self.player_dock.setFixedWidth(335)


    def log_line(self, s):
        self.run_log.append(f"[{time.strftime('%H:%M:%S')}] {s}")
        sb_ = self.run_log.verticalScrollBar()
        sb_.setValue(sb_.maximum())
        self._append_proj_log(s)

    def _append_proj_log(self, s):
        """把运行日志按项目追加写入 <项目>/_logs/run_YYYYMMDD.log，方便按项目回溯。"""
        proj_ws = getattr(self, "_proj_ws", None)
        if not proj_ws:
            return
        log_dir = os.path.join(proj_ws, "_logs")
        try:
            os.makedirs(log_dir, exist_ok=True)
            fp = os.path.join(log_dir, "run_" + time.strftime("%Y%m%d") + ".log")
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(fp, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {s}\n")
        except Exception:
            pass

    def _write_tree_manifest(self, tag=""):
        """遍历项目产出目录，生成产物文件树清单（相对路径/大小/修改时间），
        写入 <项目>/_logs/文件树清单_<tag>_<时间戳>.json，方便按项目回溯各阶段产出。"""
        proj_ws = getattr(self, "_proj_ws", None)
        if not proj_ws or not os.path.isdir(proj_ws):
            return
        log_dir = os.path.join(proj_ws, "_logs")
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception:
            return
        files = []
        for root, dirs, names in os.walk(proj_ws):
            # 不把 _logs 自身（日志/历史清单）算进产物清单，避免自我递归噪声
            dirs[:] = [d for d in dirs if d != "_logs"]
            for n in names:
                fp = os.path.join(root, n)
                rel = os.path.relpath(fp, proj_ws).replace(os.sep, "/")
                try:
                    st = os.stat(fp)
                    files.append({
                        "path": rel,
                        "size": st.st_size,
                        "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
                    })
                except Exception:
                    pass
        files.sort(key=lambda x: x["path"])
        stamp = time.strftime("%Y%m%d_%H%M%S")
        fname = (f"文件树清单_{tag}_{stamp}.json" if tag else f"文件树清单_{stamp}.json")
        out = os.path.join(log_dir, fname)
        try:
            with open(out, "w", encoding="utf-8") as f:
                json.dump({
                    "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "project": getattr(self, "_proj_name", ""),
                    "files": files,
                }, f, ensure_ascii=False, indent=2)
            self.log_line(f"📋 已生成产物文件树清单：{fname}（{len(files)} 个文件）")
        except Exception as e:
            self.log_line(f"⚠ 生成文件树清单失败：{e}")

    def _refresh_all_panels(self):
        self._sync_stage_running()
        for p in getattr(self, "stage_panels", []):
            # 先更新启动可用性，再 refresh，保证面板内提示语读到的是最新状态
            if p.pipeline[0]["key"] == "规划":
                p.set_start_enabled(self._plan_outline_ready())
            else:
                # 其余环节的【启动】保持可用（指派模式内会自动禁用）
                p.set_start_enabled(not getattr(self, "_auto_mode", False))
            p.refresh()
        # 指派模式下一旦所有环节都指派完成，自动退出并点亮【启动】
        if getattr(self, "_auto_mode", False) and self._all_stages_assigned():
            self._finish_assign_mode()
        self._update_chapter_labels()
        self._update_nav()

    def _on_auto_refresh(self):
        """全自动串跑期间从工作线程发射到主线程：切到当前环节页签并刷新状态。"""
        try:
            import auto_stage as _as
            _, rstate = _as.load()
            cur = rstate.get("current_stage", "写作")
            self._goto_stage(cur)
        except Exception as _e:
            self.log_line(f"⚠ 自动切页异常：{_e}")
        self._refresh_all_panels()

    def _update_nav(self):
        if not hasattr(self, "tabs") or not self.stage_panels:
            return
        idx = self.tabs.currentIndex()
        if idx < 0:
            return
        panel = self.stage_panels[idx]
        st = panel.pipeline[0]
        sk = st["key"]
        label = st["label"]
        run_state = panel.run_state
        cur = run_state["current_stage"]
        status = run_state["stages"][sk]["status"]
        if sk == cur:
            text = f"● 环节{idx+1} {label}（进行中）"
            color = "#1a73e8"
        elif status == "passed":
            text = f"✅ 环节{idx+1} {label}（已放行）"
            color = "#1e8e3e"
        else:
            text = f"⏳ 环节{idx+1} {label}（未开始）"
            color = "#888888"
        self.stage_indicator.setText(text)
        self.stage_indicator.setStyleSheet(
            f"font-size:14px; font-weight:bold; color:{color};")
        all_passed = sb.stage_all_passed(run_state, sk)
        self.btn_next.setEnabled(all_passed)
        if all_passed:
            self.btn_next.setToolTip("进入下一环节 →")
        else:
            failed = sb.stage_failed_steps(run_state, sk)
            tip = "本环节尚未全部通过(✔)"
            if failed:
                tip += f"：已 × 子步 {failed}"
            else:
                tip += "（仍有子步为 未判定/未通过）"
            self.btn_next.setToolTip(tip)

        # 根据当前环节动态调整日志区上方高度，让日志窗口更大
        if hasattr(self, "top"):
            if idx == 4:           # 环节5
                self.top.setFixedHeight(350)
            elif idx in (2, 3):    # 环节3、4
                self.top.setFixedHeight(400)
            else:                  # 环节1、2
                self.top.setFixedHeight(460)

    def _plan_outline_ready(self):
        """规划环节必须以「故事梗概」为上游参考；梗概未落稿前不应启动。"""
        init_dir = os.path.join(getattr(self, "_proj_ws", ""), "00_初始化")
        p = os.path.join(init_dir, "故事梗概.md")
        return os.path.exists(p) and os.path.getsize(p) >= 1

    def _run_collab_stage(self, sk):
        # 指派模式完成后的启动：点【启动】直接开始全自动串跑
        if getattr(self, "_auto_ready", False):
            self._auto_ready = False
            self.log_line("🚀 AI 指派已完成，开始全自动串跑…")
            self._run_collab_auto()
            return
        # 规划环节需先生成故事梗概（梗概 + 后续调整意见）；梗概未落稿禁止启动
        if sk == "规划" and not self._plan_outline_ready():
            self.log_line("⛔ 规划环节需要先有「故事梗概」：请回到「故事梗概确认」页，"
                          "点生成/上传梗概并确认后，再启动规划。")
            QMessageBox.warning(
                self, "缺少故事梗概",
                "规划环节以「故事梗概」为上游参考，梗概尚未落稿。\n\n"
                "请先回到「故事梗概确认」页：\n"
                "  • 点「下一步 → 进入环节1」让 WorkBuddy 生成梗概，或\n"
                "  • 点「上传参考大纲」导入已有大纲，\n"
                "确认后再启动规划。")
            return
        dry = self.cb_dry.isChecked()
        import pipeline_runner as _pr
        _pr.set_dry_run(dry)
        import collab_exec as _ce
        _ce.set_dry_run(dry)
        import auto_stage as _as
        _as.set_project_workspace(getattr(self, "_proj_ws", None)
                                  or paths.output_path(getattr(self, "_proj_name", "")))
        # 同步章节进度（当前章/总章数）从项目工作区
        _as.load_chapter_progress()
        # 启动前按磁盘真实产物复核各子项状态（默认红，只有真实文件才绿）
        _as.verify_chapter_from_disk(_as.get_current_chapter())
        self._update_chapter_labels()

        # 章为核心：每章以「写作」为起点，启动写作时重置章核心环节门控，避免上一章通过态残留
        if sk == "写作":
            _as.reset_chapter_cycle()
            self._refresh_all_panels()

        # 防止重复启动：同一环节正在运行时，只有“已暂停”才视为继续；否则忽略本次点击
        if getattr(self, "_stage_worker", None) and self._stage_worker.isRunning():
            if getattr(self, "_stage_paused", False):
                self._stage_paused = False
                _ce.resume()
                self.log_line("▶ 继续运行")
            else:
                self.log_line("⚠ 环节正在运行，请勿重复点击启动；如需暂停请点「暂停」")
            return

        # 章核心环节按当前章单章运行；非章环节（规划）忽略章号
        chapter = _as.get_current_chapter() if sk in _as.CHAPTER_AWARE_STAGES else None
        ch_tag = f" 第{chapter:03d}章" if chapter else ""
        self.log_line(f"=== 运行大环节: {sk}{ch_tag} (dry={dry}) ===")
        self._stage_worker = _StageRunWorker(sk, dry, chapter)
        self._stage_worker.progress.connect(self.log_line)
        self._stage_worker.refresh.connect(self._refresh_all_panels)
        self._stage_worker.done.connect(self._on_stage_done)
        self._running_stage_key = sk   # 标记真实运行中的环节（驱动提示语）
        self._sync_stage_running()
        self._stage_worker.start()

    def _sync_stage_running(self):
        """把「当前真实运行中的环节」同步到各面板（驱动提示语显示）。"""
        cur = getattr(self, "_running_stage_key", None)
        for p in getattr(self, "stage_panels", []):
            try:
                p.set_running(p.pipeline[0]["key"] == cur)
            except Exception:
                pass

    def _on_stage_done(self, ok, msg):
        sk = getattr(self, "_running_stage_key", None)
        self._stage_paused = False
        self._running_stage_key = None
        self._sync_stage_running()
        self._refresh_all_panels()
        if ok:
            self.log_line("✅ 大环节运行结束")
        else:
            self.log_line(f"⚠ 大环节运行结束：{msg}" if msg else "⚠ 大环节运行结束")
        # 环节结束：更新产物文件树清单到 _logs（按项目回溯各阶段产出）
        self._write_tree_manifest(sk or "环节")

    def _run_collab_next_item(self, sk):
        """手动模式：发送本环节下一个待运行的子项（块/审核/调整）。"""
        # 规划环节需先有故事梗概
        if sk == "规划" and not self._plan_outline_ready():
            self.log_line("⛔ 规划环节需要先有「故事梗概」：请回到「故事梗概确认」页生成/上传梗概并确认后，再发送。")
            QMessageBox.warning(
                self, "缺少故事梗概",
                "规划环节以「故事梗概」为上游参考，梗概尚未落稿。\n\n"
                "请先回到「故事梗概确认」页：\n"
                "  • 点「下一步 → 进入环节1」让 WorkBuddy 生成梗概，或\n"
                "  • 点「上传参考大纲」导入已有大纲，\n"
                "确认后再发送规划。")
            for p in self.stage_panels:
                p._unlock_start()
            return
        dry = self.cb_dry.isChecked()
        import pipeline_runner as _pr
        _pr.set_dry_run(dry)
        import collab_exec as _ce
        _ce.set_dry_run(dry)
        import auto_stage as _as
        _as.set_project_workspace(getattr(self, "_proj_ws", None)
                                  or paths.output_path(getattr(self, "_proj_name", "")))
        # 同步章节进度（当前章/总章数）从项目工作区
        _as.load_chapter_progress()
        # 发送前按磁盘真实产物复核各子项状态（默认红，只有真实文件才绿）
        _as.verify_chapter_from_disk(_as.get_current_chapter())
        self._update_chapter_labels()

        # 章为核心：每章以「写作」为起点，发送写作时重置章核心环节门控，避免上一章通过态残留
        if sk == "写作":
            _as.reset_chapter_cycle()
            self._refresh_all_panels()

        # 防止重复发送：上一轮仍在运行时忽略
        if (getattr(self, "_stage_worker", None) and self._stage_worker.isRunning()) or \
           (getattr(self, "_next_worker", None) and self._next_worker.isRunning()):
            self.log_line("⚠ 上一轮发送仍在进行，请等待当前子项完成（或点暂停/停止）后再发下一个。")
            for p in self.stage_panels:
                p._unlock_start()
            return

        chapter = _as.get_current_chapter() if sk in _as.CHAPTER_AWARE_STAGES else None
        ch_tag = f" 第{chapter:03d}章" if chapter else ""
        self.log_line(f"=== 手动发送：环节【{sk}】下一个子项{ch_tag}（dry={dry}）===")
        self._last_next_sk = sk
        self._next_worker = _StageNextWorker(sk, dry, chapter)
        self._next_worker.progress.connect(self.log_line)
        self._next_worker.refresh.connect(self._refresh_all_panels)
        self._next_worker.done.connect(self._on_next_done)
        self._next_worker.start()

    def _on_next_done(self, ok, msg):
        # 解锁面板按钮（无论成功与否），让用户继续点「发送下一个子项」
        for p in self.stage_panels:
            p._unlock_start()
        self._refresh_all_panels()
        if ok:
            self.log_line("✅ 已发送并完成本环节下一个子项；如还需继续，请再次点【发送下一个子项】。"
                          "全部子项通过后可点【放行】。")
        else:
            self.log_line(f"⚠ 本子项发送结束（{msg}）；如需重跑，可点该子项的 ✖ 红钮作废后再次发送。" if msg
                          else "⚠ 本子项发送结束；可能已全部通过，或前序有未通过项。")
        # 子项发送完成：更新产物文件树清单到 _logs（按项目回溯）
        self._write_tree_manifest(getattr(self, "_last_next_sk", None) or "子项")

    def _run_collab_stage_current(self):
        sk = self.stage_panels[0].run_state["current_stage"]
        self._run_collab_stage(sk)

    def _all_stages_assigned(self):
        """检查是否所有环节的全部子项（块/审核者/调整者）都已指派 AI。"""
        import stage_board as _sb
        state, _ = _sb.load()
        for st in _sb.PIPELINE:
            sk = st["key"]
            for step in st["steps"]:
                sn = step["name"]
                cfg = (state.get(sk, {}).get("steps", {}) or {}).get(sn, {}) or {}
                blocks = cfg.get("blocks", {})
                vals = list(blocks.values()) if isinstance(blocks, dict) else list(blocks or [])
                vals.append(cfg.get("reviewer"))
                if not step.get("final"):
                    vals.append(cfg.get("adjuster"))
                if any(not v for v in vals):
                    return False
        return True

    def _enter_assign_mode(self):
        """进入 AI 指派模式：启动禁用、放行全亮，用户逐环节指派后点放行切换。"""
        self._auto_mode = True
        self._auto_ready = False
        for p in self.stage_panels:
            p.set_assign_mode(True)
        self.log_line("🧩 进入 AI 指派模式：请逐环节为各子项选择 AI；"
                      "指派完当前环节后点【放行】切换到下一环节（此过程不会运行任务）。")

    def _finish_assign_mode(self):
        """全部环节指派完成：退出指派模式，点亮启动，点击启动即开始串跑。"""
        self._auto_mode = False
        self._auto_ready = True
        for p in self.stage_panels:
            p.set_assign_mode(False)
        self.log_line("✅ 全部环节 AI 均已指派完成：【启动】已点亮，点击【启动】即开始全自动串跑。")

    def _run_collab_auto(self):
        """覆盖基类：全自动串跑从当前章起，按「串跑章数」连续跑完指定章数。

        流程：先进入 AI 指派模式让用户为每个环节选择 AI；全部指派完成并点击【启动】后
        (_auto_ready=True) 才真正开始串跑。不会自动指派或跳过指派。"""
        # 只有用户刚完成指派并点【启动】(_auto_ready=True) 时才真正开跑；
        # 否则一律先进入指派模式，让用户先选好每个环节的 AI。
        if not getattr(self, "_auto_ready", False):
            self._enter_assign_mode()
            return
        import auto_stage as _as
        dry = self.cb_dry.isChecked()
        _as.set_dry_run(dry)
        _as.set_project_workspace(getattr(self, "_proj_ws", None)
                                  or paths.output_path(getattr(self, "_proj_name", "")))
        _as.load_chapter_progress()
        _as.verify_chapter_from_disk(_as.get_current_chapter())
        self._update_chapter_labels()
        start = _as.get_current_chapter()
        count = self.sb_auto_chapters.value()
        self.log_line(f"🚀 启动全自动串跑：从第{start:03d}章起，连续跑 {count} 章")
        _as.run_all_threaded(log_fn=lambda s: self.auto_log.emit(s), dry=dry,
                             done_fn=self._collab_auto_done,
                             start_chapter=start, chapter_count=count,
                             refresh_fn=lambda: self.auto_refresh.emit())

    def _advance_and_run_next(self, next_sk):
        """放行后只切到下一环节/下一章的页签并自动指派首个 AI，不自动运行。

        默认手动：真正连跑需点「🚀 全自动串跑」。章为核心：出厂放行后若还有下一章，
        则回到「写作」页签并进入下一章（仍不自动运行）。
        指派模式下：放行仅切换环节页签，全部指派完成后点亮【启动】。
        """
        if getattr(self, "_auto_mode", False):
            if next_sk:
                order = [p.pipeline[0]["key"] for p in self.stage_panels]
                if next_sk in order:
                    self.tabs.setCurrentIndex(order.index(next_sk))
                    self.log_line(f"🧩 指派模式 → 环节【{next_sk}】：请为该环节各子项选择 AI，完成后点【放行】")
            if self._all_stages_assigned():
                self._finish_assign_mode()
            return
        import auto_stage as _as
        if not next_sk:
            cur = _as.get_current_chapter()
            total = _as.get_chapter_total()
            if cur < total:
                _as.set_current_chapter(cur + 1)
                _as.save_chapter_progress()
                self.log_line(f"📖 第{cur:03d}章已放行 → 进入第{cur + 1:03d}/{total:03d}章：写作环节（请手动点「执行本环节」）")
                self._goto_stage("写作")
                self._update_chapter_labels()
                return
            self.log_line("🎉 全部章节已放行完成，全流程结束")
            self._update_chapter_labels()
            return
        order = [p.pipeline[0]["key"] for p in self.stage_panels]
        if next_sk not in order:
            return
        idx = order.index(next_sk)
        self.tabs.setCurrentIndex(idx)
        self.log_line(f"➡ 已放行并进入下一环节：{next_sk}（请手动点「执行本环节」）")
        # 不再自动为下一环节指派首个 AI：用户必须自己先选择好每个环节的 AI。
        return

    def _goto_stage(self, sk):
        """切换到指定环节页签（tabBar 隐藏，靠索引切换）。"""
        order = [p.pipeline[0]["key"] for p in getattr(self, "stage_panels", [])]
        if sk in order:
            self.tabs.setCurrentIndex(order.index(sk))

    def _update_chapter_labels(self):
        """在各章核心环节页签顶部显示「第 k/N 章 · 对应章节文件夹」。"""
        import auto_stage as _as
        ws = getattr(self, "_proj_ws", None)
        if ws:
            _as.set_project_workspace(ws)
            _as.load_chapter_progress()
        k = _as.get_current_chapter()
        N = _as.get_chapter_total()
        if hasattr(self, "sb_auto_chapters"):
            remaining = max(1, N - k + 1)
            self.sb_auto_chapters.setMaximum(remaining)
            if self.sb_auto_chapters.value() > remaining:
                self.sb_auto_chapters.setValue(remaining)
        folder_map = {"写作": "02_写作", "去AI": "03_去AI", "审核": "04_审核", "出厂": "05_出厂"}
        for p in getattr(self, "stage_panels", []):
            sk = p.pipeline[0]["key"]
            if sk in folder_map:
                p.set_chapter_info(sk, f"第{k:03d}/{N:03d}章")

    def _on_pause(self):
        import collab_exec as _ce
        _ce.pause()
        self._stage_paused = True
        self.log_line("⏸ 已请求暂停（协同写作）")

    def _collab_auto_done(self):
        # 由后台线程调用，必须全部走信号回主线程，禁止直接触碰控件
        self.auto_log.emit("✅ 程序二全自动结束")
        self.auto_refresh.emit()

    def _sync_ais_to_players(self):
        names = [p.get("名字", "?") for p in self.players]
        for p in getattr(self, "stage_panels", []):
            p.set_ais(names)

    def rebuild_table(self):
        super().rebuild_table()
        self._sync_ais_to_players()


    def _on_random_generate(self):
        import random
        # 先保存脏标记，避免后续信号改变它们影响判断
        name_d = self._name_dirty or bool(self.init_name.findChild(QLineEdit).text().strip())
        channel_d = self._channel_dirty
        genre_d = self._genre_dirty
        sub_d = self._sub_dirty
        chapters_d = self._chapters_dirty
        gender_d = self._gender_dirty
        support_d = self._support_dirty
        templates_d = self._templates_dirty
        tone_d = self._tone_dirty
        atmo_d = self._atmo_dirty
        pace_d = self._pace_dirty
        personality_d = self._personality_dirty
        emotion_d = self._emotion_dirty
        golden_d = self._golden_dirty
        desc_d = self._desc_dirty or bool(self.init_desc.toPlainText().strip())

        if not name_d:
            names = ["逆天改命", "重生之都市战神", "我在修仙界送外卖", "女帝归来", "末世囤货王", "开局签到十个亿"]
            self.init_name.findChild(QLineEdit).setText(random.choice(names) + str(random.randint(1, 999)))
        if not channel_d:
            self.init_channel.findChild(QComboBox).setCurrentIndex(random.randint(0, 1))
        if not genre_d:
            genre = random.choice(list(self.GENRE_SUBS.keys()))
            self.init_genre.findChild(QComboBox).setCurrentText(genre)
        if not sub_d:
            subs = self.GENRE_SUBS.get(self.init_genre.findChild(QComboBox).currentText(), [])
            if subs:
                self.init_sub.findChild(QComboBox).setCurrentText(random.choice(subs))
        if not chapters_d:
            self.init_chapters.setValue(random.randint(50, 500))
        if not gender_d:
            self.init_gender.findChild(QComboBox).setCurrentIndex(random.randint(0, 2))
        if not support_d:
            self.init_support.setValue(random.randint(1, 8))
        if not templates_d:
            self._pick_random_toggle(self.init_templates)
        if not tone_d:
            self._pick_random_radio(self.init_tone)
        if not atmo_d:
            self._pick_random_radio(self.init_atmo)
        if not pace_d:
            self._pick_random_radio(self.init_pace)
        if not personality_d:
            self._pick_random_toggle(self.init_personality, min_pct=0.2, max_pct=0.5)
        if not emotion_d:
            self._pick_random_toggle(self.init_emotion, min_pct=0.1, max_pct=0.4)
        if not golden_d:
            self._pick_random_toggle(self.init_golden, min_pct=0.1, max_pct=0.4)
        if not desc_d:
            self.init_desc.setPlainText("随机生成的项目设定，可直接开始规划。")
        self.log_line("已随机生成项目设定，进入梗概确认页…")
        self._on_stage0_confirm()

    def _pick_random_toggle(self, widget, min_pct=0.2, max_pct=0.6):
        import random
        btns = widget.findChildren(QPushButton)
        for b in btns:
            b.setChecked(False)
        if not btns:
            return
        k = max(1, int(len(btns) * random.uniform(min_pct, max_pct)))
        for b in random.sample(btns, min(k, len(btns))):
            b.setChecked(True)

    def _pick_random_radio(self, widget):
        import random
        group = getattr(widget, "button_group", None)
        if not group:
            return
        btns = group.buttons()
        if btns:
            random.choice(btns).setChecked(True)

    def _on_upload_outline(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "上传参考大纲", "",
            "文本文件 (*.txt *.md *.docx);;所有文件 (*.*)")
        if not path:
            return
        try:
            if path.lower().endswith(".docx"):
                try:
                    from docx import Document
                    doc = Document(path)
                    self.reference_outline = "\n".join(p.text for p in doc.paragraphs)
                except Exception:
                    self.log_line("读取 docx 失败，请安装 python-docx")
                    return
            else:
                with open(path, "r", encoding="utf-8") as f:
                    self.reference_outline = f.read()
            # 落盘，使规划环节能以其为上游参考（否则会被拦下）
            init_dir = os.path.join(getattr(self, "_proj_ws", ""), "00_初始化")
            os.makedirs(init_dir, exist_ok=True)
            with open(os.path.join(init_dir, "故事梗概.md"), "w", encoding="utf-8") as f:
                f.write(self.reference_outline + "\n")
            self.outline_label.setText(f"已上传：{os.path.basename(path)} ({len(self.reference_outline)} 字)")
            self.log_line(f"已上传参考大纲：{os.path.basename(path)}")
            self._refresh_all_panels()
        except Exception as e:
            self.log_line(f"读取参考大纲失败：{e}")

    def _generate_summary(self, data, outline=""):
        if outline.strip():
            return outline.strip()
        parts = [f"《{data['name']}》"]
        parts.append(
            f"{data['channel']} · {data['genre']} · {data['sub_genre']}，共 {data['chapters']} 章。")
        parts.append(f"主角：{data['protagonist']['gender']}，配角 {data['supporting_roles']['count']} 人。")
        if data['supporting_roles']['templates']:
            parts.append(f"角色模板：{', '.join(data['supporting_roles']['templates'])}。")
        core = data['story_core']
        parts.append(f"故事基调：{core['tone']}，氛围：{core['atmosphere']}，节奏：{core['pace']}。")
        if data['protagonist']['personality']:
            parts.append(f"主角性格：{', '.join(data['protagonist']['personality'])}。")
        if data['emotion_line']:
            parts.append(f"感情线：{', '.join(data['emotion_line'])}。")
        if data['golden_finger']:
            parts.append(f"金手指/设定：{', '.join(data['golden_finger'])}。")
        if data['extra_ideas']:
            parts.append(f"额外想法：{data['extra_ideas']}")
        return "\n\n".join(parts)

    def _build_summary_widget(self):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 4, 0, 4)
        v.setSpacing(3)

        # 顶部标题与说明，不抢占空间
        title = QLabel("环节 0.5 · 故事梗概确认")
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#00e5ff;")
        v.addWidget(title)

        hint = QLabel("请确认以下故事梗概是否合适。不合适可在下方输入调整要求，或手动编辑梗概。")
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#aaaaaa;font-size:12px;")
        v.addWidget(hint)

        # 大展示窗口
        self.summary_edit = QTextEdit()
        self.summary_edit.setPlaceholderText("根据项目标签或参考大纲生成的故事梗概…")
        self.summary_edit.setMinimumHeight(550)
        self.summary_edit.setMaximumHeight(550)
        self.summary_edit.setStyleSheet("""
            QTextEdit{
                color:#e0e0e0;
                background-color:#1e1e1e;
                border:1px solid #3a3a3a;
                border-radius:4px;
                padding:6px;
            }
        """)
        v.addWidget(self.summary_edit, 1)

        # 调整记录（紧凑底部）
        chat_label = QLabel("调整记录")
        chat_label.setStyleSheet("color:#aaaaaa;font-size:12px;")
        v.addWidget(chat_label)

        self.summary_chat = QTextEdit()
        self.summary_chat.setReadOnly(True)
        self.summary_chat.setMinimumHeight(60)
        self.summary_chat.setMaximumHeight(90)
        self.summary_chat.setStyleSheet("""
            QTextEdit{
                color:#aaa;
                background-color:#1a1a1a;
                border:1px solid #333;
                border-radius:4px;
                padding:4px;
            }
        """)
        v.addWidget(self.summary_chat)

        chat_row = QHBoxLayout()
        chat_row.setSpacing(4)
        self.summary_input = QLineEdit()
        self.summary_input.setPlaceholderText("输入调整要求，例如：把主角改成女主、节奏放慢…")
        self.summary_input.returnPressed.connect(self._on_summary_adjust)
        chat_row.addWidget(self.summary_input, 1)
        send_btn = QPushButton("发送")
        send_btn.setMaximumWidth(70)
        send_btn.clicked.connect(self._on_summary_adjust)
        chat_row.addWidget(send_btn)
        v.addLayout(chat_row)

        # 底部按钮区
        top_foot = QHBoxLayout()
        # 环节0.5 执行 AI 选择（默认 WorkBuddy，可下拉改选）
        self.summary_ai_combo = QComboBox()
        self.summary_ai_combo.setMinimumHeight(32)
        self.summary_ai_combo.setMinimumWidth(130)
        self.summary_ai_combo.setToolTip("选择由哪个 AI 生成/接收故事梗概任务（环节0.5）")
        _names = self._ai_app_names() or ["WorkBuddy"]
        self.summary_ai_combo.addItems(_names)
        if "WorkBuddy" in _names:
            self.summary_ai_combo.setCurrentText("WorkBuddy")
        top_foot.addWidget(self.summary_ai_combo)
        top_foot.addStretch(1)
        back_btn = QPushButton("返回上一页")
        back_btn.setMinimumHeight(32)
        back_btn.setStyleSheet("""
            QPushButton{
                padding:6px 14px;
                font-size:14px;
                font-weight:bold;
                color:#cfcfcf;
                background-color:#2d2d30;
                border:1px solid #5a5a5a;
                border-radius:5px;
            }
            QPushButton:hover{border-color:#00e5ff;color:#fff;}
            QPushButton:pressed{border-color:#1a73e8;}
        """)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        top_foot.addWidget(back_btn)
        regen_btn = QPushButton("🔄 重新生成")
        regen_btn.setMinimumHeight(32)
        regen_btn.clicked.connect(self._on_summary_regen)
        top_foot.addWidget(regen_btn)
        v.addLayout(top_foot)

        # 第二排：醒目的下一步，占满宽度，便于点击
        next_btn = QPushButton("下一步 → 进入环节1")
        next_btn.setMinimumHeight(36)
        next_btn.setStyleSheet("""
            QPushButton{
                padding:8px 16px;
                font-size:15px;
                font-weight:bold;
                color:#fff;
                background-color:#1a73e8;
                border-radius:5px;
            }
            QPushButton:hover{background-color:#2b7de9;}
            QPushButton:pressed{background-color:#1557b0;}
        """)
        next_btn.clicked.connect(self._on_summary_next)
        v.addWidget(next_btn)

        return w

    def _on_summary_adjust(self):
        text = self.summary_input.text().strip()
        if not text:
            return
        self.summary_chat.append(f"客户：{text}")
        current = self.summary_edit.toPlainText().strip()
        if current:
            self.summary_edit.setPlainText(current + f"\n\n[调整要求] {text}")
        else:
            self.summary_edit.setPlainText(f"[调整要求] {text}")
        self.summary_input.clear()

    def _on_summary_regen(self):
        if not self._current_init_data:
            self.log_line("缺少项目初始化数据，无法重新生成")
            return
        summary = self._generate_summary(self._current_init_data, self.reference_outline)
        self.summary_edit.setPlainText(summary)
        self.summary_chat.append("系统：已根据原始标签重新生成梗概")

    def _on_summary_next(self):
        summary = self.summary_edit.toPlainText().strip()
        if not summary:
            self.log_line("故事梗概为空，请先填写或生成梗概")
            return
        try:
            path = paths.join("work", "collab", "story_summary.txt")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(summary)
            self.log_line("故事梗概已确认并保存")
        except Exception as e:
            self.log_line(f"保存梗概失败：{e}")
        # 流程0.5 → 下一步：自动把提示词+标签通过 CDP 发给 WorkBuddy
        self._auto_send_to_workbuddy(summary)
        self.stack.setCurrentIndex(2)

    # ------------------------------------------------- 流程0 自动发 WorkBuddy
    # 流程0.5 提示词（固定文件）
    TISHICI_PROMPT_FILE = paths.prompt_path("步骤0", "no0tisc.md")
    # 固定提示词路径（留空则不附加）
    _fixed_prompt_path = ""

    def _auto_send_to_workbuddy(self, summary):
        """流程0.5 点击「下一步」后调用：自动用 CDP 打开所选 AI（默认 WorkBuddy），
        把提示词 + 展示窗口里的关键词标签 一起输入并回车；随后后台等待
        AI 生成完成，把产出存成 MD 到 _产物/步骤0。"""
        import sys as _sys
        _sys.path.insert(0, paths.WINDOWS_USE)
        try:
            from mix_send import send as _cdp_send
            from players import launch as _launch, load_players as _load_players
        except Exception as e:
            self.log_line(f"⚠ 导入 CDP/players 模块失败：{e}")
            return

        # 0) 目标 AI：取下拉选择（默认 WorkBuddy）
        ai_name = "WorkBuddy"
        if getattr(self, "summary_ai_combo", None) is not None:
            ai_name = self.summary_ai_combo.currentText().strip() or "WorkBuddy"
        self.log_line(f"🎯 环节0.5 指定 AI：{ai_name}")

        # 1) 确保所选 AI 已启动（带 CDP）
        try:
            cfg = _load_players()
            wb = next((p for p in cfg if p.get("名字") == ai_name), None)
            if wb and not _cdp_alive(wb.get("cdp_port")):
                self.log_line(f"🚀 {ai_name} 未运行，正在启动…")
                _launch(wb)
                import time as _t
                for _ in range(25):
                    if _cdp_alive(wb.get("cdp_port")):
                        break
                    _t.sleep(1)
        except Exception as e:
            self.log_line(f"⚠ 启动 {ai_name} 失败：{e}")

        # 2) 连通性模拟：仅发极简指令，验证所选 AI 落盘
        import auto_stage as _as
        mock = getattr(_as, "MOCK_PROMPTS", False)
        if mock:
            out_dir = paths.output_path(self._proj_name, "00_初始化")
            msg = (f"【连通性模拟-请勿消耗】请在目录「{out_dir}」下创建一个 .md 文件，"
                   f"文件内容只需一行：你好，不要做额外创作，也不要输出其它内容。")
            self.log_line(f"📤 [mock] 发送连通性模拟指令到 {ai_name}…")
        else:
            # 2) 读取提示词（固定文件 no0tisc.md）
            prompt_parts = []
            try:
                if os.path.exists(self.TISHICI_PROMPT_FILE):
                    _raw = open(self.TISHICI_PROMPT_FILE, encoding="utf-8").read().strip()
                    # 把提示词里「{{产物目录}}\步骤0」重定向到本项目 00_初始化 目录
                    _raw = _raw.replace(r"{{产物目录}}\步骤0",
                                        paths.output_path(self._proj_name, "00_初始化"))
                    prompt_parts.append(paths.replace_placeholders(_raw))
                    self.log_line(f"📄 已读取提示词：{os.path.basename(self.TISHICI_PROMPT_FILE)}")
            except Exception as e:
                self.log_line(f"⚠ 读取提示词失败：{e}")

            # 3) 固定提示词（可选）
            fixed = ""
            if self._fixed_prompt_path and os.path.exists(self._fixed_prompt_path):
                try:
                    fixed = open(self._fixed_prompt_path, encoding="utf-8").read().strip()
                    self.log_line(f"📄 已读取固定提示词：{self._fixed_prompt_path}")
                except Exception as e:
                    self.log_line(f"⚠ 读取固定提示词失败：{e}")

            # 4) 组合消息：固定提示词 + 提示词 + 关键词标签 + 梗概
            tags = self._format_init_tags(self._current_init_data)
            msg = ""
            if fixed:
                msg += fixed + "\n\n"
            msg += "\n\n".join(prompt_parts)
            msg += "\n\n【客户选择的标签 / 关键词】\n" + (tags or "（无标签）")
            msg += "\n\n【已生成的故事梗概（供你参考）】\n" + (summary or "（无）")

            self.log_line(f"📤 正在通过 CDP 把提示词+标签发送到 {ai_name}…")

        try:
            r = _cdp_send(ai_name, msg)
            self.log_line(f"📨 {ai_name} 回复：{r}")
        except Exception as e:
            self.log_line(f"❌ 发送到 {ai_name} 失败：{e}")
            return

        # 5) 完成判定：网页端 AI 无法自写文件，改用「页面抓取」拿到回复并落盘；
        #    本地端（electron）AI 维持「目录监听」等其把结果写成文件。
        import time as _t
        proj = self._proj_name or (self._current_init_data or {}).get("name", "未命名项目")
        watch_dir = paths.output_path(proj, "00_初始化")
        from mix_send import _type_of as _ai_type_of
        if _ai_type_of(ai_name) == "web":
            self._wb_worker = _WebCaptureWorker(
                ai_name=ai_name, out_dir=watch_dir, proj_name=proj)
            self._wb_worker.log.connect(self.log_line)
            self._wb_worker.done.connect(self._on_wb_captured)
            self._wb_worker.start()
            self.log_line(f"⏳ 已启动网页端抓取：{ai_name} 回复后将自动落盘到 {watch_dir}")
        else:
            self._wb_worker = _WBFileWorker(
                watch_dir=watch_dir,
                start_time=_t.time(),
                proj_name=proj,
                min_bytes=1 if mock else None)
            self._wb_worker.log.connect(self.log_line)
            self._wb_worker.done.connect(self._on_wb_captured)
            self._wb_worker.start()
            self.log_line(f"⏳ 已启动后台监听：{ai_name} 生成文件后落盘到 {watch_dir}，完成后请手动点「执行本环节」")

    def _on_wb_captured(self, path):
        self.log_line(f"✅ 步骤0 产出已生成：{path}")
        # 归一化：把生成产物落为 00_初始化/故事梗概.md，供规划环节作为上游参考
        try:
            init_dir = os.path.join(self._proj_ws, "00_初始化")
            os.makedirs(init_dir, exist_ok=True)
            dst = os.path.join(init_dir, "故事梗概.md")
            if not (os.path.exists(dst) and os.path.getsize(dst) >= 1):
                import shutil as _sh
                _sh.copyfile(path, dst)
                self.log_line(f"📄 已归档为 故事梗概.md：{dst}")
        except Exception as e:
            self.log_line(f"⚠ 归档 故事梗概.md 失败：{e}")
        self.log_line("⏸ 步骤0 已完成，请在确认 AI 指派后点「执行本环节」开始运行")
        self._refresh_all_panels()   # 故事梗概已落稿，刷新后规划环节的「启动」按钮会变为可用
        self._write_tree_manifest("步骤0")   # 步骤0 产出（故事梗概等）落盘后记录文件树清单
        # 不再自动指派/运行环节1：等用户手动选好模型并点「启动」

    def _format_init_tags(self, data):
        if not data:
            return ""
        lines = []
        lines.append(f"《{data.get('name', '')}》")
        lines.append(f"{data.get('channel', '')} · {data.get('genre', '')} · "
                     f"{data.get('sub_genre', '')}，共 {data.get('chapters', '')} 章")
        prot = data.get("protagonist", {}) or {}
        sup = data.get("supporting_roles", {}) or {}
        lines.append(f"主角：{prot.get('gender', '')}，配角 {sup.get('count', '')} 人")
        if sup.get("templates"):
            lines.append("角色模板：" + "、".join(sup["templates"]))
        core = data.get("story_core", {}) or {}
        lines.append(f"故事基调：{core.get('tone', '')}，氛围：{core.get('atmosphere', '')}，"
                     f"节奏：{core.get('pace', '')}")
        if prot.get("personality"):
            lines.append("主角性格：" + "、".join(prot["personality"]))
        if data.get("emotion_line"):
            lines.append("感情线：" + "、".join(data["emotion_line"]))
        if data.get("golden_finger"):
            lines.append("金手指/设定：" + "、".join(data["golden_finger"]))
        if data.get("extra_ideas"):
            lines.append("额外想法：" + data["extra_ideas"])
        return "\n".join(lines)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QFileDialog
    _app = QApplication(sys.argv)
    apply_dark(_app)
    # 启动时解析产物根目录：读 rules/paths.json → 否则默认（程序旁 output）；
    # 首次运行（无配置）弹一次文件夹选择框，选完写入配置，取消用默认。
    paths.init_output_root(
        lambda start: QFileDialog.getExistingDirectory(
            None, "选择产物根目录（取消则用默认路径）", start))
    _win = CollabApp()
    _win.show()
    sys.exit(_app.exec())

