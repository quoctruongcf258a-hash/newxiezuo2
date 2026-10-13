# fix_ret_check.py — run_task CDP 分支判断返回值，失败不再 return True
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\_scratch\orchestrator.py")
text = TARGET.read_text(encoding="utf-8")

OLD = '''            r = _cdp_send(label, prompt)
            print(f"[CDP] 返回：{r}")
            return True
        except Exception as e:                 # noqa: BLE001
            print(f"[CDP 失败] {e}，回退 windows_use")
'''

NEW = '''            r = _cdp_send(label, prompt)
            print(f"[CDP] 返回：{r}")
            # 判断是否真发送成功：mix_send 返回值以 ✅ 开头为成功
            _rs = str(r or "")
            if _rs.lstrip().startswith("✅"):
                return True
            print("[CDP] 返回非成功标记，判定为失败")
            return False
        except Exception as e:                 # noqa: BLE001
            print(f"[CDP 失败] {e}，回退 windows_use")
'''

if "mix_send 返回值以 ✅ 开头为成功" in text:
    print("已改过")
elif OLD not in text:
    print("找不到 run_task CDP 分支锚点")
else:
    bak = TARGET.with_suffix(".py.bak_retcheck")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 补丁2：run_task 判断 CDP 返回值，失败不再当成功")