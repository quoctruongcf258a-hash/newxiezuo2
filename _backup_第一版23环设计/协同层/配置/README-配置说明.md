# 配置说明（协同层/配置）

## 一、主副本 vs 镜像（重要）

| 角色 | 位置 | 能不能手改 |
|---|---|---|
| **主副本（权威）** | `C:\mai\multi-ai-pipeline\windows-use\apps.json`、`roster.json` | ✅ 改这里 |
| **分发镜像（只读）** | 本目录 `apps.json`、`roster.json` | ❌ 不要改，会被覆盖 |

改动流程：
1. 改 `C:\mai\multi-ai-pipeline\windows-use\` 下的主副本；
2. 跑 `python C:\mai\multi-ai-pipeline\scripts\export_newskill.py`；
3. 本目录与整个「协同层」自动同步刷新。

> 为什么不做两份可写副本：双写必然漂移。全项目遵守**单权威副本纪律**。

## 二、改哪儿改什么

| 想改什么 | 改主副本的哪个块 |
|---|---|
| 参战 AI 名单 / 可选 AI 池 | `roster.json` 的 `registry` / `selection` / `presets` |
| 环节增删、调序、改模式 | `apps.json` 的 `phases`（`mode`: mesh/human/lock/storage） |
| 规划审核标准 | `apps.json` 的 `auditDirections` |
| 写作创作环境（29 环节） | `apps.json` 的 `writingEnvironment` |
| 写作审核标准（六要素） | `apps.json` 的 `sixElements`（含 `redLines`） |
| 润色标准与验收清单 | `apps.json` 的 `polishStandard` |
| 质检标准（20 节） | `apps.json` 的 `qcStandard` |
| 上架包装标准 | `apps.json` 的 `packagingStandard` |
| 番茄平台规则 | `apps.json` 的 `platform`、`complianceMode` |
| 投票与终审规则 | `apps.json` 的 `voting`、`stageFinalGates` |
| 每 10 章复检 / 问题定位卡 | `apps.json` 的 `periodicRecheck` |

## 三、几个开关

- `auditGates`：规划八方向审核闸总开关。关掉只跑主链路不做方向闸。
- `sixAudit`：写作六要素审核闸总开关。
- `complianceMode.default`：当前为 `aiDirect`（AI 直出·高风险·2026-10-02 作者裁定，目的是测试 AI 直出写作效果，作者按需参与关注与审核）；`aiAssist`（番茄合规·人为主笔）可随时切回。
- `periodicRecheck.trigger.every`：复检粒度，默认 10 章。

## 四、改完必须校验

```bash
python -c "import json;json.load(open(r'C:\mai\multi-ai-pipeline\windows-use\apps.json',encoding='utf-8'));print('OK')"
```
