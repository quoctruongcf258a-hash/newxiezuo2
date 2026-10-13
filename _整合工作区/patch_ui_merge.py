# patch_ui_merge.py — UI 加汇总者下拉 + 导出 today.json 按钮
import shutil
from pathlib import Path

TARGET = Path(r"F:\赛马23环整合工作室\程序2改装版\app\collab_app.py")


def main():
    print("=" * 60)
    print("patch_ui_merge")
    print("=" * 60)

    if not TARGET.exists():
        print(f"[错误] 找不到 {TARGET}")
        return

    text = TARGET.read_text(encoding="utf-8")

    if "_export_roster_to_cli" in text:
        print("[跳过] 已打过补丁")
        return

    bak = TARGET.with_suffix(".py.bak_merge")
    if not bak.exists():
        shutil.copy(TARGET, bak)
        print(f"已备份：{bak.name}")

    # ── 改动 1：在 tool_col.addWidget(self.shot_btn, 3, 1) 后面插入新行 ──
    a1 = "        tool_col.addWidget(self.ruler_btn, 3, 0)\n" \
         "        tool_col.addWidget(self.shot_btn, 3, 1)\n"
    b1 = a1 + \
        "        # 汇总者下拉（第 4 行整行）\n" \
        "        _lbl_merge = QLabel(\"汇总者:\")\n" \
        "        _lbl_merge.setStyleSheet(\"color:#cfcfcf;font-size:12px;\")\n" \
        "        tool_col.addWidget(_lbl_merge, 4, 0)\n" \
        "        self.merge_combo = QComboBox()\n" \
        "        self.merge_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)\n" \
        "        self.merge_combo.setStyleSheet(BTN_3D_QSS)\n" \
        "        self.merge_combo.setToolTip(\"指定拼接者：负责把各写手版本按块择优拼成候选稿\")\n" \
        "        tool_col.addWidget(self.merge_combo, 4, 1)\n" \
        "        # 导出按钮（第 5 行整行）\n" \
        "        _b_export = QPushButton(\"📤 导出运行中AI到命令行\")\n" \
        "        _b_export.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)\n" \
        "        _b_export.setStyleSheet(BTN_3D_QSS)\n" \
        "        _b_export.setToolTip(\"把 ai_apps.json 里『启用』且已连通（绿灯）的 AI 写成 today.json，供命令行引擎使用\")\n" \
        "        _b_export.clicked.connect(self._export_roster_to_cli)\n" \
        "        tool_col.addWidget(_b_export, 5, 0, 1, 2)\n"

    if a1 not in text:
        print("[失败] 改动1 锚点未找到：tool_col.addWidget(ruler/shot)")
        return
    text = text.replace(a1, b1, 1)
    print("✔ 改动1：已插入汇总者下拉 + 导出按钮")

    # ── 改动 2：加 _export_roster_to_cli 方法 ──
    # 插在 def log_line(self, s): 之前
    a2 = "    def log_line(self, s):\n"
    b2 = '''    def _export_roster_to_cli(self):
        """把 ai_apps.json 里启用的 AI 转成命令行引擎的 today.json。"""
        import json as _json
        try:
            from players import load_players
            apps = load_players() or []
        except Exception as e:
            self.log_line(f"❌ 读 players 失败：{e}")
            return

        enabled = [x for x in apps if x.get("启用") is not False]
        if not enabled:
            self.log_line("⚠ ai_apps.json 里没有启用中的 AI")
            return

        def _key(name):
            return (name or "").lower().replace(" ", "_")

        opened = []
        for x in enabled:
            name = x.get("名字", "")
            key = _key(name)
            typ = x.get("类型", "web")
            form = "desktop" if typ == "electron" else "web"
            target = x.get("exe") or x.get("url") or ""
            opened.append({
                "key": key,
                "label": name,
                "vendor": "",
                "region": "国内",
                "form": form,
                "target": target,
                "browser": x.get("浏览器", "msedge"),
                "cdpPort": x.get("cdp_port"),
                "cdpMatch": key,
            })

        # 写到 windows-use/_scratch/today.json
        scratch = os.path.join(os.path.dirname(paths.WINDOWS_USE), "_scratch")
        today_path = os.path.join(scratch, "today.json")
        merge_key = (self.merge_combo.currentText() or "").strip()
        merge_key = _key(merge_key) if merge_key else (opened[0]["key"] if opened else "")
        data = {
            "_说明": "今日阵容（由 UI 自动生成，勿手改）",
            "opened": opened,
            "merge_app": merge_key,
        }
        try:
            os.makedirs(scratch, exist_ok=True)
            with open(today_path, "w", encoding="utf-8") as f:
                _json.dump(data, f, ensure_ascii=False, indent=2)
            self.log_line(f"✅ 已导出 {len(opened)} 个 AI 到 today.json（汇总者={merge_key}）")
            for x in opened:
                self.log_line(f"   · {x['label']} → key={x['key']}, port={x['cdpPort']}")
        except Exception as e:
            self.log_line(f"❌ 写 today.json 失败：{e}")

    def _refresh_merge_combo(self):
        """刷新汇总者下拉（从 ai_apps.json 拿启用的 AI）。"""
        try:
            from players import load_players
            apps = load_players() or []
        except Exception:
            apps = []
        names = [x.get("名字", "") for x in apps if x.get("启用") is not False and x.get("名字")]
        cur = self.merge_combo.currentText() if hasattr(self, "merge_combo") else ""
        self.merge_combo.blockSignals(True)
        self.merge_combo.clear()
        self.merge_combo.addItems(names)
        if cur and cur in names:
            self.merge_combo.setCurrentText(cur)
        elif names:
            self.merge_combo.setCurrentIndex(0)
        self.merge_combo.blockSignals(False)

    def log_line(self, s):
'''
    if a2 not in text:
        print("[失败] 改动2 锚点未找到：def log_line")
        return
    text = text.replace(a2, b2, 1)
    print("✔ 改动2：已插入 _export_roster_to_cli / _refresh_merge_combo")

    # ── 改动 3：在 __init__ 里调 _refresh_merge_combo ──
    # 放在 self._sync_ais_to_players() 之后
    a3 = "        self._sync_ais_to_players()\n"
    b3 = ("        self._sync_ais_to_players()\n"
          "        self._refresh_merge_combo()\n")
    if a3 in text:
        text = text.replace(a3, b3, 1)
        print("✔ 改动3：启动时初始化汇总者下拉")

    TARGET.write_text(text, encoding="utf-8")
    print(f"\n✔ 已写回 {TARGET}")


if __name__ == "__main__":
    main()