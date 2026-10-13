# gen_user_input.py — 从项目信息.json 生成 用户输入.md
import json
from pathlib import Path

BASE = Path(r"F:\赛马23环整合工作室\程序2改装版")
INIT = BASE / "output" / "女王归来_test" / "00_初始化"
info = json.loads((INIT / "项目信息.json").read_text(encoding="utf-8"))

def j(v):
    if isinstance(v, list):
        return " / ".join(str(x) for x in v)
    if isinstance(v, dict):
        return " / ".join(f"{k}:{v}" for k, v in v.items())
    return str(v) if v else ""

text = f"""# 用户输入（关键词 + 参考大纲）

## 关键词

- 频道：{j(info.get('频道'))}
- 题材：{j(info.get('题材'))}
- 细分：{j(info.get('细分'))}
- 章节数：{j(info.get('章节数'))}
- 主角性别：{j(info.get('主角性别'))}
- 主角性格：{j(info.get('主角性格'))}
- 感情线：{j(info.get('感情线'))}
- 金手指：{j(info.get('金手指'))}
- 角色模板：{j(info.get('角色模板'))}
- 配角数量：{j(info.get('配角数量'))}
- 额外想法：{j(info.get('额外想法'))}

## 参考大纲

{j(info.get('参考大纲')) if info.get('参考大纲') else '（用户未提供）'}
"""

out = INIT / "用户输入.md"
out.write_text(text, encoding="utf-8")
print(f"OK 已生成 {out}")
print()
print(text)