"""core/visualize.py
AI 能力表可视化：AI×维度 热力图、单 AI 雷达图（matplotlib Agg -> PNG bytes），
以及自包含 HTML 导出。供程序一结果竞技场与程序二复用。
"""
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def heatmap(matrix: dict, title: str = "AI × 维度 能力热力图") -> bytes:
    if not matrix:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "暂无数据", ha="center", va="center")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=110)
        plt.close(fig)
        return buf.getvalue()

    ais = list(matrix.keys())
    dims = list(next(iter(matrix.values())).keys())
    data = np.array([[matrix[a].get(d, 0) for d in dims] for a in ais])

    fig, ax = plt.subplots(
        figsize=(max(6, len(dims) * 1.1), max(3.5, len(ais) * 0.55)))
    im = ax.imshow(data, cmap="YlGnBu", vmin=0, vmax=10, aspect="auto")
    ax.set_xticks(range(len(dims)))
    ax.set_xticklabels(dims, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(range(len(ais)))
    ax.set_yticklabels(ais, fontsize=9)
    for i in range(len(ais)):
        for j in range(len(dims)):
            ax.text(j, i, data[i, j], ha="center", va="center",
                    color="black", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title(title, fontsize=12, color="#E5E7EB")
    fig.patch.set_facecolor("#0B1120")
    ax.set_facecolor("#0B1120")
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=110, bbox_inches="tight",
                facecolor="#0B1120")
    plt.close(fig)
    return buf.getvalue()


def radar(ai: str, dims_dict: dict) -> bytes:
    labels = list(dims_dict.keys())
    vals = list(dims_dict.values())
    if not labels:
        fig, ax = plt.subplots(figsize=(5, 5))
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=110)
        plt.close(fig)
        return buf.getvalue()

    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    vals2 = vals + vals[:1]
    angles2 = angles + angles[:1]

    fig, ax = plt.subplots(subplot_kw=dict(polar=True), figsize=(5, 5))
    ax.plot(angles2, vals2, color="#22D3EE", linewidth=2)
    ax.fill(angles2, vals2, alpha=0.25, color="#A78BFA")
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 10)
    ax.set_title(f"{ai} 能力雷达", fontsize=12, color="#E5E7EB")
    fig.patch.set_facecolor("#0B1120")
    ax.set_facecolor("#0B1120")
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=110, bbox_inches="tight",
                facecolor="#0B1120")
    plt.close(fig)
    return buf.getvalue()


def export_html(matrix: dict, ranking: list, crown: tuple, dims: list,
                path: str):
    head = "<th>AI</th>" + "".join(f"<th>{d}</th>" for d in dims)
    rows = ""
    for ai, row in matrix.items():
        cells = "".join(f"<td>{row.get(d, '-')}</td>" for d in dims)
        rows += f"<tr><td>{ai}</td>{cells}</tr>"
    rank_items = "".join(
        f"<li>#{i+1} &nbsp; <b>{a}</b> &nbsp; 均分 {s}</li>"
        for i, (a, s) in enumerate(ranking))
    crown_txt = "、".join(c for c in crown if c) or "无"

    html = f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>AI 能力表</title>
<style>
 body{{background:#0B1120;color:#E5E7EB;font-family:"Microsoft YaHei",sans-serif;padding:24px}}
 h1{{color:#22D3EE}} table{{border-collapse:collapse;margin:12px 0}}
 th,td{{border:1px solid #334155;padding:6px 12px;text-align:center}}
 th{{background:#1F2937;color:#A78BFA}}
 tr:nth-child(even){{background:#111827}}
 .crown{{color:#F59E0B;font-weight:700}}
 ol li{{margin:4px 0}}
</style></head><body>
<h1>AI 写作擂台 · 能力表</h1>
<h3>AI × 维度 得分矩阵</h3>
<table><tr>{head}</tr>{rows}</table>
<h3>累计排行榜</h3><ol>{rank_items}</ol>
<p class="crown">冠 / 亚 / 季军：{crown_txt}</p>
</body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
