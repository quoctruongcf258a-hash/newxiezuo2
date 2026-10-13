# Windows-Use 自动化层 · 部署指南（四程序版）

> 本目录把「多 AI 流水线」从「你手动当信使」升级为「Windows-Use 自动驱动外部 AI 软件」。
> 所有 AI 调用走**外部软件**（豆包 / 元宝 / DeepSeek / Gemini / 通义 / Kimi…），不使用 WorkBuddy 内部多 Agent——符合设计铁律。
>
> 新模型：**程序零·阵容 + 四程序（规划/写作/润色/质检）+ 每程序一道终审闸 + 分块产出 + 过半投票 + 每 10 章连贯性复检**。
> 日常怎么用见 `README-怎么用.md`；规则与标准见 `apps.json` / `roster.json`，或分发副本 `G:\迅雷下载\novel_tools\万象宇宙\newskill\协同层\`。

---

## 0. 原理一句话

编排器 `orchestrator.py` 按 `apps.json`（流程与标准）+ `roster.json` + `today.json`（今日阵容）的配置，给 **Windows-Use**（看屏幕、控键鼠的 GUI 代理）派「自然语言任务」：

打开某个 AI → 粘贴 prompt + 输入 → 发送 → 等回复 → 复制 → 用记事本另存为到 `work/` 文件总线。

产出→盲审→拼接→投票的统计由 `voting.py` 在进程内完成，**无需外部脚本**。

→ 你不再手动搬运，整个过程在**你的 Windows 机器**上自动跑。

---

## 1. 环境要求

- Windows 10 / 11（Windows-Use 需要真实 GUI 与 UI Automation）
- Python 3.10+（建议 3.12）
- 本机已装好目标 AI 的**网页可访问**或**桌面客户端已安装**
- 目标 AI **已全部手动登录并保持会话**（Windows-Use 不负责登录）
- **GUI 需要 tkinter**：启动脚本会自动挑选带 tkinter 的解释器（详见第 4 节）

> ⚠️ 安全：Windows-Use 会真实移动鼠标、按键、改文件。官方强烈建议在 **Windows 沙盒 / 虚拟机**里跑。本机裸跑请自担风险。
> 运行期间**不要动鼠标键盘**。

---

## 2. 安装

把整个 `multi-ai-pipeline` 文件夹复制到本机（如 `D:\multi-ai-pipeline`），然后双击：

```
windows-use\install_fast.bat
```

脚本会在 `windows-use\.venv` 建虚拟环境并安装 `requirements.txt`。也可以手动：

```powershell
cd D:\multi-ai-pipeline\windows-use
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> `install_fast.bat` 会检测 tkinter（GUI 用）与 windows-use（引擎用），缺哪个会提示怎么补。

---

## 3. 准备 LLM（驱动 Windows-Use 的「大脑」）

Windows-Use 自己不生成决策，需要一个 LLM 告诉它「下一步点哪」。两种选：

### A. Ollama 本地（免费，默认）
1. 安装 Ollama，拉一个能跑 GUI 自动化的模型（越大越稳）：
   ```powershell
   ollama pull qwen2.5:14b
   ```
2. 默认即走 Ollama，可在环境变量覆盖模型：
   ```
   $env:WINDOWS_USE_PROVIDER="ollama"
   $env:OLLAMA_MODEL="qwen2.5:14b"
   ```
   > 本地小模型做 GUI 规划容易失误；若要稳定，建议用下面的云模型。
   > 注意：`mistralai` 包需锁 `<2`（与 windows-use 0.8.1 冲突）。

### B. 云模型（更稳，需 key）
```powershell
# Gemini（推荐，性价比高）
$env:WINDOWS_USE_PROVIDER="gemini"
$env:GOOGLE_API_KEY="你的key"
# 或在 windows-use/ 下建 .env 写 GOOGLE_API_KEY=...
```
也可改用 `openai` / `deepseek`（改 `WINDOWS_USE_PROVIDER` 与对应 key 即可，编排器已兼容）。

---

## 4. 启动（GUI 是主入口）

```
windows-use\run_gui.bat      ← 推荐：图形界面登记今日阵容
windows-use\run.bat          ← 命令行菜单（老手用）
```

**关于 Python 解释器**：GUI 需要 tkinter，而托管 Python 常不带；引擎需要 windows-use，装在 `.venv` 里。
`run_gui.bat` / `run.bat` 会自动按优先级挑选可用解释器，无需你手动指定。若两个都找不到会明确报错并给出补救命令。

---

## 5. 配置（三份文件，改哪个看这里）

