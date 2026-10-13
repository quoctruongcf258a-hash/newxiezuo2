> ⚠️ **【历史版本·已弃用】**
> 本手册描述的是**旧「固定角色 + 人工信使」模型**（writers/merge_app/reviewers/polishers/qc_app，高/中/低分级）。
> 该模型已被 **四程序版**取代：全员网格、分块产出、过半投票、S/A/B/C 分级、问题定位卡、每 10 章复检。
> **日常操作请看 `windows-use/README-怎么用.md`**；完整流程看 `全员网格写作流水线-使用说明.md`。
> 本文件仅作历史参考保留，字段与流程均**不再适用**，请勿照此操作。

---

# 多 AI 协同 · 信使操作手册（旧版）

> 配套 `README.md`（架构）与 `prompts/`（各角色简报）。本手册只讲**具体操作**：
> 你现在打开哪个 AI 窗口、复制什么、粘贴到哪、存成哪个文件。
>
> 设计铁律（见 README）：**AI 一律走外部软件，本目录不调用任何内部 Agent；你当信使，脚本当离线调度器。**

---

## 0. 一句话机制

多个外部 AI **互不通信**，只通过 `work/` 下的**文件**对齐信息。
你 = 唯一的搬运工：把 A 的产出复制 → 粘贴给 B → 存成约定文件名。
`scripts/consolidate.py` + `validate.py` = 把多份盲审 JSON 合并去重、判绿/红、写台账。

```
AI-写1 ─┐
AI-写2 ─┼─(你搬运草稿)─▶ merged_draft.md ─┬─▶ AI-审1 ─┐
AI-写3 ─┘                                │           ├─(你存JSON)─▶ consolidate.py ─▶ 判定
                                        └─▶ AI-审2 ─┘                  │
                                                                      ▼
                                                            validate.py → fail循环 / pass定稿
```

---

## 1. 准备清单

- [ ] 几个外部 AI 聊天窗口（Claude / GPT / 通义 / Kimi……随意；同一家开多个会话也行）
- [ ] 本机 `multi-ai-pipeline/work/` 文件夹
- [ ] 本机 Python（跑 consolidate / validate，脚本离线不联网）

---

## 2. 文件名「总线协议」（AI 之间靠这个对齐）

| 文件 | 谁写 | 谁读 | 说明 |
|------|------|------|------|
| `work/outline.md` | 你 | 写作 AI | 同一份大纲，多写作 AI 共写 |
| `work/drafts/draft_k.md` | 你（存写作 AI 产出） | 整合 AI | 第 k 个写作 AI 的稿 |
| `work/merged_draft.md` | 你（存整合 AI 产出） | 盲审 AI / 润色 AI / QC AI | **被审的单一稿** |
| `work/reviews/review_k.json` | 你（存盲审 AI 产出） | consolidate.py | 第 k 个盲审 AI，newskill issue schema |
| `work/polish/polish_k.md` | 你（存润色 AI 产出） | —— | 第 k 个润色 AI 的稿 |
| `work/reviews/qc_1.json` | 你（存 QC AI 产出） | 你（人工终检参考） | 交付前总检查清单 |
| `work/consolidated_review.json` | consolidate.py | validate.py | 汇总判定 |
| `work/final.md` | validate.py --final | —— | 定稿 |
| `work/ledger.md` | 脚本自动追加 | 你 | 复验台账（每轮记录） |

---

## 3. 分阶段操作（含每步「复制→粘贴→存盘」）

### 阶段 0 · 准备大纲
1. 把同一份大纲写进 `work/outline.md`。

### 阶段 1 · 多 AI 写作（扇出）
对第 k 个写作 AI（建议 2~3 个）：
1. 打开 AI-写k 窗口。
2. **复制** `prompts/PROMPT_WRITE.md` 全文 + `work/outline.md` 全文，粘贴给 AI-写k。
3. AI 产出一版草稿后，**全选复制**其纯文本回复。
4. **存为** `work/drafts/draft_k.md`（k = 1, 2, 3…）。

> 多个写作 AI 用不同窗口/不同家软件皆可，彼此看不到对方稿。

