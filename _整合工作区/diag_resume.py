from pathlib import Path

root = Path(r"F:\赛马23环整合工作室\程序2改装版")

# ── 1. 找 UI 相关文件 ──
print("=== UI 相关文件 ===")
for p in root.rglob("*.py"):
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    rel = str(p.relative_to(root))
    if any(k in rel.lower() for k in ["app/", "ui", "gui", "panel", "monitor", "main"]):
        print(f"  {rel}")

# ── 2. 找断点续跑/进度检测相关代码 ──
print("\n=== 含 断点/续跑/进度/resume/checkpoint 的代码 ===")
for p in root.rglob("*.py"):
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if any(k in text for k in ["断点", "续跑", "checkpoint", "resume", "继续后续", "上次完成", "检查完成"]):
        rel = str(p.relative_to(root))
        print(f"\n  📄 {rel}")
        # 打印含关键词的行
        for i, ln in enumerate(text.splitlines()):
            if any(k in ln for k in ["断点", "续跑", "checkpoint", "resume", "继续后续", "上次完成", "检查完成"]):
                print(f"     {i+1:4d}| {ln.strip()[:100]}")

# ── 3. app 目录结构 ──
print("\n\n=== app/ 目录 ===")
app_dir = root / "app"
if app_dir.exists():
    for p in sorted(app_dir.rglob("*")):
        if p.is_file() and p.suffix in (".py", ".json", ".md"):
            print(f"  {p.relative_to(app_dir)}")

# ── 4. 找 UI 中"选择 AI 数量"的地方 ──
print("\n\n=== 含 选择/指派 AI 数量的代码 ===")
for p in root.rglob("*.py"):
    if ".venv" in str(p) or "site-packages" in str(p):
        continue
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if "stage_assign" in text.lower() or "load_stage_assignments" in text or "steps" in text and "blocks" in text:
        rel = str(p.relative_to(root))
        print(f"  📄 {rel}")

# ── 5. load_stage_assignments 函数 ──
print("\n\n=== load_stage_assignments 函数 ===")
orch = root / "windows-use" / "_scratch" / "orchestrator.py"
if orch.exists():
    lines = orch.read_text(encoding="utf-8", errors="ignore").splitlines()
    for i, ln in enumerate(lines):
        if "def load_stage_assignments" in ln:
            for j in range(i, min(i+60, len(lines))):
                print(f"  {j+1:4d}| {lines[j]}")
            break
