# backend_orchestrator.py — 多 AI 协作流水线 · 纯后台 API 高速直连总控
# 继承并保留 orchestrator.py 的全部四大程序、23 环逻辑、盲审、择优与投票规则，
# 将前端图形 GUI (windows-use 击键) 彻底替换为 后台 API 静默直连！

import os
import sys
import re
import json
import urllib.request
import urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import orchestrator as orch

def extract_prompt_and_target(task_text: str):
    """从派发任务说明中解析出真正的 Prompt 与目标保存路径。"""
    # 提取 Prompt 内容
    prompt_match = re.search(r"=====\s*指令开始\s*=====\s*(.*?)\s*=====\s*指令结束\s*=====", task_text, re.DOTALL)
    prompt = prompt_match.group(1).strip() if prompt_match else task_text

    # 提取目标保存路径
    path_match = re.search(r"路径填：\s*([^\r\n]+)", task_text)
    target_path = path_match.group(1).strip() if path_match else None

    return prompt, target_path

def call_llm_api_direct(prompt: str, model_name: str = "gemma4-e2b:latest") -> str:
    """通过本地 Ollama 后台端口 (http://localhost:11434) 静默请求回复。"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json.get("response", "").strip()
    except Exception as e:
        print(f"[API 错误] 直连 Ollama 服务失败: {e}")
        return ""

def api_run_task(agent, task_text, dry=False, title=""):
    print("\n" + "─" * 74)
    if title:
        print(f"[{title}]")
    print("─" * 74)

    if dry:
        print("[dry-run] 未实际驱动。")
        return True

    prompt, target_path = extract_prompt_and_target(task_text)

    if not target_path:
        print("⚠️ 未解析到输出保存路径，跳过。")
        return False

    print(f"🤖 [后台直连] 正在向 LLM 发送请求 → 目标保存: {target_path}")
    
    # 获取本地模型
    model_name = os.getenv("OLLAMA_MODEL", "gemma4-e2b:latest")
    reply = call_llm_api_direct(prompt, model_name=model_name)

    if reply:
        p = Path(target_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(reply, encoding="utf-8")
        print(f"✅ [后台直连] 成功！写入文件: {p.name} ({len(reply)} 字)")
        return True
    else:
        print("❌ [后台直连] 生成内容为空。")
        return False

# 替换原生 orchestrator 的 run_task
orch.run_task = api_run_task

if __name__ == "__main__":
    # 直接转发命令行参数给原版 main()
    orch.main()