### 阶段 2 · 整合出完整版（汇聚）
1. 打开 AI-合 窗口。
2. **复制** `prompts/PROMPT_MERGE.md` + 全部 `draft_k.md` 内容，粘贴给 AI-合。
3. AI 产出完整版后，**存为** `work/merged_draft.md`。
   - 只改「怎么写」，不改剧情事实。

### 阶段 3 · 多 AI 盲审（扇出，关键：隔离）
对第 k 个盲审 AI：
1. 打开 **新的、独立的** AI-审k 窗口。
2. **复制** `prompts/PROMPT_REVIEW.md` + `work/merged_draft.md` 全文，粘贴给 AI-审k。
3. ⚠️ **不要**给盲审 AI 看任何 `draft_*` 或其他 `review_*`——它只审 merged_draft，这才是「盲审隔离」。
4. AI 输出 JSON 后，**存为** `work/reviews/review_k.json`（k = 1, 2…）。
   - 必须严格遵循 newskill issue schema（见 README 或 PROMPT_REVIEW.md）。

> 盲审窗口互相独立、互不可见，才能复现「多 AI 单独审核后汇总」。可多开标签同时跑。

### 阶段 4 · 汇总判定（脚本调度）
```powershell
cd multi-ai-pipeline
python scripts/consolidate.py     # 合并 work/reviews/review_*.json → consolidated_review.json + 台账
python scripts/validate.py        # 读汇总，判绿/红 + 下一步 + 台账
```
- **fail** → 拿问题清单回 **阶段 2** 让整合 AI 按问题重改 → 再走 **阶段 3** 盲审 → 再 consolidate（循环）。
- **pass** → 进入阶段 5。

### 阶段 5 · 多 AI 润色（扇出）
对第 k 个润色 AI：
1. **复制** `prompts/PROMPT_POLISH.md` + `work/merged_draft.md`，粘贴给 AI-润k。
2. 产出后 **存为** `work/polish/polish_k.md`。
3. 人工比选各润色版，挑一版覆盖回 `work/merged_draft.md`（或取共识部分）。

### 阶段 6 · 终检定稿
1. 打开 AI-QC 窗口，**复制** `prompts/PROMPT_QC.md` + `work/merged_draft.md`，粘贴。
2. 产出 **存为** `work/reviews/qc_1.json`（人工终检参考）。
3. 确认无误后落定稿：
   ```powershell
   python scripts/validate.py --final   # 拷贝 merged_draft.md → final.md，台账追加
   ```

---

## 4. 为什么这算「多 AI 协同」

- **共识层 = 文件总线 + 结构化 JSON schema**：每个 AI 只干一件事，靠约定文件名和 newskill issue schema 对齐，不靠互相直连。
- **合并层 = consolidate.py**：把 N 份盲审按 `类别|位置|证据` 指纹去重、保留最高严重度、记录 `reported_by`，得到一份「多 AI 共识判定」。
- **状态传递 = consolidated_review.json + ledger.md**：下一轮改写 AI 靠这份综合判定知道要改什么，不靠 AI 间对话。

---

## 5. 提速与避坑

- **固定命名**：`draft_1 / review_1 / polish_1` 一路编号，别用中文或时间戳，便于脚本 glob 与人工核对。
- **盲审隔离是灵魂**：盲审窗口绝不要喂 draft 或其他 review，否则「多 AI 单独审核」退化成「串供」。
- **台账可回溯**：`ledger.md` 自动累积每轮 fail/pass 与问题数，多轮循环时一眼看清收敛情况。
- **脚本只动文件不动正文**：consolidate/validate 绝不改写你的稿，可放心反复跑。
- **换任何外部 AI 都不影响总线**：总线是文件 + newskill 规则，不是某个具体 AI。

---

## 6. 最小跑通示例（用自带 demo）

目录里已带 demo（`outline.md` / `drafts/draft_1.md` / `reviews/review_1.json` / `review_2.json` / `polish/polish_1.md`）。
想先看脚本怎么动，直接：
```powershell
cd multi-ai-pipeline
python scripts/consolidate.py
python scripts/validate.py
```
会看到：2 份盲审 → 去重 3 条（1 高/1 中/1 低），翻案句式红线被双抓合并，总判定 fail。
（跑完会生成 `consolidated_review.json` 与 `ledger.md`，验证完可删，留干净骨架。）
