import os, json
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]

sz = {}
for p in P:
    d = os.path.join(R, p, "产出", "章纲轮")
    total = sum(os.path.getsize(os.path.join(d,f)) for f in os.listdir(d) if f.endswith(".md") and "总稿" not in f)
    sz[p] = total / 1024
    print(f"{p:12} {sz[p]:6.1f} KB")

print()
# 分组：每批 ≤60 KB
LIMIT = 60.0
assign = {}
total_batches = 0
for me in P:
    others = [x for x in P if x != me]
    items = sorted(others, key=lambda x: -sz[x])
    bins = []
    for it in items:
        placed = False
        for b in bins:
            if b["sum"] + sz[it] <= LIMIT:
                b["items"].append(it); b["sum"] += sz[it]; placed = True; break
        if not placed:
            bins.append({"items":[it], "sum":sz[it]})
    assign[me] = [b["items"] for b in bins]
    total_batches += len(bins)
    print(f"{me}: {len(bins)} 批")
    for i, b in enumerate(bins, 1):
        print(f"  批{i}: {' + '.join(b)}  ({sum(sz[x] for x in b):.1f} KB)")

out = os.path.join(R, "资料", "指令", "章纲轮评审_分配.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(assign, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n共 {total_batches} 批，分配表: {out}")
