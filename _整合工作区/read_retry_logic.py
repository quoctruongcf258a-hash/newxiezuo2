from pathlib import Path

target = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
lines = target.read_text(encoding="utf-8").splitlines()

# 读关键函数的完整代码
FUNCS = ["def wait_file", "def run_task", "def do_produce", "def run_gate",
         "def run_mesh_phase", "def _do_produce_split"]

for prefix in FUNCS:
    i_func = None
    for i, ln in enumerate(lines):
        if ln.startswith(prefix):
            i_func = i
            break
    if i_func is None:
        print(f"\n[--] 找不到 {prefix}")
        continue
    print(f"\n{'='*70}")
    print(f"=== {prefix} (第 {i_func+1} 行) ===")
    print(f"{'='*70}")
    end = i_func + 1
    while end < len(lines) and end < i_func + 200:
        if end > i_func + 1 and lines[end].startswith("def "):
            break
        end += 1
    for j in range(i_func, end):
        print(f"{j+1:4d}| {lines[j]}")
