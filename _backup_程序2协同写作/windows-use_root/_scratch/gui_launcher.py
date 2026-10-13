# gui_launcher.py — 多 AI 协作写作流水线 · 今日阵容登记台
#
# 双击 run_gui.bat 打开。它解决一个现实问题：
#   你每天打开、能用的 AI 不一定一样（有的网页、有的桌面端、有的没登、有的额度满）。
#   所以每次开跑前先在这里登记「今天实际打开了哪些、分别是什么形态」，
#   程序据此合成阵容，再交给 orchestrator 去驱动。
#
# 三个页签：
#   ① 今日阵容  —— 勾选今天开着的 AI，核对形态（网页/桌面）与地址/路径
#   ② 运行设置  —— 选动作（校验/探测/跑某程序/复检）+ 章号 + 回改轮数
#   ③ 说明      —— 操作顺序与注意事项
#
# 登记结果写入 windows-use/today.json，与 apps.json（长期配置）、roster.json（候选池）分离。

import json
import subprocess
import sys
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    sys.stderr.write("tkinter 不可用：本环境 Python 未带 GUI 库。请改用 run.bat（命令行菜单）。\n")
    sys.exit(1)

HERE = Path(__file__).resolve().parent
APPS_JSON = HERE / "apps.json"
ROSTER_JSON = HERE / "roster.json"
TODAY_JSON = HERE / "today.json"
ORCH = HERE / "orchestrator.py"
SESSION = HERE / "session.py"
VENV_PY = HERE / ".venv" / "Scripts" / "python.exe"

FORMS = ["web", "desktop"]
ACK = ["校验阵容", "探测可用", "跑规划", "跑写作", "跑润色", "跑质检", "手动复检"]
PROGRAM_OF = {
    "跑规划": "规划", "跑写作": "写作", "跑润色": "润色", "跑质检": "质检",
}


def py_exe():
    return str(VENV_PY) if VENV_PY.exists() else sys.executable


