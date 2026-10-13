from pathlib import Path
import shutil

proj_root = Path(r"F:\赛马23环整合工作室\程序2改装版\output\女王归来_test")

# 保留 00_初始化 和 进度.json
keep = {"00_初始化", "进度.json"}

for item in proj_root.iterdir():
    if item.name in keep:
        print(f"保留：{item.name}")
        continue
    if item.is_dir():
        shutil.rmtree(item)
        print(f"删除：{item.name}/")
    else:
        item.unlink()
        print(f"删除：{item.name}")

# 但保留 split.json（P09 还没有，P10 需要）
# 不对，既然要从 P09 开始，都删掉，让 P09 重新产
print("\n=== 清理完成 ===")
