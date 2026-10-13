import sys, json
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")

print("=" * 70)
print(" CDP 端口检查（4 个 AI 是否在线）")
print("=" * 70)
ports = {
    "deepseek": 9222, "codebuddy": 9223, "quest": 9224,
    "doubao": 9225, "qianwen": 9226, "workbuddy": 9227, "zcode": 9228,
}
for name, port in ports.items():
    try:
        with urlopen(f"http://127.0.0.1:{port}/json", timeout=2) as f:
            pages = [t for t in json.load(f) if t.get("type") == "page"]
        if pages:
            title = pages[0].get("title", "")[:40]
            print(f"  ✅ {name:12} :{port}  [{title}]")
        else:
            print(f"  ⚠️  {name:12} :{port}  无页面")
    except Exception as e:
        print(f"  ❌ {name:12} :{port}  连不上（{type(e).__name__}）")

print()
print("=" * 70)
print(" 00_初始化 文件检查")
print("=" * 70)
init_dir = proj_root / "00_初始化"
must_have = ["项目信息.json"]
nice_have = ["用户输入.md"]
for f in must_have:
    p = init_dir / f
    ok = p.exists() and p.stat().st_size > 0
    print(f"  {'✅' if ok else '❌'} {f}  ({p.stat().st_size if p.exists() else 0}B)")
for f in nice_have:
    p = init_dir / f
    ok = p.exists() and p.stat().st_size > 0
    print(f"  {'✅' if ok else '⚠️ '} {f}  ({p.stat().st_size if p.exists() else 0}B)")

if (init_dir / "项目信息.json").exists():
    info = json.loads((init_dir / "项目信息.json").read_text(encoding="utf-8"))
    print(f"\n  项目名称：{info.get('项目名称')}")
    print(f"  章节数：{info.get('章节数')}")
    print(f"  人物列表：{info.get('人物设计列表')}")

print()
print("=" * 70)
print(" 进度.json 检查")
print("=" * 70)
pj = proj_root / "进度.json"
if pj.exists():
    prog = json.loads(pj.read_text(encoding="utf-8"))
    print(f"  ✅ 当前阶段：{prog.get('当前阶段')} / {prog.get('总阶段数')}")
    for s in (prog.get("阶段列表") or [])[:3]:
        print(f"      阶段{s.get('阶段号')}：{s.get('起章')}-{s.get('止章')} 章")
else:
    print(f"  ❌ 进度.json 不存在，需先跑 init_progress_v2.py")

print()
print("=" * 70)
print(" split.json 检查（级联输入）")
print("=" * 70)
# 规划阶段的 split.json
for split_name in ["全书结构", "分卷结构", "粗纲规划"]:
    p = proj_root / "01_规划" / split_name / "split.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        items = d.get("列表") or []
        print(f"  ✅ {split_name}/split.json  ({len(items)} 项)")
    else:
        print(f"  ❌ {split_name}/split.json 不存在")

print()
print("=" * 70)
print(" mix_send 模块检查")
print("=" * 70)
try:
    from mix_send import is_ai_busy, wait_idle, check_running, send
    print("  ✅ mix_send 导入成功")
    for ai in ["workbuddy", "doubao", "quest", "gemini"]:
        try:
            busy = is_ai_busy(ai)
            print(f"  {ai:12}: {'忙' if busy else '闲'}")
        except Exception as e:
            print(f"  {ai:12}: err({e.__class__.__name__})")
except Exception as e:
    print(f"  ❌ 导入失败：{e}")

print()
print("=" * 70)
print(" 快速总结")
print("=" * 70)
print("""
如果上面都是 ✅：
  1. 所有 AI 在线
  2. 00_初始化 数据齐全
  3. 进度.json 存在
  4. split.json 存在（可能只跑了规划阶段的部分环节）
  5. mix_send 可用

如果某些是 ❌，先补那些，再真跑。
""")
