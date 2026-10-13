import json
import urllib.request
import urllib.error
import sys
from pathlib import Path

APPS = Path(r"F:\赛马23环整合工作室\程序2改装版\windows-use\apps.json")
KEY_NAME = "workbuddy"

data = json.loads(APPS.read_text(encoding="utf-8-sig"))

def find_cfg(obj, name):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == name and isinstance(v, dict):
                return v
            r = find_cfg(v, name)
            if r:
                return r
    elif isinstance(obj, list):
        for item in obj:
            r = find_cfg(item, name)
            if r:
                return r
    return None

cfg = find_cfg(data, KEY_NAME)
if not cfg:
    print("apps.json 里没找到", KEY_NAME)
    sys.exit(1)

print("配置字段:", list(cfg.keys()))

base = cfg.get("base_url") or cfg.get("url") or cfg.get("endpoint")
key  = cfg.get("api_key") or cfg.get("key") or cfg.get("token")
model = cfg.get("model") or KEY_NAME

if not base or not key:
    print("base_url 或 key 缺失")
    sys.exit(1)

if not base.endswith("/chat/completions"):
    base = base.rstrip("/") + "/v1/chat/completions"

# 检查是否全是 ASCII，避免 latin-1 header 报错
def is_ascii(s):
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False

print("base:", base)
print("model:", model)
print("key 前6位:", key[:6] + "..." if len(key) > 6 else key)
print("key 是否纯ASCII:", is_ascii(key))
print("base 是否纯ASCII:", is_ascii(base))

if not is_ascii(key) or not is_ascii(base):
    print("警告：key 或 base 含非 ASCII 字符，HTTP header 会报 latin-1 错")
    sys.exit(2)

payload = {
    "model": model,
    "messages": [{"role": "user", "content": "只回复一个 JSON，不要额外文字：{\"ok\": true}"}],
    "max_tokens": 64,
}

req = urllib.request.Request(
    base,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
        print("HTTP", resp.status)
        print(body[:1000])
except urllib.error.HTTPError as e:
    print("HTTPError", e.code)
    print(e.read().decode("utf-8", errors="replace")[:1000])
except Exception as e:
    print("FAILED:", type(e).__name__, e)
