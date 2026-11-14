"""問題として成り立たない条件がないかを、問題データ全体で確認する（見つかったら、ビルドを失敗させる）。

確認の内容：
- 三角形の 3 辺（AB・BC・CA、「3 辺の長さが …」）が、三角形として成り立つか（2 辺の和 > 残りの辺）
- 三角形の 2 つの角の和が 180° 未満か
- 方べきの定理の問題で、PA < PB、PC < PD が成り立つか
- 4 択の選択肢に、数値として同じものがないか
- 円錐の母線が半径より長いか
- 個数・長さ・面積の答えが負になっていないか
- 図の問題の図ファイルが、実際に存在するか
"""
import json, os, re, sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ps = json.load(open(os.path.join(ROOT, "mathscreen", "Resources", "problems.json"), encoding="utf-8"))
MATH = ("elem", "junior", "math1a", "math2b", "math3c", "triv_math")
bad = []


def clean(t):
    return re.sub(r"\\mathrm\{(\w+)\}", r"\1", t).replace("$", "").replace("\\,", " ").replace("\\dfrac", "").replace("{", "").replace("}", "")


def num(s):
    s = s.replace("$", "").replace("\\dfrac", "").replace(" ", "").replace("−", "-")
    if re.fullmatch(r"-?\d+(\.\d+)?", s): return F(s)
    m = re.fullmatch(r"(-?\d+)/(\d+)", s)
    if m and int(m.group(2)): return F(int(m.group(1)), int(m.group(2)))
    return None


for p in ps:
    if p["category"] not in MATH: continue
    b, plain, pid = clean(p["body"]), p["plain"], p["id"]
    sides = {}
    for m in re.finditer(r"(AB|BC|CA|AC)\s*=\s*(\d+(?:\.\d+)?)", b):
        sides["".join(sorted(m.group(1)))] = float(m.group(2))
    if len(sides) == 3:
        v = sorted(sides.values())
        if v[0] + v[1] <= v[2]: bad.append((pid, "三角形が成り立たない", plain[:60]))
    m = re.search(r"3\s*辺(?:の長さが|が)\s*(\d+)[、,]\s*(\d+)[、,]\s*(\d+)", b)
    if m:
        v = sorted(map(int, m.groups()))
        if v[0] + v[1] <= v[2]: bad.append((pid, "3辺が三角形にならない", plain[:60]))
    if "三角形" in b and "外角" not in b and "sin" not in b and "cos" not in b:
        d = [int(x) for x in re.findall(r"(\d+)\s*(?:°|\^\\circ)", p["body"])]
        if len(d) >= 2 and ("残り" in b or "求め" in b) and sum(d[:2]) >= 180 and "内角の和" not in b:
            bad.append((pid, "三角形の角の和が 180° 以上", plain[:60]))
    m = re.search(r"PA = (\d+)、PB = (\d+)、PC = (\d+) のとき", plain)
    if m and "方べき" in p["title"]:
        pa, pb, pc = map(int, m.groups())
        if not (pa < pb) or (pa * pb) % pc or pa * pb // pc <= pc: bad.append((pid, "方べきの定理の条件", plain[:60]))
    ch = p.get("choices")
    if ch:
        vs = [num(c) for c in ch]
        if all(v is not None for v in vs) and len(set(vs)) < 4: bad.append((pid, "選択肢が数値として同じ", plain[:60]))
    r = re.search(r"半径\s*(\d+).*?母線(?:の長さが)?\s*(\d+)", plain)
    if r and int(r.group(2)) <= int(r.group(1)): bad.append((pid, "母線が半径以下", plain[:60]))
    if not ch and re.search(r"(長さ|面積|体積|何個|何人|何通り|何組|何度)", b) and p["answer"] < 0:
        bad.append((pid, "答えが負", plain[:60]))
    if p.get("figure") and not os.path.exists(os.path.join(ROOT, "mathscreen", "Resources", "figures", p["figure"] + ".png")):
        bad.append((pid, "図のファイルがない", p["figure"]))

for b_ in bad[:50]: print("NG", *b_)
print(f"確認した数学の問題: {sum(1 for p in ps if p['category'] in MATH)} 問 / 成り立たない可能性のある問題: {len(bad)} 問")
sys.exit(1 if bad else 0)
