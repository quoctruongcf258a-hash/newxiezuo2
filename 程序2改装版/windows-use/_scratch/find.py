import os, time
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
now = time.time()
print("最近 30 分钟内生成/改动的 .md 文件：")
for dp, _, fs in os.walk(R):
    for fn in fs:
        if not fn.endswith(".md"): continue
        fp = os.path.join(dp, fn)
        try: m = os.path.getmtime(fp)
        except: continue
        if now - m < 1800:
            rel = fp.replace(R, "")
            ago = int((now - m) / 60)
            print(f"  [{ago:>3}分钟前] {rel}  ({os.path.getsize(fp)} B)")
