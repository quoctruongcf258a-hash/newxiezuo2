import os, subprocess
import paths  # 集中路径：源码/打包 exe 都通过 paths.py 推导

VENV_PY = os.path.join(paths.WINDOWS_USE, ".venv", "Scripts", "python.exe")
SCRIPTS = paths.WINDOWS_USE

def list_scripts():
    fs = sorted([f for f in os.listdir(SCRIPTS) if f.endswith(".py")])
    pri = ["auto_outline.py","auto_review.py","gen_fuse2.py","mon_outline.py","rank2.py",
           "send_v5.py","send_b5.py","send_one.py","send_final.py"]
    head = [f for f in pri if f in fs]
    rest = [f for f in fs if f not in head and not f.startswith(("_","fix"))]
    return head + rest

def run_async(name, args_str, on_line, on_done):
    script = os.path.join(SCRIPTS, name)
    if not os.path.exists(script):
        on_done(f"脚本不存在: {script}"); return None
    cmd = [VENV_PY, script] + (args_str.split() if args_str else [])
    env = {**os.environ, "PYTHONIOENCODING":"utf-8","PYTHONUTF8":"1"}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="replace",
                             bufsize=1, cwd=SCRIPTS, env=env)
    return proc