| 文件 | 管什么 | 何时改 |
|------|--------|--------|
| `apps.json` | 四程序流程、各环节模式、各阶段审核标准（八方向/六要素/润色 28 项/质检 20 节）、番茄平台档案、投票与终审规则 | 想增删环节、改流程、改标准 |
| `roster.json` | 候选 AI 名单（35 项：国内网页 13 / 国内桌面 3 / 国外网页 13 / 国外桌面 6）、准入门槛、预设阵容、四层选角 | 想增减可选 AI、换预设、改角色适配 |
| `today.json` | **今日实际打开了哪些 AI**、什么形态（网页 URL / 桌面 exe 路径）、谁是拼接者 | **每次开跑前**（GUI 里点选即可） |

> `workbuddy` 不列入——设计铁律要求只用外部 AI。
>
> **单权威副本**：主副本在 `C:\mai\multi-ai-pipeline\windows-use\`；`newskill\协同层\配置\` 下是只读镜像。
> 改主副本后重跑 `python scripts\export_newskill.py` 刷新分发。

---

## 6. 试运行（不真驱动）

先 `--dry-run` 看会派发哪些任务，确认配置无误：

```powershell
cd windows-use
.venv\Scripts\python.exe orchestrator.py --check-session                    # 只校验今日阵容
.venv\Scripts\python.exe orchestrator.py --program 写作 --chapter 0057 --dry-run
```

---

## 7. 正式运行

```powershell
python orchestrator.py                              # 按 apps.json 全量跑
python orchestrator.py --program 写作 --chapter 0057 # 只跑写作程序第 0057 章
python orchestrator.py --program 质检 --chapter 0057 --phase 文风格式回查
python orchestrator.py --recheck --chapter 0030      # 手动触发每 10 章连贯性复检
python orchestrator.py --probe                       # 探测今日阵容可用性
```

观察 `work/` 下是否生成（按四程序分目录）：

```
work/规划/<环节>/versions/*.md          各 AI 的分块产出
work/规划/<环节>/reviews/*.json         盲审意见
work/规划/<环节>/phase_candidate.md     拼接后的环节候选稿
work/规划/章纲/phase_candidate.md       规划程序锁定产物
work/写作/ch0057/正文/…                 写作程序（六要素 6 段）
work/润色/…                             润色程序
work/质检/…                             质检程序 + 成书检验
work/library/第0057章.md                入库定稿
```

---

## 8. 可靠性与排错

- **盲审隔离**：评审必须只看到分配给自己的那一版。引擎已对每个评审新建独立对话；若手动复用同一窗口，务必确认开的是新聊天。
- **回复未落盘**：若某 `*.json` 没生成，多半是 Windows-Use 没点到「复制/保存」。看屏幕回放、调大 `wait_file` 超时、或换更强的 LLM。
- **网页版更稳**：相比桌面客户端 UI 自动化，网页版靠浏览器无障碍树更可靠。桌面 exe（如 Antigravity）路径需在 `today.json` 填对。
- **循环不收敛**：终审平票走「交叉提意见 + 综合改稿再投」，上限 2 轮；仍平票转人工裁决，不无限循环。
- **import 报错**：`windows-use` 不同 fork 导入路径不同（`windows_use.providers.*` vs `windows_use.llms.*`）。编排器已双路兼容；若仍报错，按你装的版本调整 `tasks.py` 顶部导入。
- **GUI 起不来**：`tkinter` 缺失。用系统 Python（`install_fast.bat` 会提示路径），或改装带 tkinter 的发行版。

---

## 9. 目录一览

```
multi-ai-pipeline/
├─ windows-use/
│  ├─ apps.json           # 四程序流程 + 各阶段审核标准 + 番茄档案 + 投票规则（主要改这里）
│  ├─ roster.json         # 候选 AI 名单 + 准入 + 预设 + 四层选角
│  ├─ today.json          # 今日阵容（每次开跑前由 GUI 写）
│  ├─ session.py          # 今日阵容解析（四层覆盖 × 今日交集）
│  ├─ tasks.py            # 把任务拼成 Windows-Use 自然语言 SOP（web/desktop 双路）
│  ├─ voting.py           # 投票统计 + 问题定位卡四件套校验
│  ├─ orchestrator.py     # 总控：四程序编排 + 复检触发
│  ├─ gui_launcher.py     # 今日阵容登记界面
│  ├─ run_gui.bat / run.bat / install_fast.bat
│  ├─ requirements.txt
│  ├─ README-怎么用.md     # 日常操作手册（先看这个）
│  └─ DEPLOY.md           # 本文件
├─ prompts/               # PROMPT_PRODUCE / REVIEW / MERGE / VOTE / HARD_RULES
├─ scripts/export_newskill.py  # 同步分发到 newskill
├─ 全员网格写作流水线-使用说明.md
└─ work/                  # 文件总线（跑起来才生成）
```

> `scripts/consolidate.py` / `validate.py` / `OPERATION.md` / `README.md` 为**旧固定角色模型**遗留，已被本版取代，仅作历史参考。
