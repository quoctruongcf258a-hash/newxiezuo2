"""流水线状态机"""
import os, json, time
import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导

ROOT = os.path.join(os.path.expanduser("~"), "Desktop", "新书", "火影忍者", "七人赛马")
STATE_FILE = paths.join("windows-use", "pipeline_state.json")
CMD_ROOT = os.path.join(ROOT, "资料", "指令")

AIS = ["CodeBuddy", "QUEST", "Doubao", "Qianwen", "WorkBuddy", "ZCode"]

# 每个阶段: key / name / action / cmd_dir / check / need / 可选 n_batches / file
STAGES = [
    # 规划轮
    {"key":"plan_outline",  "name":"规划·出稿",  "action":"broadcast",      "cmd_dir":"规划轮",     "check":"产出/规划轮",     "need":7},
    {"key":"plan_review",   "name":"规划·互审",  "action":"broadcast_batch","cmd_dir":"规划轮评审", "check":"评审/规划轮",     "need":5, "n_batches":5},
    {"key":"plan_fuse",     "name":"规划·融合",  "action":"merge",          "cmd_dir":"规划轮融合", "check":"_融合产物/规划轮","need":4},
    {"key":"plan_final",    "name":"规划·终审",  "action":"broadcast_one",  "cmd_dir":"规划轮终审", "check":"评审/规划轮终审", "need":1, "file":"公共.txt"},
    # 章纲轮
    {"key":"outline_outline","name":"章纲·出稿", "action":"broadcast",      "cmd_dir":"章纲轮",     "check":"产出/章纲轮",     "need":5},
    {"key":"outline_review", "name":"章纲·互审", "action":"broadcast_batch","cmd_dir":"章纲轮评审", "check":"评审/章纲轮",     "need":5, "n_batches":5},
    {"key":"outline_fuse",   "name":"章纲·融合", "action":"merge",          "cmd_dir":"章纲轮融合", "check":"_融合产物/章纲轮","need":5},
    {"key":"outline_final",  "name":"章纲·终审", "action":"broadcast_one",  "cmd_dir":"章纲轮终审", "check":"评审/章纲轮终审", "need":1, "file":"公共.txt"},
    # 正文轮
    {"key":"write_outline",  "name":"正文·出稿", "action":"broadcast",      "cmd_dir":"正文轮",     "check":"产出/正文轮",     "need":1},
    {"key":"write_review",   "name":"正文·互审", "action":"broadcast_batch","cmd_dir":"正文轮评审", "check":"评审/正文轮",     "need":5, "n_batches":5},
    {"key":"write_fuse",     "name":"正文·融合", "action":"merge",          "cmd_dir":"正文轮融合", "check":"_融合产物/正文轮","need":4},
    {"key":"write_final",    "name":"正文·终审", "action":"broadcast_one",  "cmd_dir":"正文轮终审", "check":"评审/正文轮终审", "need":1, "file":"公共.txt"},
    # 润色轮
    {"key":"polish_outline", "name":"润色·出稿", "action":"broadcast",      "cmd_dir":"润色轮",     "check":"产出/润色轮",     "need":1},
    {"key":"polish_review",  "name":"润色·互审", "action":"broadcast_batch","cmd_dir":"润色轮评审", "check":"评审/润色轮",     "need":5, "n_batches":5},
    {"key":"polish_fuse",    "name":"润色·融合", "action":"merge",          "cmd_dir":"润色轮融合", "check":"_融合产物/润色轮","need":4},
    {"key":"polish_final",   "name":"润色·终审", "action":"broadcast_one",  "cmd_dir":"润色轮终审", "check":"评审/润色轮终审", "need":1, "file":"公共.txt"},
]

KEY2STAGE = {s["key"]: s for s in STAGES}


def get_current_key():
    if not os.path.exists(STATE_FILE):
        return STAGES[0]["key"]
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d.get("current", STAGES[0]["key"])
    except:
        return STAGES[0]["key"]


def set_current_key(key):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"current": key, "updated": time.time()}, f, ensure_ascii=False, indent=2)


def find_stage_index(key):
    for i, s in enumerate(STAGES):
        if s["key"] == key:
            return i
    return 0


def check_stage(stage):
    """检查落盘：返回 (完整数, 总数, 是否全齐)"""
    check = stage["check"]
    need = stage["need"]
    if check.startswith("_融合产物"):
        # 融合产物不在 AI 文件夹里，只看目录文件数
        d = os.path.join(ROOT, check)
        if not os.path.isdir(d):
            return 0, 1, False
        n = len([f for f in os.listdir(d) if f.endswith(".md")])
        return (1 if n >= 1 else 0), 1, (n >= 1)
    ok = 0
    total = len(AIS)
    for ai in AIS:
        d = os.path.join(ROOT, ai, check)
        if not os.path.isdir(d):
            continue
        n = len([f for f in os.listdir(d) if f.endswith((".md", ".json"))])
        if n >= need:
            ok += 1
    return ok, total, (ok == total)
