import os, json
R = r"C:\Users\Administrator\Desktop\新书\火影忍者\七人赛马"
P = ["CodeBuddy","QUEST","Doubao","Qianwen","WorkBuddy","ZCode"]
sz = {}
for p in P:
    d = os.path.join(R, p, "产出", "章纲轮")
    sz[p] = sum(os.path.getsize(os.path.join(d,f)) for f in os.listdir(d) if f.endswith(".md") and "总稿" not in f)/1024
    print(f"{p:12} {sz[p]:6.1f} KB")

LIMIT = 60.0
assign = {}
total = 0
for me in P:
    others = sorted([x for x in P if x != me], key=lambda x: -sz[x])
    bins = []
    for it in others:
        placed = False
        for b in bins:
            if b["s"] + sz[it] <= LIMIT:
                b["i"].append(it); b["s"] += sz[it]; placed = True; break
        if not placed: bins.append({"i":[it], "s":sz[it]})
    assign[me] = [b["i"] for b in bins]
    total += len(bins)

print()
for me, bins in assign.items():
    print(f"{me} ({len(bins)} 批)")
    for i, items in enumerate(bins, 1):
        print(f"  批{i}: {' + '.join(items)}  ({sum(sz[x] for x in items):.1f} KB)")

out = os.path.join(R, "资料", "指令", "章纲轮评审_分配.json")
json.dump(assign, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n共 {total} 批，分配表: {out}")
