"""paths.py — 集中路径解析（只由本模块推导，代码里不写死任何盘符路径）。

三套根目录：
- APP_ROOT   程序根目录。
             源码运行时 = app/ 的上级目录（项目顶层）。
             打包 exe 时 = exe 所在目录（exe 旁放 app/rules/prompts/docs）。
- WORKSPACE  工作区根（跟程序走：APP_ROOT/workspace），程序内部用，用户一般不直接看。
- OUTPUT     产出区（默认 APP_ROOT/output；可在 rules/paths.json 由用户指定位置）。

提示词里用占位符 {{产物目录}} {{工作区目录}}，由 replace_placeholders 在发送前替换。
"""

import os
import sys
import json
import tempfile


def _program_root():
    """计算程序根目录。

    - 源码运行：本文件位于 app/paths.py，程序根 = app/ 的上级目录。
    - 打包 exe：程序根 = exe 所在目录（exe 与 app/rules/prompts/docs 并列）。
    """
    if getattr(sys, "frozen", False):
        # 打包成 exe：exe 所在目录就是程序根
        return os.path.dirname(os.path.abspath(sys.executable))
    # 源码运行：取本文件的上两级（app/paths.py → app/ → 程序根）
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 全局唯一，启动时算一次
APP_ROOT = _program_root()
APP_DIR = os.path.dirname(os.path.abspath(__file__))      # app/ 本身
WINDOWS_USE = os.path.join(APP_ROOT, "windows-use")       # 共享投递层（保留为共享基建）
RULES_DIR = os.path.join(APP_ROOT, "rules")
RULES_PATH = os.path.join(RULES_DIR, "paths.json")        # 用户选的产出区位置（首次运行生成）
PROMPTS_DIR = os.path.join(APP_ROOT, "prompts")
DOCS_DIR = os.path.join(APP_ROOT, "docs")
WORKSPACE = os.path.join(APP_ROOT, "workspace")
DEFAULT_OUTPUT = os.path.join(APP_ROOT, "output")

# 用户主目录（系统 API，不写死用户名）
USER_HOME = os.path.expanduser("~")

# 解析后缓存（由 init_output_root 赋值）
_OUTPUT_ROOT = None


def _is_writable(path):
    """试探：在 path 下建临时文件再删，判断是否有写权限。"""
    try:
        os.makedirs(path, exist_ok=True)
        fd, fp = tempfile.mkstemp(dir=path, prefix=".writable_test_")
        os.close(fd)
        os.remove(fp)
        return True
    except Exception:
        return False


def _read_rules():
    try:
        if os.path.exists(RULES_PATH):
            with open(RULES_PATH, encoding="utf-8") as f:
                return json.load(f) or {}
    except Exception:
        pass
    return {}


def _write_rules(output_root):
    try:
        os.makedirs(RULES_DIR, exist_ok=True)
        with open(RULES_PATH, "w", encoding="utf-8") as f:
            json.dump({"产物根目录": output_root}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def init_output_root(ask_callback=None):
    """解析产出区根目录，全程只算一次。

    ask_callback(start_dir) -> 用户选中的路径字符串，或 ''/None 表示取消。
    返回最终采用的产出区根目录。
    """
    global _OUTPUT_ROOT
    cfg = _read_rules()
    user_path = (cfg.get("产物根目录") or "").strip()
    if user_path and os.path.isdir(os.path.dirname(user_path)) and _is_writable(user_path):
        _OUTPUT_ROOT = user_path
        return _OUTPUT_ROOT

    # 没有可用配置：用默认路径（程序旁 output），无写权限则退回用户主目录
    candidate = DEFAULT_OUTPUT
    if not _is_writable(candidate):
        candidate = os.path.join(USER_HOME, "番茄流水线", "output")

    # 首次运行（配置文件不存在）才弹框让用户选；选完写入，取消则用默认
    if not os.path.exists(RULES_PATH):
        if ask_callback is not None:
            chosen = ask_callback(candidate)
            if chosen:
                candidate = chosen
        _write_rules(candidate)

    _OUTPUT_ROOT = candidate
    return _OUTPUT_ROOT


def get_output_root():
    """已解析的产出区根目录；若尚未 init 则返回默认值（不写配置、不弹框）。"""
    if _OUTPUT_ROOT is None:
        return DEFAULT_OUTPUT
    return _OUTPUT_ROOT


def output_path(*parts):
    """拼接产出区根目录下的子路径。"""
    return os.path.join(get_output_root(), *parts)


def prompt_path(*parts):
    """拼接 prompts 目录下的子路径。"""
    return os.path.join(PROMPTS_DIR, *parts)


def docs_path(*parts):
    """拼接 docs 目录下的子路径。"""
    return os.path.join(DOCS_DIR, *parts)


def workspace_path(*parts):
    """拼接工作区根目录下的子路径。"""
    return os.path.join(WORKSPACE, *parts)


def workspace_project_path(safe, *parts):
    """拼接『按项目』工作区目录（workspace/<项目名>/...）下的子路径。

    与全局 workspace_path 区分：本函数定位到具体项目的独立工作区，
    用于存放该项目的『规划文件树』与『提示词副本』（产出仍在 output/<项目名>/）。
    """
    return os.path.join(WORKSPACE, safe, *parts)


# 当前激活项目的『按项目』工作区（由初始化设置），用于 {{工作区目录}} 占位符解析
_ACTIVE_WS = None


def set_active_project_workspace(p):
    """设置当前激活项目的『按项目』工作区路径。"""
    global _ACTIVE_WS
    _ACTIVE_WS = p


def join(*parts):
    """拼接程序根目录下的子路径。"""
    return os.path.join(APP_ROOT, *parts)


def replace_placeholders(text):
    """把提示词里的占位符替换成真实路径。"""
    ws = _ACTIVE_WS or WORKSPACE
    return (text.replace("{{产物目录}}", get_output_root())
                .replace("{{工作区目录}}", ws))


def open_output_folder():
    """用系统默认方式（Windows 资源管理器）打开产出区根目录。"""
    import subprocess
    d = get_output_root()
    os.makedirs(d, exist_ok=True)
    try:
        os.startfile(d)
    except Exception:
        try:
            subprocess.run(["explorer", os.path.normpath(d)])
        except Exception:
            pass


def open_workspace_folder():
    """用系统默认方式（Windows 资源管理器）打开工作区根目录。"""
    import subprocess
    d = WORKSPACE
    os.makedirs(d, exist_ok=True)
    try:
        os.startfile(d)
    except Exception:
        try:
            subprocess.run(["explorer", os.path.normpath(d)])
        except Exception:
            pass


def ensure_dirs():
    """启动时建好工作区与产出区（跟程序走）。"""
    os.makedirs(WORKSPACE, exist_ok=True)
    os.makedirs(get_output_root(), exist_ok=True)


# 启动即保证工作区存在（产出区在 init_output_root 后 ensure）
try:
    os.makedirs(WORKSPACE, exist_ok=True)
except Exception:
    pass
