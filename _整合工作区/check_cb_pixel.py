import sys
sys.path.insert(0, r"F:\赛马23环整合工作室\程序2改装版\windows-use")
from mix_send import _get_pixel

for pt in [(1833, 864), (1830, 865), (1836, 862), (1831, 866)]:
    rgb = _get_pixel(*pt)
    print(f"{pt}  ->  {rgb}")
