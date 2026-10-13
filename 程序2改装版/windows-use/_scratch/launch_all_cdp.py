"""一键启动所有 AI（带 CDP 参数）"""
import subprocess, time, psutil, os

# 每个 AI 的 (进程名, exe路径, CDP端口)
ELECTRON_APPS = [
    ("CodeBuddy CN", r"C:\Users\Administrator\AppData\Local\Programs\CodeBuddy CN\CodeBuddy CN.exe", 9223),
    ("QoderCN",      r"C:\Users\Administrator\AppData\Local\Programs\QoderCN\QoderCN.exe",         9224),
    ("TRAE SOLO CN", r"G:\TRAE SOLO CN\TRAE SOLO CN.exe",                                            9225),
    ("qianwen",      r"C:\Program Files\QianwenApp\qianwen.exe",                                     9226),
    ("WorkBuddy",    r"F:\Program\WorkBuddy.exe",                                                    9227),
    ("ZCode",        r"C:\Program Files\ZCode\ZCode.exe",                                            9228),
]

EDGE = r"F:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

print("=" * 60)
print("启动所有 AI（带 CDP）")
print("=" * 60)

for proc, exe, port in ELECTRON_APPS:
    print(f"\n--- {proc} (端口 {port}) ---")
    # 关掉旧的
    n = 0
    for x in psutil.process_iter(['name','pid']):
        if (x.info['name'] or "").lower().startswith(proc.lower()):
            try:
                psutil.Process(x.info['pid']).terminate(); n += 1
            except: pass
    if n:
        print(f"  关闭了 {n} 个旧进程")
        time.sleep(2)

    if not os.path.exists(exe):
        print(f"  ❌ exe 不存在: {exe}"); continue

    subprocess.Popen([exe, f"--remote-debugging-port={port}", "--remote-allow-origins=*"])
    print(f"  🚀 启动（CDP {port}）")
    time.sleep(4)

print("\n--- Edge（网页 AI）---")
# Edge 关 + 带 CDP 启动
n = 0
for x in psutil.process_iter(['name','pid']):
    if (x.info['name'] or "").lower() == "msedge":
        try:
            psutil.Process(x.info['pid']).terminate(); n += 1
        except: pass
if n:
    print(f"  关闭了 {n} 个 Edge 进程")
    time.sleep(2)

if os.path.exists(EDGE):
    subprocess.Popen([EDGE, "--remote-debugging-port=9222", "--remote-allow-origins=*",
                      "--user-data-dir=C:\\mai\\edge_cdp",
                      "https://chat.deepseek.com"])
    print("  🚀 Edge 启动（CDP 9222）")
    time.sleep(5)
else:
    print(f"  ❌ Edge 不存在: {EDGE}")

print("\n等待所有窗口就绪（15 秒）...")
time.sleep(15)

# 验证
print("\n=== 验证 CDP 端口 ===")
import urllib.request
for port in [9222, 9223, 9224, 9225, 9226, 9227, 9228]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3) as f:
            n = len([t for t in __import__('json').load(f) if t.get("type")=="page"])
        print(f"  ✅ 端口 {port}  ({n} 个页面)")
    except:
        print(f"  ❌ 端口 {port}  连不上")
