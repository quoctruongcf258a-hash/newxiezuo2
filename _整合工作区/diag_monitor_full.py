from pathlib import Path

# ── 1. is_ai_busy 完整代码 ──
mix = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\mix_send.py")
lines = mix.read_text(encoding="utf-8", errors="ignore").splitlines()

print("=== is_ai_busy（第 828 行）===")
for j in range(827, min(882, len(lines))):
    print(f"{j+1:4d}| {lines[j]}")

print("\n\n=== wait_idle（第 882 行）===")
for j in range(881, min(940, len(lines))):
    print(f"{j+1:4d}| {lines[j]}")

# ── 2. monitor_busy.py 全文 ──
print("\n\n" + "="*70)
print("=== monitor_busy.py ===")
print("="*70)
mb = Path(r"F:\赛马23环整合工作室\_整合工作区\monitor_busy.py")
if mb.exists():
    text = mb.read_text(encoding="utf-8", errors="ignore")
    for i, ln in enumerate(text.splitlines()):
        print(f"{i+1:4d}| {ln}")

# ── 3. show_busy.py 全文 ──
print("\n\n" + "="*70)
print("=== show_busy.py ===")
print("="*70)
sb = Path(r"F:\赛马23环整合工作室\_整合工作区\show_busy.py")
if sb.exists():
    text = sb.read_text(encoding="utf-8", errors="ignore")
    for i, ln in enumerate(text.splitlines()):
        print(f"{i+1:4d}| {ln}")

# ── 4. check_busy.py 全文 ──
print("\n\n" + "="*70)
print("=== check_busy.py ===")
print("="*70)
cb = Path(r"F:\赛马23环整合工作室\_整合工作区\check_busy.py")
if cb.exists():
    text = cb.read_text(encoding="utf-8", errors="ignore")
    for i, ln in enumerate(text.splitlines()):
        print(f"{i+1:4d}| {ln}")

# ── 5. status.py 全文 ──
print("\n\n" + "="*70)
print("=== _scratch/status.py ===")
print("="*70)
st = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\status.py")
if st.exists():
    text = st.read_text(encoding="utf-8", errors="ignore")
    for i, ln in enumerate(text.splitlines()):
        print(f"{i+1:4d}| {ln}")