def load_json(p, default=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:                                  # noqa: BLE001
        return default


def save_json(p, data):
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("多 AI 协作写作流水线 · 今日阵容登记台")
        self.geometry("1080x720")
        self.minsize(900, 600)

        self.roster = load_json(ROSTER_JSON, {}) or {}
        self.cfg = load_json(APPS_JSON, {}) or {}
        self.today = load_json(TODAY_JSON, {}) or {}
        self.reg = {x["key"]: x for x in self.roster.get("registry", [])}

        # 行控件引用：key -> dict(var, form_var, target_var, row)
        self.rows = {}
        self._build()

    # ──────────────────────────── 界面 ────────────────────────────

    def _build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=6)
        self.tab_roster = ttk.Frame(nb)
        self.tab_run = ttk.Frame(nb)
        self.tab_help = ttk.Frame(nb)
        nb.add(self.tab_roster, text="  今日阵容  ")
        nb.add(self.tab_run, text="  运行设置  ")
        nb.add(self.tab_help, text="  说明  ")

        self._build_roster_tab()
        self._build_run_tab()
        self._build_help_tab()

    def _build_roster_tab(self):
        top = ttk.Frame(self.tab_roster)
        top.pack(fill="x", padx=10, pady=(10, 4))
        ttk.Label(top, text="勾选「今天已经打开并且可用」的 AI；形态与地址请按实际核对（桌面端要填 exe 路径）。",
                  font=(None, 10)).pack(side="left")

        pre = ttk.Frame(self.tab_roster)
        pre.pack(fill="x", padx=10, pady=4)
        ttk.Label(pre, text="快速套用预设:").pack(side="left")
        self.preset_var = tk.StringVar()
        names = [f"{p.get('key')} — {p.get('label')}" for p in self.roster.get("presets", [])]
        ttk.Combobox(pre, textvariable=self.preset_var, values=names, width=34,
                     state="readonly").pack(side="left", padx=6)
        ttk.Button(pre, text="套用", command=self.apply_preset).pack(side="left")
        ttk.Button(pre, text="全部取消", command=self.clear_all).pack(side="left", padx=6)
        ttk.Button(pre, text="只留已勾选", command=self.keep_checked).pack(side="left")

        # 表头
        head = ttk.Frame(self.tab_roster)
        head.pack(fill="x", padx=10, pady=(6, 0))
        for txt, w in (("今天打开", 9), ("AI", 20), ("厂商", 12), ("形态", 10),
                       ("地址 / 可执行路径", 58), ("", 8)):
            ttk.Label(head, text=txt, font=(None, 9, "bold"), width=w).pack(side="left")

        # 滚动列表
        wrap = ttk.Frame(self.tab_roster)
        wrap.pack(fill="both", expand=True, padx=10, pady=4)
        canvas = tk.Canvas(wrap, highlightthickness=0)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        opened = {x["key"]: x for x in (self.today.get("opened") or [])}
        for i, entry in enumerate(self.roster.get("registry", [])):
            key = entry["key"]
            cur = opened.get(key)
            chk = tk.BooleanVar(value=bool(cur))
            form = tk.StringVar(value=(cur or {}).get("form")
                               or ("desktop" if "desktop" in entry.get("channel", []) and
                                   "web" not in entry.get("channel", []) else "web"))
            target = tk.StringVar(value=(cur or {}).get("target") or entry.get("target", ""))

            row = ttk.Frame(inner)
            row.pack(fill="x", pady=1)
            ttk.Checkbutton(row, variable=chk, width=6).pack(side="left")
            ttk.Label(row, text=f"{entry.get('label', key)}", width=20).pack(side="left")
            ttk.Label(row, text=entry.get("vendor", ""), width=12,
                      foreground="#777").pack(side="left")
            ttk.Combobox(row, textvariable=form, values=FORMS, width=9,
                         state="readonly").pack(side="left", padx=3)
            ttk.Entry(row, textvariable=target, width=52).pack(side="left", padx=2)
            ttk.Button(row, text="浏览", width=6,
                       command=lambda t=target: self.browse_target(t)).pack(side="left", padx=2)

            self.rows[key] = {"chk": chk, "form": form, "target": target,
                              "label": entry.get("label", key)}

        bot = ttk.Frame(self.tab_roster)
        bot.pack(fill="x", padx=10, pady=8)
        ttk.Label(bot, text="汇总拼接者（可由它汇总各版本，也可换）:").pack(side="left")
        self.merge_var = tk.StringVar(value=self.today.get("merge_app")
                                      or (self.roster.get("selection") or {}).get("merge_app", ""))
        self.merge_cb = ttk.Combobox(bot, textvariable=self.merge_var, width=20,
                                     state="readonly")
        self.merge_cb.pack(side="left", padx=6)
        ttk.Button(bot, text="按已勾选刷新拼接者候选", command=self.refresh_merge).pack(side="left")
        ttk.Button(bot, text="保存今日阵容", command=self.save_today).pack(side="right")
        self.refresh_merge()

    def _build_run_tab(self):
        f = ttk.Frame(self.tab_run)
        f.pack(fill="both", expand=True, padx=16, pady=16)

        ttk.Label(f, text="动作", font=(None, 10, "bold")).grid(row=0, column=0, sticky="w", pady=6)
        self.ack_var = tk.StringVar(value="校验阵容")
        ttk.Combobox(f, textvariable=self.ack_var, values=ACK, width=16,
                     state="readonly").grid(row=0, column=1, sticky="w")

        ttk.Label(f, text="章号", font=(None, 10, "bold")).grid(row=1, column=0, sticky="w", pady=6)
        self.chap_var = tk.StringVar(value="0057")
        ttk.Entry(f, textvariable=self.chap_var, width=18).grid(row=1, column=1, sticky="w")
        ttk.Label(f, text="（四位，如 0057；跑规划可留空）",
                  foreground="#777").grid(row=1, column=2, sticky="w", padx=8)

        ttk.Label(f, text="只跑某一环", font=(None, 10, "bold")).grid(row=2, column=0, sticky="w", pady=6)
        self.phase_var = tk.StringVar(value="（全部）")
        self.phase_cb = ttk.Combobox(f, textvariable=self.phase_var, width=22, state="readonly")
        self.phase_cb.grid(row=2, column=1, sticky="w")
        ttk.Button(f, text="刷新环节列表", command=self.refresh_phases).grid(row=2, column=2, sticky="w", padx=8)

        ttk.Label(f, text="出口闸回改轮数", font=(None, 10, "bold")).grid(row=3, column=0, sticky="w", pady=6)
        self.loop_var = tk.StringVar(value="2")
        ttk.Combobox(f, textvariable=self.loop_var, values=["1", "2", "3"], width=6,
                     state="readonly").grid(row=3, column=1, sticky="w")

        ttk.Label(f, text="省额度试跑", font=(None, 10, "bold")).grid(row=4, column=0, sticky="w", pady=6)
        self.once_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(f, text="每个环节只让 1 名 AI 产出（正式跑别勾，仅用来验证流程）",
                        variable=self.once_var).grid(row=4, column=1, columnspan=2, sticky="w")

        ttk.Separator(f, orient="horizontal").grid(row=5, column=0, columnspan=4,
                                                   sticky="ew", pady=12)

        ttk.Label(f, text="运行方式", font=(None, 10, "bold")).grid(row=6, column=0, sticky="w")
        self.mode_var = tk.StringVar(value="dry")
        ttk.Radiobutton(f, text="试运行（只打印任务，不操控 AI）", variable=self.mode_var,
                        value="dry").grid(row=6, column=1, sticky="w")
        ttk.Radiobutton(f, text="正式运行（真实操控 AI 窗口）", variable=self.mode_var,
                        value="live").grid(row=6, column=2, sticky="w")

        ttk.Separator(f, orient="horizontal").grid(row=7, column=0, columnspan=4,
                                                   sticky="ew", pady=12)
        btns = ttk.Frame(f)
        btns.grid(row=8, column=0, columnspan=4, sticky="w")
        ttk.Button(btns, text="开始运行", command=self.start).pack(side="left")
        ttk.Button(btns, text="打开工作目录", command=self.open_work).pack(side="left", padx=8)
        ttk.Button(btns, text="打开今日阵容文件", command=self.open_today).pack(side="left")

        ttk.Label(f, text="正式运行会真实操控你电脑上的 AI 窗口；运行期间请勿碰鼠标键盘。",
                  foreground="#c33").grid(row=9, column=0, columnspan=4, sticky="w", pady=(14, 0))
        self.refresh_phases()

    def _build_help_tab(self):
        txt = tk.Text(self.tab_help, wrap="word", font=("Microsoft YaHei", 11))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("1.0", HELP_TEXT)
        txt.configure(state="disabled")

    # ──────────────────────────── 交互 ────────────────────────────

    def browse_target(self, var):
        p = filedialog.askopenfilename(title="选择该桌面程序的可执行文件",
                                       filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")])
        if p:
            var.set(p.replace("/", "\\"))

    def apply_preset(self):
        sel = self.preset_var.get()
        if not sel:
            return
        key = sel.split(" — ")[0].strip()
        preset = next((p for p in self.roster.get("presets", []) if p.get("key") == key), None)
        if not preset:
            return
        want = set(preset.get("participants", []))
        for k, r in self.rows.items():
            r["chk"].set(k in want)
        if preset.get("merge_app"):
            self.merge_var.set(preset["merge_app"])
        messagebox.showinfo("已套用预设",
                            f"{preset.get('label')}\n\n"
                            f"参战：{', '.join(preset.get('participants', []))}\n"
                            f"拼接者：{preset.get('merge_app')}\n\n"
                            "请核对形态与地址是否与今天实际情况一致。")

    def clear_all(self):
        for r in self.rows.values():
            r["chk"].set(False)

    def keep_checked(self):
        for r in self.rows.values():
            r["form"].set(r["form"].get())

    def refresh_merge(self):
        checked = [k for k, r in self.rows.items() if r["chk"].get()]
        labels = [f"{k} — {self.rows[k]['label']}" for k in checked]
        self.merge_cb.configure(values=labels)
        cur = self.merge_var.get()
        if cur and not any(l.startswith(cur + " ") or l == cur for l in labels):
            # 拼接者必须是今天打开的一个；不在则回退到第一个
            self.merge_var.set(labels[0] if labels else "")

    def collect_opened(self):
        out = []
        for key, r in self.rows.items():
            if not r["chk"].get():
                continue
            e = self.reg.get(key, {})
            form = r["form"].get()
            out.append({
                "key": key,
                "label": e.get("label", key),
                "vendor": e.get("vendor", ""),
                "region": e.get("region", ""),
                "form": form,
                "target": r["target"].get(),
                "browser": e.get("browser", "EDGE"),
                "bestFor": e.get("bestFor", []),
            })
        return out

    def save_today(self):
        opened = self.collect_opened()
        if not opened:
            messagebox.showwarning("还没勾选", "请至少勾选 1 个今天打开的 AI。")
            return False
        mk = self.merge_var.get().split(" — ")[0].strip()
        save_json(TODAY_JSON, {
            "_说明": "今日阵容：本次运行实际打开的 AI（由 run_gui.bat 生成，可直接编辑）。",
            "opened": opened,
            "merge_app": mk,
        })
        return True

    def refresh_phases(self):
        ack = self.ack_var.get()
        prog = PROGRAM_OF.get(ack)
        vals = ["（全部）"]
        if prog:
            vals += [p["key"] for p in self.cfg.get("phases", []) if p["stage"] == prog]
        self.phase_cb.configure(values=vals)
        if self.phase_var.get() not in vals:
            self.phase_var.set("（全部）")

    def open_work(self):
        d = Path(__file__).resolve().parent.parent / "work"
        d.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(["explorer", str(d)])

    def open_today(self):
        if not TODAY_JSON.exists():
            self.save_today()
        subprocess.Popen(["notepad", str(TODAY_JSON)])

    def start(self):
        ack = self.ack_var.get()

        if ack in ("跑写作", "跑润色", "跑质检", "手动复检") and not self.chap_var.get().strip():
            messagebox.showerror("缺章号", f"「{ack}」需要填章号（四位，如 0057）。")
            return
        if not self.save_today():
            return

        args = [py_exe(), str(ORCH)]
        dry = self.mode_var.get() == "dry"

        if ack == "校验阵容":
            args.append("--check-session")
        elif ack == "探测可用":
            args.append("--probe")
        elif ack == "手动复检":
            args += ["--recheck", "--chapter", self.chap_var.get().strip()]
        else:
            args += ["--program", PROGRAM_OF[ack]]
            if self.chap_var.get().strip():
                args += ["--chapter", self.chap_var.get().strip()]
            if self.phase_var.get() != "（全部）":
                args += ["--phase", self.phase_var.get()]
            args += ["--loop", self.loop_var.get()]
            if self.once_var.get():
                args.append("--once")

        if dry and ack not in ("校验阵容", "探测可用"):
            args.append("--dry-run")

        try:
            subprocess.Popen(args, cwd=str(HERE), creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:                         # noqa: BLE001
            messagebox.showerror("启动失败", str(e))
            return

        self.iconify()
        messagebox.showinfo(
            "已启动",
            "已在独立窗口启动。\n\n"
            "· 试运行：窗口里会打印全部将派发的任务，检查无误后再用正式运行。\n"
            "· 正式运行：会真实操控 AI 窗口，运行期间请勿碰鼠标键盘。",
        )


HELP_TEXT = """【每天怎么用】

第一步  打开你打算用的 AI
        网页版就在浏览器里登录好；桌面端程序先手动启动好（并确认能正常提问）。

第二步  在本窗口「今日阵容」页勾选今天打开的 AI
        · 形态选对：网页 = web，桌面程序 = desktop
        · 桌面端要填对 exe 路径（点「浏览」选）
        · 网页端地址若与默认不同（如自建代理），直接改
        · 选好「汇总拼接者」——它负责把各版本按段落择优拼成一稿
        · 点「保存今日阵容」

第三步  切到「运行设置」
        · 先选「校验阵容」→ 试运行，确认人数 ≥ 2、拼接者在列、无跨厂告警
        · 可选「探测可用」核对每个 AI 是否真能提问（登录页/额度用完会被抓出来）

第四步  正式开跑
        · 规划：动作选「跑规划」，章号可留空（跑完整轮规划）
        · 写作：动作选「跑写作」，章号填 0057
        · 润色：动作选「跑润色」，章号填 0057
        · 质检：动作选「跑质检」，章号填 0057（每 10 章会自动追加连贯性复检）

【重要】
· 第一次务必先用「试运行」把任务清单打印出来看一遍，确认流程对再正式跑。
· 正式运行期间不要碰鼠标键盘——GUI 代理正在控制它们。
· 每个 AI 都会新开独立会话；盲审是隔离的，不要中途手动介入某个对话。

【文件在哪】
· 今日阵容：windows-use/today.json（本窗口生成，可手动编辑）
· 长期配置：windows-use/apps.json（程序、环节、审核标准）
· 候选池  ：windows-use/roster.json（可选 AI 名单、预设阵容）
· 产出目录：multi-ai-pipeline/work/（按程序/章号分目录）
· 入库成品：multi-ai-pipeline/work/library/
"""


if __name__ == "__main__":
    Launcher().mainloop()
