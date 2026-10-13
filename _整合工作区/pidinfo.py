import psutil
pids = [p.pid for p in psutil.process_iter(['name']) if (p.info['name'] or '').lower()=='python.exe']
for pid in pids:
    try:
        p = psutil.Process(pid)
        print("PID", pid)
        print("  exe :", p.exe())
        print("  cmd :", " ".join(p.cmdline())[:400])
        print("  cwd :", p.cwd())
        print("  mem :", round(p.memory_info().rss/1024/1024,1), "MB")
        print("  start:", p.create_time())
        print("-"*70)
    except Exception as e:
        print("PID", pid, "ERR", e)
