import os, subprocess
E = r"F:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
print("路径存在:", os.path.exists(E))
print("是文件:", os.path.isfile(E) if os.path.exists(E) else "N/A")
print("F 盘可访问:", os.path.exists("F:\\"))
if os.path.exists(E):
    print("大小:", os.path.getsize(E))

# 试启动（不带参数）
if os.path.exists(E):
    try:
        subprocess.Popen([E])
        print("✅ 启动成功（无参数）")
    except Exception as ex:
        print("❌ 启动失败:", ex)

    # 试带参数
    try:
        subprocess.Popen([E, "--remote-debugging-port=9222", "--user-data-dir=C:\\mai\\edge_cdp", "https://chat.deepseek.com"])
        print("✅ 启动成功（带参数）")
    except Exception as ex:
        print("❌ 带参数启动失败:", ex)
