# 表格刷新 → 60 秒
fp = r"C:\mai\multi-ai-pipeline\ui\ui_main.py"
with open(fp, "r", encoding="utf-8") as f:
    t = f.read()
t = t.replace("self.tbl_timer.start(5000)", "self.tbl_timer.start(60000)")
t = t.replace("self.tbl_timer.start(15000)", "self.tbl_timer.start(60000)")
t = t.replace("self.tbl_timer.start(2000)", "self.tbl_timer.start(60000)")
with open(fp, "w", encoding="utf-8") as f:
    f.write(t)

# 监控面板刷新 → 60 秒
fp2 = r"C:\mai\multi-ai-pipeline\ui\monitor_panel.py"
with open(fp2, "r", encoding="utf-8") as f:
    t2 = f.read()
t2 = t2.replace("self.timer.start(3000)", "self.timer.start(60000)")
t2 = t2.replace("self.timer.start(10000)", "self.timer.start(60000)")
with open(fp2, "w", encoding="utf-8") as f:
    f.write(t2)

print("OK 自动刷新都拉到 60 秒")
