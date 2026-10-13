# patch_write_proj.py — set_project_name 里加"写项目名到文件"
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")

OLD = '''    def set_project_name(self, name):
        """把当前项目名称显示到每个环节页顶部（环节窗口上方）。"""
        for lbl in getattr(self, "proj_name_labels", []):
            lbl.setText(f"📁 当前项目：{name}" if name else "")
'''

NEW = '''    def set_project_name(self, name):
        """把当前项目名称显示到每个环节页顶部（环节窗口上方）。"""
        for lbl in getattr(self, "proj_name_labels", []):
            lbl.setText(f"📁 当前项目：{name}" if name else "")
        # _PROJ_TO_FILE：把项目名写到文件，供 orchestrator 读
        try:
            import json as _json
            _p = paths.join("work", "collab", "current_project.json")
            import os as _os
            _os.makedirs(_os.path.dirname(_p), exist_ok=True)
            with open(_p, "w", encoding="utf-8") as _f:
                _json.dump({"project": name or ""}, _f, ensure_ascii=False, indent=2)
            self.log_line(f"💾 已记录当前项目：{name}")
        except Exception as _e:
            try:
                self.log_line(f"⚠ 写 current_project.json 失败：{_e}")
            except Exception:
                pass
'''

text = TARGET.read_text(encoding="utf-8")

if "_PROJ_TO_FILE" in text:
    print("已打过补丁")
elif OLD not in text:
    print("找不到 set_project_name 锚点，请检查文件内容")
else:
    bak = TARGET.with_suffix(".py.bak_projfile")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("✔ 已给 set_project_name 加写文件逻辑")