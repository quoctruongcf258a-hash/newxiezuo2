# diag_session.py — 看 session 里实际参与者
import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch")
import session as S

roster = S.load_roster()
today = S.load_today()
sess = S.resolve(roster, today, program="写作", phase="W0_细纲分析")

print("=== participants ===")
for p in sess["participants"]:
    print(f"  key={p.get('key')!r}  label={p.get('label')!r}  cdpPort={p.get('cdpPort')}")
print()
print("=== merge_app ===")
m = sess.get("merge_app")
print(f"  {m.get('label') if m else None}")
print()
print(f"共 {len(sess['participants'])} 个参与者")