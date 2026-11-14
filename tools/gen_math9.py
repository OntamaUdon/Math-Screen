"""これまで入っていなかった数学の単元の問題（2026年11月に追加）。

- 概数・単位量あたり・合同と対称・平行線と線分の比・箱ひげ図と標本調査・正弦定理と面積・三角形の五心・
  条件付き確率・n 進法・剰余の定理と解と係数・点と直線と領域・三角関数の合成・内分点とベクトル・
  確率分布と統計的な推測・媒介変数と極座標・いろいろな関数・グラフの凹凸と漸近線。
- 図が必要な問題は、matplotlib で PNG を作り、mathscreen/Resources/figures/ に置く（問題の figure にファイル名）。
  図は1問ずつなので、数字を変えて増やすのは、図がいらない問題と、記号だけの共通の図を使う問題に限る。
- どの問題も、答えをコードで計算して確かめる。
"""
import math
import os
import random
import itertools
from fractions import Fraction as F
import sympy as sp
from gen_problems import tex2plain
import gen_math7 as G7

R = random.Random(20261111)
OUT = []
_count = {}
_seen = set()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(ROOT, "mathscreen", "Resources", "figures")

CAT = dict(G7.CAT)
for u in "e_round e_unit e_shape".split(): CAT[u] = "elem"
for u in "m_parallel m_boxplot".split(): CAT[u] = "junior"
for u in "h_sine h_center h_condprob h_nbase".split(): CAT[u] = "math1a"
for u in "h_remainder h_line h_compose h_divpt h_statinf".split(): CAT[u] = "math2b"
for u in "h_curve h_func3 h_graph".split(): CAT[u] = "math3c"
RATE = {1: 7.4, 2: 5.4, 3: 3.7, 4: 2.0}

frac_tex, ab, poly, sg = G7.frac_tex, G7.ab, G7.poly, G7.sg


def add(unit, diff, title, body, ans, expl, choices=None, figure=None):
    if (unit, body, figure) in _seen: return False
    _seen.add((unit, body, figure))
    _count[unit] = _count.get(unit, 0) + 1
    p = dict(id=f"x9-{unit}-{_count[unit]}", category=CAT[unit], difficulty=diff, title=title, body=body,
             answer=ans, explanation=expl, plain=tex2plain(body), unit=unit, rate_hint=RATE[diff])
    if figure: p["figure"] = figure
    if choices is not None:
        labels = ["①", "②", "③", "④"]
        assert len(set(choices)) == 4 and 0 <= ans < 4
        p["choices"] = choices
        p["plain"] += "　" + "　".join(f"{labels[i]} {tex2plain(c)}" for i, c in enumerate(choices))
    else:
        assert isinstance(ans, int), (body, ans)
    OUT.append(p)
    return True


def choice(unit, diff, title, body, correct, wrongs, expl, figure=None):
    opts = [correct] + list(wrongs)
    R.shuffle(opts)
    return add(unit, diff, title, body, opts.index(correct), expl, opts, figure)


def fracq(unit, diff, title, body, f, expl, figure=None):
    f = F(f)
    if f <= 0 or f.denominator == 1: return False
    return add(unit, diff, title, body + "既約分数 $\\dfrac{p}{q}$ で表したとき、$p + q$ を答えよ。", ab(f), expl, figure=figure)


def make(n, fn, tries=3000):
    k = 0
    for _ in range(tries):
        if k >= n: break
        if fn(): k += 1
    assert k >= max(1, n * 6 // 10), (fn.__name__, k, n)


# ═════════ 図 ═════════
_plt = None


def plt():
    global _plt
    if _plt is None:
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib import font_manager
        import matplotlib.pyplot as p
        for f in ["/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"]:
            if os.path.exists(f):
                font_manager.fontManager.addfont(f)
                p.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
        _plt = p
    return _plt


INK = "#23263A"
ACC = "#2A9D8F"


def fig_save(name, draw, w=4.2, h=2.8):
    p = plt()
    os.makedirs(FIG_DIR, exist_ok=True)
    fig, ax = p.subplots(figsize=(w, h), dpi=150)
    ax.set_aspect("equal")
    ax.axis("off")
    draw(ax)
    fig.savefig(os.path.join(FIG_DIR, name + ".png"), facecolor="white", bbox_inches="tight", pad_inches=0.08)
    p.close(fig)
    return name


def poly_draw(ax, pts, close=True, **kw):
    xs = [q[0] for q in pts] + ([pts[0][0]] if close else [])
    ys = [q[1] for q in pts] + ([pts[0][1]] if close else [])
    ax.plot(xs, ys, color=kw.get("color", INK), lw=kw.get("lw", 2))


def label(ax, xy, text, dx=0, dy=0, size=13, color=INK):
    ax.text(xy[0] + dx, xy[1] + dy, text, ha="center", va="center", fontsize=size, color=color)


# ═════════ 小学：概数・単位量あたり・合同と対称 ═════════
def e_round_place():
    n = R.randint(10000, 999999); place, name = R.choice([(100, "百"), (1000, "千"), (10000, "一万")])
    if n < place * 10: return False
    v = int(F(n, place) + F(1, 2)) * place
    return add("e_round", 1, "四捨五入", f"{n} を四捨五入して、{name}の位までの概数にせよ。", v,
               f"{name}の位の 1 つ下の位を四捨五入する。答えは {v}。")


def e_round_top2():
    n = R.randint(1000, 99999)
    k = len(str(n)) - 2
    v = int(F(n, 10 ** k) + F(1, 2)) * 10 ** k
    return add("e_round", 1, "上から 2 けたの概数", f"{n} を四捨五入して、上から 2 けたの概数にせよ。", v,
               f"上から 3 けためを四捨五入する。答えは {v}。")


def e_round_range():
    c = R.randint(2, 9) * 1000 + R.choice([0, 500]); place = 100
    lo, hi = c - 50, c + 49
    which = R.choice(["最小", "最大"])
    return add("e_round", 2, "概数のもとの範囲", f"十の位を四捨五入すると {c} になる整数のうち、{which}のものはいくつか。", lo if which == "最小" else hi,
               f"十の位を四捨五入して {c} になる整数は、{lo} 以上 {hi} 以下。")


def e_round_estimate():
    a, b = R.randint(110, 980), R.randint(11, 98)
    ra = int(F(a, 10 ** (len(str(a)) - 1)) + F(1, 2)) * 10 ** (len(str(a)) - 1)
    rb = int(F(b, 10 ** (len(str(b)) - 1)) + F(1, 2)) * 10 ** (len(str(b)) - 1)
    return add("e_round", 2, "積の見積もり", f"${a} \\times {b}$ の積を、それぞれ上から 1 けたの概数にして見積もると、いくつになるか。", ra * rb,
               f"${a}$ は約 ${ra}$、${b}$ は約 ${rb}$。${ra} \\times {rb} = {ra * rb}$。")


def e_unit_crowd():
    a, s1, b, s2 = R.randint(12, 40), R.randint(6, 20), R.randint(12, 40), R.randint(6, 20)
    if F(a, s1) == F(b, s2): return False
    ans = 0 if F(a, s1) > F(b, s2) else 1
    return add("e_unit", 1, "こみぐあい", f"A の部屋は {s1} m² に {a} 人、B の部屋は {s2} m² に {b} 人いる。1 m² あたりの人数で比べると、こんでいるのはどちらか。",
               ans, f"A は $\\dfrac{{{a}}}{{{s1}}}$ 人、B は $\\dfrac{{{b}}}{{{s2}}}$ 人。大きい方がこんでいる。", ["A の部屋", "B の部屋", "同じ", "比べられない"])


def e_unit_density():
    area = R.randint(20, 300); d = R.randint(50, 900)
    return add("e_unit", 2, "人口密度", f"面積が {area} km²、人口が {area * d} 人の町の人口密度（1 km² あたりの人口）は何人か。", d,
               f"${area * d} \\div {area} = {d}$ 人。")


def e_unit_fuel():
    k, l = R.randint(8, 25), R.randint(2, 30)
    return add("e_unit", 1, "1 L で走る道のり", f"ガソリン 1 L で {k} km 走る車は、{k * l} km 走るのに何 L のガソリンを使うか。", l,
               f"${k * l} \\div {k} = {l}$ L。")


def e_unit_price():
    g1, p1, g2, p2 = R.choice([200, 300, 400, 500]), None, R.choice([150, 250, 600, 800]), None
    u1, u2 = R.randint(80, 300), R.randint(80, 300)
    if u1 == u2: return False
    p1, p2 = u1 * g1 // 100, u2 * g2 // 100
    if p1 * 100 != u1 * g1 or p2 * 100 != u2 * g2: return False
    return add("e_unit", 2, "100 g あたりのねだん", f"A の肉は {g1} g で {p1} 円、B の肉は {g2} g で {p2} 円。100 g あたりで安い方の、100 g あたりのねだんは何円か。", min(u1, u2),
               f"A は 100 g あたり {u1} 円、B は {u2} 円。安いのは {min(u1, u2)} 円。")


def shape_figs():
    for n in range(3, 9):
        def draw(ax, n=n):
            pts = [(math.cos(math.pi / 2 + 2 * math.pi * k / n), math.sin(math.pi / 2 + 2 * math.pi * k / n)) for k in range(n)]
            poly_draw(ax, pts)
            ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3)
        fig_save(f"fig_poly{n}", draw, 2.4, 2.4)
    names = {3: "正三角形", 4: "正方形", 5: "正五角形", 6: "正六角形", 7: "正七角形", 8: "正八角形"}
    for n in range(3, 9):
        add("e_shape", 1, "対称の軸の本数", f"図の{names[n]}は線対称な図形である。対称の軸は何本あるか。", n,
            f"正 $n$ 角形の対称の軸は $n$ 本。{names[n]}は {n} 本。", figure=f"fig_poly{n}")
        pt = n % 2 == 0
        add("e_shape", 2, "点対称かどうか", f"図の{names[n]}は、点対称な図形か。", 0 if pt else 1,
            "頂点の数が偶数の正多角形は点対称。奇数のときは点対称ではない。", ["点対称である", "点対称ではない", "線対称でも点対称でもない", "どちらともいえない"], figure=f"fig_poly{n}")


def e_scale_map():
    sc = R.choice([2500, 5000, 10000, 25000, 50000]); cm = R.randint(2, 12)
    return add("e_shape", 1, "縮図と縮尺", f"縮尺 $\\dfrac{{1}}{{{sc}}}$ の地図で {cm} cm の長さは、実際には何 m か。", sc * cm // 100,
               f"${cm} \\times {sc} = {sc * cm}$ cm $= {sc * cm // 100}$ m。") if (sc * cm) % 100 == 0 else False


def e_scale_tri():
    k = R.randint(2, 4); a = R.randint(2, 9)
    return add("e_shape", 1, "拡大図", f"三角形 ABC を {k} 倍に拡大した三角形 DEF をかいた。辺 AB が {a} cm のとき、AB に対応する辺 DE は何 cm か。", k * a,
               f"拡大図では、対応する辺の長さがすべて {k} 倍。${a} \\times {k} = {k * a}$ cm。")


# ═════════ 中学：平行線と線分の比・箱ひげ図と標本調査 ═════════
def parallel_figs():
    def tri(ax):
        A, B, C = (0.4, 2.2), (0, 0), (3, 0)
        t = 0.4
        D = (A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t)
        E = (A[0] + (C[0] - A[0]) * t, A[1] + (C[1] - A[1]) * t)
        poly_draw(ax, [A, B, C]); poly_draw(ax, [D, E], close=False, color=ACC)
        for P, s, dx, dy in [(A, "A", 0, .15), (B, "B", -.12, -.1), (C, "C", .12, -.1), (D, "D", -.15, 0), (E, "E", .15, 0)]:
            label(ax, P, s, dx, dy)
        ax.set_xlim(-.4, 3.4); ax.set_ylim(-.35, 2.5)
    fig_save("fig_tri_de", tri)

    def lines(ax):
        for y, s in [(2, "ℓ"), (1.2, "m"), (0, "n")]:
            ax.plot([-.3, 3.6], [y, y], color=INK, lw=1.6); label(ax, (3.8, y), s, size=12)
        ax.plot([0.3, 1.3], [2, 0], color=ACC, lw=2); ax.plot([1.6, 3.2], [2, 0], color=ACC, lw=2)
        for (x, y), s in [((0.3, 2), "A"), ((0.7, 1.2), "B"), ((1.3, 0), "C"), ((1.6, 2), "D"), ((2.24, 1.2), "E"), ((3.2, 0), "F")]:
            ax.plot([x], [y], "o", color=INK, ms=3); label(ax, (x, y), s, -.17, .14, 11)
        ax.set_xlim(-.4, 4); ax.set_ylim(-.3, 2.35)
    fig_save("fig_parallel3", lines)

    def bis(ax):
        A, B, C = (1.0, 2.0), (0, 0), (3.2, 0)
        D = (1.35, 0)
        poly_draw(ax, [A, B, C]); poly_draw(ax, [A, D], close=False, color=ACC)
        for P, s, dx, dy in [(A, "A", 0, .15), (B, "B", -.12, -.1), (C, "C", .12, -.1), (D, "D", 0, -.18)]:
            label(ax, P, s, dx, dy)
        ax.set_xlim(-.4, 3.6); ax.set_ylim(-.4, 2.3)
    fig_save("fig_bisector", bis)

    def mid(ax):
        A, B, C = (0.8, 2.2), (0, 0), (3, 0)
        M, N = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2), ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)
        poly_draw(ax, [A, B, C]); poly_draw(ax, [M, N], close=False, color=ACC)
        for P, s, dx, dy in [(A, "A", 0, .15), (B, "B", -.12, -.1), (C, "C", .12, -.1), (M, "M", -.18, 0), (N, "N", .18, 0)]:
            label(ax, P, s, dx, dy)
        ax.set_xlim(-.4, 3.4); ax.set_ylim(-.35, 2.5)
    fig_save("fig_midpoint", mid)


def m_par_de():
    a, b = R.randint(1, 5), R.randint(1, 5)
    if math.gcd(a, b) != 1: return False
    bc = (a + b) * R.randint(1, 6)
    de = F(bc * a, a + b)
    if de.denominator != 1: return False
    return add("m_parallel", 2, "平行線と線分の比", f"図で DE // BC、AD : DB = {a} : {b}、BC = {bc} のとき、DE の長さを答えよ。", int(de),
               f"三角形 ADE と ABC は相似で、相似比は AD : AB = {a} : {a + b}。DE $= {bc} \\times \\dfrac{{{a}}}{{{a + b}}} = {int(de)}$。", figure="fig_tri_de")


def m_par_three():
    ab_, bc_ = R.randint(2, 9), R.randint(2, 9); k = R.randint(1, 3)
    de, ef = ab_ * k, bc_ * k
    return add("m_parallel", 2, "3 本の平行線", f"図で ℓ // m // n のとき、AB = {ab_}、BC = {bc_}、DE = {de} である。EF の長さを答えよ。", ef,
               f"平行線にはさまれた線分の比は等しいので、AB : BC = DE : EF。${ab_} : {bc_} = {de} : x$ より $x = {ef}$。", figure="fig_parallel3")


def m_par_mid():
    bc = R.randint(3, 20) * 2
    return add("m_parallel", 1, "中点連結定理", f"図で M、N はそれぞれ辺 AB、AC の中点で、BC = {bc} である。MN の長さを答えよ。", bc // 2,
               f"中点連結定理より、MN // BC、MN $= \\dfrac{{1}}{{2}}$BC $= {bc // 2}$。", figure="fig_midpoint")


def m_par_bis():
    # 三角形が成り立つ（|AB − AC| < BC < AB + AC）ように BC を選び、BD が整数になる組だけを使う
    cands = [(a, b, bc) for a in range(3, 13) for b in range(3, 13) if a != b
             for bc in range(abs(a - b) + 1, a + b) if (bc * a) % (a + b) == 0]
    ab_, ac_, bc = R.choice(cands)
    bd = bc * ab_ // (ab_ + ac_)
    return add("m_parallel", 2, "角の二等分線と比", f"図で AD は角 A の二等分線で、AB = {ab_}、AC = {ac_}、BC = {bc} である。BD の長さを答えよ。", bd,
               f"角の二等分線の性質より BD : DC = AB : AC = {ab_} : {ac_}。BD $= {bc} \\times \\dfrac{{{ab_}}}{{{ab_ + ac_}}} = {bd}$。", figure="fig_bisector")


def quartiles(xs):
    xs = sorted(xs); n = len(xs)
    def med(v):
        m = len(v)
        return F(v[m // 2] + v[(m - 1) // 2], 2)
    lo, hi = xs[:n // 2], xs[(n + 1) // 2:]
    return med(lo), med(xs), med(hi)


def m_box_q():
    n = R.choice([7, 8, 9, 10, 11])
    xs = [R.randint(1, 40) for _ in range(n)]
    q1, q2, q3 = quartiles(xs)
    which = R.choice(["第 1 四分位数", "第 3 四分位数", "四分位範囲"])
    v = q1 if which == "第 1 四分位数" else q3 if which == "第 3 四分位数" else q3 - q1
    if v.denominator != 1: return False
    return add("m_boxplot", 2 if which == "四分位範囲" else 1, which, f"次の {n} 個のデータの{which}を答えよ。　{', '.join(map(str, xs))}", int(v),
               f"小さい順に {', '.join(map(str, sorted(xs)))}。中央値で前半・後半に分け、それぞれの中央値が第 1・第 3 四分位数。第 1 四分位数 {q1}、第 3 四分位数 {q3}。")


def box_figs():
    k = 0
    for _ in range(40):
        lo = R.randint(0, 20); q1 = lo + R.randint(4, 15); q2 = q1 + R.randint(2, 12); q3 = q2 + R.randint(2, 12); hi = q3 + R.randint(3, 15)
        k += 1
        name = f"fig_box{k}"

        def draw(ax, v=(lo, q1, q2, q3, hi)):
            ax.set_aspect("auto"); ax.axis("on")
            ax.plot([v[0], v[1]], [0, 0], color=INK, lw=1.8); ax.plot([v[3], v[4]], [0, 0], color=INK, lw=1.8)
            ax.add_patch(plt().Rectangle((v[1], -.3), v[3] - v[1], .6, fill=True, facecolor="#BFEFE8", edgecolor=INK, lw=1.8))
            ax.plot([v[2], v[2]], [-.3, .3], color=INK, lw=2)
            for e in (v[0], v[4]): ax.plot([e, e], [-.15, .15], color=INK, lw=1.8)
            for e in v: ax.text(e, .42, str(e), ha="center", va="bottom", fontsize=9, color=INK)
            ax.set_ylim(-.6, .6); ax.set_yticks([])
            ax.set_xticks(range(0, 101, 10)); ax.set_xlim(-2, max(60, v[4] + 5))
            ax.grid(axis="x", color="#D5DAE6", lw=.8); ax.set_axisbelow(True)
            for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
            ax.tick_params(labelsize=9)
        fig_save(name, draw, 4.4, 1.5)
        which = ["最小値", "第 1 四分位数", "中央値", "第 3 四分位数", "最大値", "範囲", "四分位範囲"][k % 7]
        val = {"最小値": lo, "第 1 四分位数": q1, "中央値": q2, "第 3 四分位数": q3, "最大値": hi, "範囲": hi - lo, "四分位範囲": q3 - q1}[which]
        add("m_boxplot", 1 if which in ("最小値", "中央値", "最大値") else 2, "箱ひげ図の読み取り", f"図はあるデータの箱ひげ図である（図の数は、ひげの端・箱の端・箱の中の線の値）。{which}を答えよ。", val,
            "箱の左端が第 1 四分位数、箱の中の線が中央値、箱の右端が第 3 四分位数、ひげの両端が最小値と最大値。範囲は最大値 − 最小値、四分位範囲は第 3 − 第 1 四分位数。", figure=name)
        if k >= 14: break


def m_sample():
    a, b = R.randint(30, 120), R.randint(30, 100)
    c = R.randint(3, 20)
    total = F(a * b, c)
    if total.denominator != 1: return False
    return add("m_boxplot", 2, "標本調査で全体を推定", f"池の魚に {a} 匹印をつけて戻した。数日後に {b} 匹とったら、印のついた魚が {c} 匹いた。池の魚はおよそ何匹と推定できるか。", int(total),
               f"標本の割合 $\\dfrac{{{c}}}{{{b}}}$ が全体の割合と同じと考える。$x \\times \\dfrac{{{c}}}{{{b}}} = {a}$ より $x = {int(total)}$。")


# ═════════ 数学I・A ═════════
def h_sine_R():
    rr = R.randint(2, 12)
    deg, s = R.choice([(30, F(1, 2)), (150, F(1, 2)), (90, F(1))])
    a = 2 * rr * s
    if a.denominator != 1: return False
    return add("h_sine", 1, "正弦定理", f"三角形 ABC の外接円の半径が {rr}、$A = {deg}^\\circ$ のとき、辺 BC の長さを答えよ。", int(a),
               f"正弦定理 $\\dfrac{{a}}{{\\sin A}} = 2R$ より、$a = 2 \\times {rr} \\times \\sin {deg}^\\circ = {int(a)}$。")


def h_sine_area():
    a, b = R.randint(2, 12), R.randint(2, 12)
    deg, s = R.choice([(30, F(1, 2)), (150, F(1, 2)), (90, F(1))])
    v = F(a * b, 2) * s
    if v.denominator != 1: return False
    return add("h_sine", 1, "三角形の面積", f"三角形 ABC で、AB = {a}、AC = {b}、$A = {deg}^\\circ$ のとき、面積を答えよ。", int(v),
               f"$S = \\dfrac{{1}}{{2}} \\cdot {a} \\cdot {b} \\cdot \\sin {deg}^\\circ = {int(v)}$。")


def h_sine_area60():
    a, b = R.randint(2, 12), R.randint(2, 12)
    k = F(a * b, 4)
    if k.denominator != 1: return False
    return add("h_sine", 2, "面積（√3 を含む）", f"三角形 ABC で、AB = {a}、AC = {b}、$A = 60^\\circ$ のとき、面積は $k\\sqrt{{3}}$ と表せる。$k$ を答えよ。", int(k),
               f"$S = \\dfrac{{1}}{{2}} \\cdot {a} \\cdot {b} \\cdot \\dfrac{{\\sqrt{{3}}}}{{2}} = {int(k)}\\sqrt{{3}}$。")


def h_sine_ratio():
    a, b, c = R.randint(2, 9), R.randint(2, 9), R.randint(2, 9)
    if not (a + b > c and b + c > a and a + c > b): return False
    return add("h_sine", 2, "正弦の比", f"三角形 ABC で $\\sin A : \\sin B : \\sin C = {a} : {b} : {c}$、辺 BC = {a * 3} のとき、辺 CA の長さを答えよ。", b * 3,
               f"正弦定理より $a : b : c = \\sin A : \\sin B : \\sin C = {a} : {b} : {c}$。$a = {a * 3}$ なので $b = {b * 3}$。")


def _inter(p1, p2, p3, p4):
    """直線 p1p2 と直線 p3p4 の交点。"""
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def center_figs():
    def ceva(ax):
        A, B, C = (1.0, 2.3), (0, 0), (3.2, 0)
        P = (1.3, 0.75)
        D = _inter(A, P, B, C); E = _inter(B, P, C, A); F_ = _inter(C, P, A, B)
        poly_draw(ax, [A, B, C])
        for X_, Y_ in [(A, D), (B, E), (C, F_)]: poly_draw(ax, [X_, Y_], close=False, color=ACC, lw=1.6)
        ax.plot([P[0]], [P[1]], "o", color=INK, ms=3)
        for Q, s_, dx, dy in [(A, "A", 0, .15), (B, "B", -.12, -.1), (C, "C", .12, -.1), (D, "D", 0, -.18), (E, "E", .17, .05), (F_, "F", -.17, .05), (P, "P", .05, .2)]:
            label(ax, Q, s_, dx, dy, 12)
        ax.set_xlim(-.4, 3.6); ax.set_ylim(-.4, 2.6)
    fig_save("fig_ceva", ceva)

    def mene(ax):
        A, B, C = (0.8, 2.2), (0, 0), (2.6, 0)
        F_ = (0.4, 1.1); D = (3.7, 0)
        E = _inter(F_, D, A, C)
        poly_draw(ax, [A, B, C]); poly_draw(ax, [F_, D], close=False, color=ACC, lw=1.8); poly_draw(ax, [C, D], close=False, lw=1.4)
        ax.plot([E[0]], [E[1]], "o", color=INK, ms=3)
        for Q, s_, dx, dy in [(A, "A", 0, .15), (B, "B", -.12, -.1), (C, "C", 0, -.18), (D, "D", .1, -.16), (E, "E", .14, .14), (F_, "F", -.17, 0)]:
            label(ax, Q, s_, dx, dy, 12)
        ax.set_xlim(-.4, 4.0); ax.set_ylim(-.4, 2.5)
    fig_save("fig_menelaus", mene)


def h_center_g():
    m = R.randint(2, 20) * 3
    return add("h_center", 1, "重心と中線", f"三角形 ABC の重心を G、辺 BC の中点を M とする。AM = {m} のとき、AG の長さを答えよ。", 2 * m // 3,
               f"重心は中線を 2 : 1 に内分する。AG $= {m} \\times \\dfrac{{2}}{{3}} = {2 * m // 3}$。")


def h_center_i():
    a = R.randint(10, 80) * 2
    return add("h_center", 2, "内心と角", f"三角形 ABC の内心を I とする。$\\angle A = {a}^\\circ$ のとき、$\\angle$BIC は何度か。", 90 + a // 2,
               f"$\\angle$IBC $+ \\angle$ICB $= \\dfrac{{180^\\circ - {a}^\\circ}}{{2}}$。$\\angle$BIC $= 90^\\circ + \\dfrac{{{a}^\\circ}}{{2}} = {90 + a // 2}^\\circ$。")


def h_center_o():
    a = R.randint(20, 85)
    return add("h_center", 1, "外心と角", f"鋭角三角形 ABC の外心を O とする。$\\angle A = {a}^\\circ$ のとき、$\\angle$BOC は何度か。", 2 * a,
               f"円周角の定理より、中心角 $\\angle$BOC は $\\angle A$ の 2 倍で ${2 * a}^\\circ$。")


def h_center_ceva():
    p, q, r, s_ = [R.randint(1, 6) for _ in range(4)]
    v = F(q, p) * F(s_, r)          # AF/FB · BD/DC · CE/EA = 1 → CE/EA = (FB/AF)(DC/BD)
    if v.denominator == 1 and v.numerator == 1: return False
    return fracq("h_center", 3, "チェバの定理", f"図で 3 本の線分 AD、BE、CF は 1 点 P で交わり、AF : FB = {p} : {q}、BD : DC = {r} : {s_} である。$\\dfrac{{\\text{{CE}}}}{{\\text{{EA}}}}$ を", v,
                 f"チェバの定理 $\\dfrac{{AF}}{{FB}} \\cdot \\dfrac{{BD}}{{DC}} \\cdot \\dfrac{{CE}}{{EA}} = 1$ より、$\\dfrac{{CE}}{{EA}} = \\dfrac{{{q}}}{{{p}}} \\cdot \\dfrac{{{s_}}}{{{r}}} = {frac_tex(v)}$。", figure="fig_ceva")


def h_center_mene():
    p, q, r, s_ = [R.randint(1, 6) for _ in range(4)]
    if r <= s_: return False             # D は BC の延長上（BD > CD）
    v = F(q, p) * F(s_, r)               # AF/FB · BD/DC · CE/EA = 1
    if v.denominator == 1 and v.numerator == 1: return False
    return fracq("h_center", 3, "メネラウスの定理", f"図で直線 FD が辺 AB、AC とそれぞれ F、E で交わり、BC の延長と D で交わる。AF : FB = {p} : {q}、BD : DC = {r} : {s_} のとき、$\\dfrac{{\\text{{CE}}}}{{\\text{{EA}}}}$ を", v,
                 f"メネラウスの定理 $\\dfrac{{AF}}{{FB}} \\cdot \\dfrac{{BD}}{{DC}} \\cdot \\dfrac{{CE}}{{EA}} = 1$ より、$\\dfrac{{CE}}{{EA}} = {frac_tex(v)}$。", figure="fig_menelaus")


def h_cond_basic():
    pa = F(R.randint(2, 9), 10); pab = pa * F(R.randint(1, 9), 10)
    v = pab / pa
    return fracq("h_condprob", 1, "条件付き確率の定義", f"$P(A) = {frac_tex(pa)}$、$P(A \\cap B) = {frac_tex(pab)}$ のとき、$P_A(B)$（A が起こったときに B が起こる確率）を", v,
                 f"$P_A(B) = \\dfrac{{P(A \\cap B)}}{{P(A)}} = {frac_tex(v)}$。")


def h_cond_draw():
    w, r = R.randint(1, 6), R.randint(2, 8)
    v = F(w - 1, w + r - 1)
    return fracq("h_condprob", 2, "2 回目の確率", f"当たり {w} 本、はずれ {r} 本のくじがある。1 本引いて戻さずに、もう 1 本引く。1 本目が当たりだったとき、2 本目も当たりである確率を", v,
                 f"1 本目が当たりなら、残りは当たり {w - 1} 本、全部で {w + r - 1} 本。確率は ${frac_tex(v)}$。") if w > 1 else False


def h_cond_test():
    prev = R.choice([F(1, 100), F(1, 50), F(1, 20), F(1, 10)])
    sens = R.choice([F(9, 10), F(19, 20), F(99, 100)]); fp = R.choice([F(1, 10), F(1, 20), F(1, 100)])
    v = prev * sens / (prev * sens + (1 - prev) * fp)
    return fracq("h_condprob", 3, "検査の陽性と病気", f"ある病気にかかっている人の割合は ${frac_tex(prev)}$。検査は、病気の人を ${frac_tex(sens)}$ の確率で陽性と判定し、病気でない人も ${frac_tex(fp)}$ の確率で陽性と判定する。陽性と判定された人が実際に病気である確率を", v,
                 f"$\\dfrac{{{frac_tex(prev)} \\cdot {frac_tex(sens)}}}{{{frac_tex(prev)} \\cdot {frac_tex(sens)} + {frac_tex(1 - prev)} \\cdot {frac_tex(fp)}}} = {frac_tex(v)}$。")


def h_nbase_to10():
    b = R.choice([2, 3, 5, 8]); n = R.randint(10, 400)
    digs = sp.ntheory.digits(n, b)[1:]
    s = "".join(map(str, digs))
    return add("h_nbase", 1, "n 進法から 10 進法へ", f"{b} 進法で表された数 ${s}_{{({b})}}$ を、10 進法で表せ。", n,
               f"各位に {b} のべきをかけて足す。答えは {n}。")


def h_nbase_digits():
    b = R.choice([2, 3, 4, 5, 7]); n = R.randint(30, 3000)
    digs = sp.ntheory.digits(n, b)[1:]
    return add("h_nbase", 1, "n 進法のけた数", f"10 進法の {n} を {b} 進法で表すと、何けたの数になるか。", len(digs),
               f"{b} 進法では ${''.join(map(str, digs))}_{{({b})}}$ となり、{len(digs)} けた。")


def h_nbase_ones():
    n = R.randint(30, 1000)
    c = bin(n).count("1")
    return add("h_nbase", 2, "2 進法の 1 の個数", f"10 進法の {n} を 2 進法で表したとき、1 は何個あるか。", c,
               f"{n} $= {bin(n)[2:]}_{{(2)}}$。1 は {c} 個。")


def h_nbase_frac():
    k = R.randint(2, 5); bits = [R.randint(0, 1) for _ in range(k - 1)] + [1]
    v = sum(F(bit, 2 ** (i + 1)) for i, bit in enumerate(bits))
    s = "0." + "".join(map(str, bits))
    return fracq("h_nbase", 2, "2 進法の小数", f"2 進法の小数 ${s}_{{(2)}}$ を 10 進法の分数で表す。", v,
                 f"小数点以下 $k$ けた目は $\\dfrac{{1}}{{2^k}}$ の位。足すと ${frac_tex(v)}$。")


# ═════════ 数学II ═════════
X = sp.Symbol("x")


def h_rem_two():
    a, b = R.randint(-4, 4), R.randint(-4, 4)
    if a == b or 0 in (a, b): return False
    r1, r2 = R.randint(-9, 9), R.randint(-9, 9)
    # 余り px + q：pa + q = r1, pb + q = r2
    p_ = F(r1 - r2, a - b)
    if p_.denominator != 1: return False
    q_ = r1 - p_ * a
    which = R.choice(["x の係数", "定数項"])
    v = int(p_) if which == "x の係数" else int(q_)
    return add("h_remainder", 2, "2 次式で割った余り", f"整式 $P(x)$ を $x {sg(-a)}$ で割ると余りが ${r1}$、$x {sg(-b)}$ で割ると余りが ${r2}$ である。$P(x)$ を $(x {sg(-a)})(x {sg(-b)})$ で割った余りを $px + q$ とするとき、{'$p$' if which == 'x の係数' else '$q$'} を答えよ。".replace("x + 0", "x").replace("x - 0", "x"),
               v, f"剰余の定理より $P({a}) = {a}p + q = {r1}$、$P({b}) = {b}p + q = {r2}$。解くと $p = {p_}$、$q = {q_}$。")


def h_rem_factor():
    r1, r2 = R.randint(-4, 4), R.randint(-4, 4)
    if r1 == r2 or 0 in (r1, r2): return False
    c = R.randint(-6, 6)
    # x^3 + a x^2 + b x + c が (x-r1)(x-r2) で割り切れる → 第3の根 r3 = -c/(r1 r2)
    r3 = F(-c, r1 * r2)
    if r3.denominator != 1 or c == 0: return False
    a_ = -(r1 + r2 + r3)
    return add("h_remainder", 2, "因数定理", f"$x^3 + ax^2 + bx {sg(c)}$ が $(x {sg(-r1)})(x {sg(-r2)})$ で割り切れるとき、$a$ を答えよ。", int(a_),
               f"因数定理より、もう 1 つの因数を $x - \\gamma$ とおくと、定数項から ${-r1} \\cdot {-r2} \\cdot (-\\gamma) = {c}$。$\\gamma = {r3}$。$a = -({r1} + {r2} + {r3}) = {a_}$。")


def h_rem_vieta():
    s, p_ = R.randint(-6, 6), R.randint(-6, 6)
    if p_ == 0: return False
    which = R.randint(0, 2)
    if which == 0:
        v = s * s - 2 * p_; t = "$\\alpha^2 + \\beta^2$"; e = f"$(\\alpha + \\beta)^2 - 2\\alpha\\beta = {s * s} - ({2 * p_}) = {v}$"
    elif which == 1:
        v = s ** 3 - 3 * p_ * s; t = "$\\alpha^3 + \\beta^3$"; e = f"$(\\alpha + \\beta)^3 - 3\\alpha\\beta(\\alpha + \\beta) = {v}$"
    else:
        v = (s * s - 4 * p_); t = "$(\\alpha - \\beta)^2$"; e = f"$(\\alpha + \\beta)^2 - 4\\alpha\\beta = {v}$"
    return add("h_remainder", 1 if which != 1 else 2, "解と係数の関係", f"2 次方程式 ${poly([(1, 'x^2'), (-s, 'x'), (p_, '')])} = 0$ の 2 つの解を $\\alpha$、$\\beta$ とするとき、{t} の値を答えよ。", v,
               f"解と係数の関係より $\\alpha + \\beta = {s}$、$\\alpha\\beta = {p_}$。{e}。")


def h_rem_cubic():
    r = [R.randint(-4, 4) for _ in range(3)]
    e1, e2, e3 = sum(r), r[0] * r[1] + r[1] * r[2] + r[0] * r[2], r[0] * r[1] * r[2]
    v = e1 * e1 - 2 * e2
    return add("h_remainder", 2, "3 次方程式の解と係数", f"3 次方程式 ${poly([(1, 'x^3'), (-e1, 'x^2'), (e2, 'x'), (-e3, '')])} = 0$ の 3 つの解を $\\alpha$、$\\beta$、$\\gamma$ とするとき、$\\alpha^2 + \\beta^2 + \\gamma^2$ の値を答えよ。", v,
               f"$\\alpha + \\beta + \\gamma = {e1}$、$\\alpha\\beta + \\beta\\gamma + \\gamma\\alpha = {e2}$。$\\alpha^2 + \\beta^2 + \\gamma^2 = {e1}^2 - 2 \\cdot ({e2}) = {v}$。")


def h_line_dist():
    a, b, c_ = R.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (8, 15, 17), (6, 8, 10)])
    a *= R.choice([1, -1]); px, py = R.randint(-5, 5), R.randint(-5, 5)
    d = R.randint(1, 6)
    c = -(a * px + b * py) + R.choice([1, -1]) * d * c_
    return add("h_line", 1, "点と直線の距離", f"点 $({px}, {py})$ と直線 ${poly([(a, 'x'), (b, 'y'), (c, '')])} = 0$ の距離を答えよ。", d,
               f"$\\dfrac{{|{a} \\cdot ({px}) + {b} \\cdot ({py}) {sg(c)}|}}{{\\sqrt{{{a}^2 + {b}^2}}}} = \\dfrac{{{d * c_}}}{{{c_}}} = {d}$。")


def h_line_tangent():
    m, r = R.choice([(F(3, 4), 4), (F(4, 3), 3), (F(3, 4), 8), (F(5, 12), 12), (F(12, 5), 5), (F(4, 3), 6)])
    k2 = r * r * (1 + m * m)
    k = math.isqrt(int(k2))
    if F(k * k) != k2: return False
    return add("h_line", 2, "円と直線が接する条件", f"円 $x^2 + y^2 = {r * r}$ と直線 $y = {frac_tex(m)}x + k$ が接するような正の定数 $k$ を答えよ。", k,
               f"中心と直線の距離が半径に等しい：$\\dfrac{{|k|}}{{\\sqrt{{1 + ({frac_tex(m)})^2}}}} = {r}$。$k = {k}$。")


def h_line_apollo():
    a = R.randint(2, 6); k = R.choice([2, 3])
    # A(0,0), B(a,0)、PA:PB = k:1 → アポロニウスの円。中心と半径
    P = sp.symbols("px py", real=True)
    eq = sp.expand(P[0] ** 2 + P[1] ** 2 - k * k * ((P[0] - a) ** 2 + P[1] ** 2))
    cx = sp.Rational(k * k * a, k * k - 1); r2 = cx ** 2 - sp.Rational(k * k * a * a, k * k - 1)
    rad = sp.sqrt(r2)
    assert sp.simplify(eq.subs(P[0], cx + rad).subs(P[1], 0)) == 0
    radf = F(str(sp.nsimplify(rad)))
    return fracq("h_line", 3, "アポロニウスの円", f"2 点 A$(0, 0)$、B$({a}, 0)$ からの距離の比が PA : PB $= {k} : 1$ となる点 P の軌跡は円になる。その半径を", radf,
                 f"$x^2 + y^2 = {k * k}\\{{(x - {a})^2 + y^2\\}}$ を整理して、中心 $\\left({frac_tex(F(str(cx)))}, 0\\right)$、半径 ${frac_tex(radf)}$ の円。")


def h_line_lp():
    a, b, c, d = R.randint(1, 4), R.randint(1, 4), R.randint(6, 16), R.randint(6, 16)
    # x ≥ 0, y ≥ 0, ax + y ≤ c, x + by ≤ d で x + y の最大値（端点）
    pts = [(F(0), F(0)), (F(c, a), F(0)), (F(0), F(d, b))]
    det = a * b - 1
    if det == 0: return False
    xi, yi = F(c * b - d, det), F(a * d - c, det)
    if xi >= 0 and yi >= 0: pts.append((xi, yi))
    feas = [q for q in pts if q[0] >= 0 and q[1] >= 0 and a * q[0] + q[1] <= c and q[0] + b * q[1] <= d]
    v = max(q[0] + q[1] for q in feas)
    if v.denominator != 1: return False
    return add("h_line", 3, "領域と最大値", f"$x \\ge 0$、$y \\ge 0$、${poly([(a, 'x'), (1, 'y')])} \\le {c}$、${poly([(1, 'x'), (b, 'y')])} \\le {d}$ を満たすとき、$x + y$ の最大値を答えよ。", int(v),
               f"条件の表す領域は多角形。$x + y = k$ の直線を動かし、領域の頂点で最大になる。頂点の値をくらべて最大値は ${int(v)}$。")


def h_comp_max():
    a, b = R.choice([(3, 4), (4, 3), (5, 12), (12, 5), (6, 8), (8, 6), (1, 0)])
    if b == 0: return False
    c = R.randint(-5, 5)
    r = math.isqrt(a * a + b * b)
    return add("h_compose", 1, "合成と最大値", f"関数 $y = {a}\\sin x + {b}\\cos x {sg(c)}$ の最大値を答えよ。".replace(" + 0$", "$"), r + c,
               f"$\\sqrt{{{a}^2 + {b}^2}} = {r}$ なので $y = {r}\\sin(x + \\alpha) {sg(c)}$。最大値は ${r + c}$。")


def h_comp_min():
    a, b = R.choice([(3, 4), (4, 3), (5, 12), (12, 5), (6, 8), (8, 15)])
    return add("h_compose", 1, "合成と最小値", f"関数 $y = {a}\\sin x - {b}\\cos x$ の最小値を答えよ。", -math.isqrt(a * a + b * b),
               f"$y = {math.isqrt(a * a + b * b)}\\sin(x - \\alpha)$ と合成できるので、最小値は $-{math.isqrt(a * a + b * b)}$。")


def h_divpt_in():
    a1, a2, b1, b2 = [R.randint(-8, 8) for _ in range(4)]
    m, n = R.randint(1, 4), R.randint(1, 4)
    x = F(n * a1 + m * b1, m + n)
    if x.denominator != 1: return False
    return add("h_divpt", 1, "内分点の座標", f"2 点 A$({a1}, {a2})$、B$({b1}, {b2})$ を結ぶ線分 AB を ${m} : {n}$ に内分する点の $x$ 座標を答えよ。", int(x),
               f"$\\dfrac{{{n} \\cdot ({a1}) + {m} \\cdot ({b1})}}{{{m} + {n}}} = {int(x)}$。")


def h_divpt_out():
    a1, b1 = R.randint(-8, 8), R.randint(-8, 8)
    m, n = R.randint(1, 5), R.randint(1, 5)
    if m == n: return False
    x = F(-n * a1 + m * b1, m - n)
    if x.denominator != 1: return False
    return add("h_divpt", 2, "外分点の座標", f"数直線上の 2 点 A$({a1})$、B$({b1})$ を結ぶ線分 AB を ${m} : {n}$ に外分する点の座標を答えよ。", int(x),
               f"$\\dfrac{{-{n} \\cdot ({a1}) + {m} \\cdot ({b1})}}{{{m} - {n}}} = {int(x)}$。")


def h_divpt_g():
    xs = [R.randint(-9, 9) for _ in range(3)]
    if sum(xs) % 3: return False
    ys = [R.randint(-9, 9) for _ in range(3)]
    return add("h_divpt", 1, "重心の座標", f"3 点 $({xs[0]}, {ys[0]})$、$({xs[1]}, {ys[1]})$、$({xs[2]}, {ys[2]})$ を頂点とする三角形の重心の $x$ 座標を答えよ。", sum(xs) // 3,
               f"重心の $x$ 座標は、3 つの $x$ 座標の平均。$\\dfrac{{{xs[0]} + ({xs[1]}) + ({xs[2]})}}{{3}} = {sum(xs) // 3}$。")


def h_divpt_space():
    a = [R.randint(-4, 4) for _ in range(3)]; b = [R.randint(-4, 4) for _ in range(3)]
    if a == [0, 0, 0] or b == [0, 0, 0]: return False
    which = R.randint(0, 1)
    if which == 0:
        return add("h_divpt", 1, "空間ベクトルの内積", f"$\\vec{{a}} = ({a[0]}, {a[1]}, {a[2]})$、$\\vec{{b}} = ({b[0]}, {b[1]}, {b[2]})$ のとき、$\\vec{{a}} \\cdot \\vec{{b}}$ を答えよ。", sum(i * j for i, j in zip(a, b)),
                   "成分ごとの積を足す。")
    v = sum((i + j) ** 2 for i, j in zip(a, b))
    return add("h_divpt", 2, "空間ベクトルの大きさ", f"$\\vec{{a}} = ({a[0]}, {a[1]}, {a[2]})$、$\\vec{{b}} = ({b[0]}, {b[1]}, {b[2]})$ のとき、$|\\vec{{a}} + \\vec{{b}}|^2$ を答えよ。", v,
               f"$\\vec{{a}} + \\vec{{b}} = ({a[0] + b[0]}, {a[1] + b[1]}, {a[2] + b[2]})$。2 乗の和は ${v}$。")


def h_stat_binom():
    n = R.randint(10, 400); p_ = R.choice([F(1, 2), F(1, 3), F(1, 4), F(1, 5), F(1, 6), F(2, 5), F(3, 4)])
    which = R.choice(["期待値", "分散"])
    v = n * p_ if which == "期待値" else n * p_ * (1 - p_)
    if v.denominator != 1: return False
    return add("h_statinf", 1, f"二項分布の{which}", f"確率変数 $X$ が二項分布 $B\\left({n}, {frac_tex(p_)}\\right)$ に従うとき、$X$ の{which}を答えよ。", int(v),
               f"二項分布 $B(n, p)$ の期待値は $np$、分散は $np(1 - p)$。答えは ${int(v)}$。")


def h_stat_table():
    vals = sorted(R.sample(range(-3, 10), 3)); ws = [R.randint(1, 5) for _ in range(3)]
    tot = sum(ws); e = F(sum(v * w for v, w in zip(vals, ws)), tot)
    body = f"確率変数 $X$ のとる値は {vals[0]}、{vals[1]}、{vals[2]} で、それぞれの確率は ${frac_tex(F(ws[0], tot))}$、${frac_tex(F(ws[1], tot))}$、${frac_tex(F(ws[2], tot))}$ である。$X$ の期待値を答えよ。"
    if e.denominator != 1: return fracq("h_statinf", 2, "期待値", body.replace("答えよ。", ""), e, "値と確率の積を足す。") if e > 0 else False
    return add("h_statinf", 2, "期待値", body, int(e), "値と確率の積を足す。")


def h_stat_lin():
    m, v = R.randint(-5, 10), R.randint(1, 9); a, b = R.randint(-4, 4), R.randint(-9, 9)
    if a == 0: return False
    which = R.choice(["期待値", "分散"])
    ans = a * m + b if which == "期待値" else a * a * v
    return add("h_statinf", 2, "aX + b の期待値・分散", f"確率変数 $X$ の期待値が ${m}$、分散が ${v}$ のとき、$Y = {poly([(a, 'X'), (b, '')])}$ の{which}を答えよ。", ans,
               "$E(aX + b) = aE(X) + b$、$V(aX + b) = a^2 V(X)$。")


def h_stat_mean():
    s = R.randint(2, 20); n = R.choice([4, 9, 16, 25, 36, 49, 64, 100])
    sd = F(s, math.isqrt(n))
    if sd.denominator != 1: return False
    return add("h_statinf", 2, "標本平均の標準偏差", f"母標準偏差 ${s}$ の母集団から、大きさ ${n}$ の標本を無作為に取り出す。標本平均の標準偏差を答えよ。", int(sd),
               f"標本平均の標準偏差は $\\dfrac{{\\sigma}}{{\\sqrt{{n}}}} = \\dfrac{{{s}}}{{\\sqrt{{{n}}}}} = {int(sd)}$。")


def h_curve_polar():
    r = R.randint(1, 9)
    th, cx, sx = R.choice([("0", 1, 0), ("\\dfrac{\\pi}{2}", 0, 1), ("\\pi", -1, 0), ("\\dfrac{3\\pi}{2}", 0, -1)])
    which = R.choice(["x", "y"])
    v = r * (cx if which == "x" else sx)
    return add("h_curve", 1, "極座標と直交座標", f"極座標が $\\left({r}, {th}\\right)$ の点の、直交座標の ${which}$ 座標を答えよ。", v,
               f"$x = r\\cos\\theta$、$y = r\\sin\\theta$。${which} = {v}$。")


def h_curve_param():
    a, b = R.randint(2, 9), R.randint(1, 9)
    if a == b: return False
    return add("h_curve", 2, "媒介変数表示と楕円", f"媒介変数表示 $x = {a}\\cos\\theta$、$y = {b}\\sin\\theta$ で表される曲線の、$x$ 軸との交点のうち、$x$ 座標が正のものの $x$ 座標を答えよ。", a,
               f"$\\theta$ を消すと $\\dfrac{{x^2}}{{{a * a}}} + \\dfrac{{y^2}}{{{b * b}}} = 1$ の楕円。$y = 0$ のとき $x = \\pm {a}$。")


def h_func3_asym():
    a, b, c = R.randint(-5, 5), R.randint(-9, 9), R.randint(-6, 6)
    if a == 0 or c == 0 or b == a * c: return False
    which = R.choice(["x", "y"])
    v = -c if which == "x" else a
    return add("h_func3", 1, "分数関数の漸近線", f"関数 $y = \\dfrac{{{poly([(a, 'x'), (b, '')])}}}{{x {sg(c)}}}$ のグラフの漸近線のうち、${which} = k$ の形のものの $k$ を答えよ。", v,
               f"$y = {a} + \\dfrac{{{b - a * c}}}{{x {sg(c)}}}$ と変形できる。漸近線は $x = {-c}$ と $y = {a}$。")


def h_func3_inv():
    a, b = R.randint(2, 6), R.randint(-9, 9); y = R.randint(-20, 30)
    if (y - b) % a: return False
    return add("h_func3", 1, "逆関数の値", f"$f(x) = {poly([(a, 'x'), (b, '')])}$ の逆関数を $f^{{-1}}(x)$ とする。$f^{{-1}}({y})$ の値を答えよ。", (y - b) // a,
               f"$f(t) = {y}$ となる $t$ を求める。${a}t {sg(b)} = {y}$ より $t = {(y - b) // a}$。")


def h_func3_comp():
    a, b, c, d, t = R.randint(1, 4), R.randint(-5, 5), R.randint(1, 3), R.randint(-5, 5), R.randint(-3, 3)
    v = a * (c * t * t + d) + b
    return add("h_func3", 1, "合成関数の値", f"$f(x) = {poly([(a, 'x'), (b, '')])}$、$g(x) = {poly([(c, 'x^2'), (d, '')])}$ のとき、$(f \\circ g)({t})$ の値を答えよ。", v,
               f"$g({t}) = {c * t * t + d}$。$f({c * t * t + d}) = {v}$。")


def h_func3_irr():
    a, s = R.randint(-5, 8), R.randint(0, 9)
    # √(x + a) = x + b の解が s（s + b ≥ 0）。b = √(s+a) − s
    if s + a < 0: return False
    rt = math.isqrt(s + a)
    if rt * rt != s + a: return False
    b = rt - s
    sols = [z for z in sp.solve(sp.Eq((X + b) ** 2, X + a), X) if z.is_real and z + b >= 0]
    if len(sols) != 1: return False
    return add("h_func3", 2, "無理方程式", f"方程式 $\\sqrt{{x {sg(a)}}} = x {sg(b)}$ を解け（解は 1 つ）。".replace("x + 0", "x").replace("x - 0", "x"), int(sols[0]),
               f"両辺を 2 乗して解き、$x {sg(b)} \\ge 0$ を満たすものだけを残す。$x = {sols[0]}$。")


def h_graph_infl():
    a = R.randint(-4, 4) * 3; b, c = R.randint(-9, 9), R.randint(-9, 9)
    if a == 0: return False
    return add("h_graph", 1, "3 次関数の変曲点", f"曲線 $y = {poly([(1, 'x^3'), (a, 'x^2'), (b, 'x'), (c, '')])}$ の変曲点の $x$ 座標を答えよ。", -a // 3,
               f"$y'' = 6x {sg(2 * a)}$。$y'' = 0$ となる $x = {-a // 3}$ の前後で符号が変わる。")


def hand_items():
    # ── 合同・対称（図なし） ──
    choice("e_shape", 2, "点対称な図形", "次のうち、点対称な図形はどれか。", "平行四辺形", ["正三角形", "二等辺三角形", "正五角形"],
           "180° 回転させてぴったり重なる図形が点対称。平行四辺形は対角線の交点を中心に点対称。")
    choice("e_shape", 2, "線対称で点対称", "次のうち、線対称でもあり点対称でもある図形はどれか。", "ひし形", ["平行四辺形", "台形", "正三角形"],
           "ひし形は、対角線を対称の軸とする線対称で、対角線の交点を中心とする点対称。")
    # ── 合成 ──
    choice("h_compose", 1, "合成の形", "$\\sqrt{3}\\sin x + \\cos x$ を $r\\sin(x + \\alpha)$（$r > 0$、$-\\pi < \\alpha \\le \\pi$）の形にしたものはどれか。",
           "$2\\sin\\left(x + \\dfrac{\\pi}{6}\\right)$", ["$2\\sin\\left(x + \\dfrac{\\pi}{3}\\right)$", "$\\sqrt{3}\\sin\\left(x + \\dfrac{\\pi}{6}\\right)$", "$4\\sin\\left(x + \\dfrac{\\pi}{6}\\right)$"],
           "$r = \\sqrt{3 + 1} = 2$、$\\cos\\alpha = \\dfrac{\\sqrt{3}}{2}$、$\\sin\\alpha = \\dfrac{1}{2}$ より $\\alpha = \\dfrac{\\pi}{6}$。")
    cnt = sum(1 for k in range(200000) if False)
    sols = sp.solveset(sp.sin(X) + sp.sqrt(3) * sp.cos(X) - 1, X, sp.Interval.Ropen(0, 2 * sp.pi))
    add("h_compose", 2, "合成して方程式を解く", "$0 \\le x < 2\\pi$ で、方程式 $\\sin x + \\sqrt{3}\\cos x = 1$ の解は何個あるか。", len(sols),
        "$2\\sin\\left(x + \\dfrac{\\pi}{3}\\right) = 1$。$\\dfrac{\\pi}{3} \\le x + \\dfrac{\\pi}{3} < \\dfrac{7\\pi}{3}$ で $\\sin = \\dfrac{1}{2}$ となるのは 2 個。")
    t = sp.Symbol("t")
    mx = sp.maximum((t ** 2 - 1) / 2 + t, t, sp.Interval(-sp.sqrt(2), sp.sqrt(2)))
    assert sp.simplify(mx - (sp.Rational(1, 2) + sp.sqrt(2))) == 0
    choice("h_compose", 4, "おきかえと最大値", "関数 $y = \\sin x + \\cos x + \\sin x\\cos x$ の最大値はどれか。", "$\\sqrt{2} + \\dfrac{1}{2}$",
           ["$2$", "$\\sqrt{2} + 1$", "$\\dfrac{3}{2}$"], "$t = \\sin x + \\cos x$（$-\\sqrt{2} \\le t \\le \\sqrt{2}$）とおくと $\\sin x\\cos x = \\dfrac{t^2 - 1}{2}$。$y = \\dfrac{t^2 - 1}{2} + t$ は $t = \\sqrt{2}$ で最大 $\\sqrt{2} + \\dfrac{1}{2}$。")
    # ── 剰余（難） ──
    q, r = sp.div(X ** 100, (X - 1) * (X - 2), X)
    p_, q_ = sp.Poly(r, X).all_coeffs()
    assert p_ == 2 ** 100 - 1 and q_ == 2 - 2 ** 100
    choice("h_remainder", 4, "大きな次数の余り", "$x^{100}$ を $x^2 - 3x + 2$ で割った余りはどれか。", "$(2^{100} - 1)x - 2^{100} + 2$",
           ["$(2^{100} + 1)x - 2^{100}$", "$2^{100}x - 2^{100} + 1$", "$(2^{100} - 1)x + 1$"],
           "余りを $ax + b$ とおく。$x = 1$ で $a + b = 1$、$x = 2$ で $2a + b = 2^{100}$。$a = 2^{100} - 1$、$b = 2 - 2^{100}$。")
    # ── 条件付き確率（難） ──
    fracq("h_condprob", 4, "3 つの扉の問題", "3 つの扉のうち 1 つに賞品がある。あなたが 1 つ選ぶと、賞品の場所を知る司会者が、残りの 2 つのうち、はずれの扉を 1 つ開ける（両方はずれなら等しい確率で選ぶ）。ここで選び直すと当たる確率を", F(2, 3),
          "最初に当たりを選んでいる確率は $\\dfrac{1}{3}$。そうでないとき（確率 $\\dfrac{2}{3}$）は、選び直せば必ず当たる。")
    fracq("h_condprob", 4, "2 人の子ども", "2 人の子どもがいる家庭のうち、少なくとも 1 人が男の子だとわかっている。2 人とも男の子である確率を（男女は等しい確率で、2 人は独立とする）", F(1, 3),
          "男男、男女、女男の 3 通りが同じ確率で、そのうち 2 人とも男の子は 1 通り。")
    # ── ベクトル（難） ──
    fracq("h_divpt", 4, "ベクトルの式と面積比", "三角形 ABC の内部の点 P が $\\vec{PA} + 2\\vec{PB} + 3\\vec{PC} = \\vec{0}$ を満たす。三角形 PBC の面積は三角形 ABC の面積の何倍か。", F(1, 6),
          "$\\vec{AP} = \\dfrac{2\\vec{AB} + 3\\vec{AC}}{6}$。面積比は、係数の比で $\\triangle PBC : \\triangle PCA : \\triangle PAB = 1 : 2 : 3$。$\\triangle PBC$ は全体の $\\dfrac{1}{6}$。")
    # ── n 進法（難） ──
    c = sum(1 for k in range(1, 1025) if bin(k).count("1") == 3)
    add("h_nbase", 4, "2 進法で 1 が 3 個", "1 以上 1024 以下の整数のうち、2 進法で表したときに 1 がちょうど 3 個あるものは何個あるか。", c,
        "1024 は 2 進法で 11 けた（1 が 1 個）なので数えなくてよい。10 けた以下の 2 進数で、10 か所から 1 を 3 か所選ぶ：${}_{10}\\mathrm{C}_3 = 120$。")
    # ── 領域（難） ──
    xs = [(x, y) for x in range(-10, 11) for y in range(-10, 11) if x * x + y * y <= 25 and y >= x * x - 5]
    add("h_line", 4, "2 つの不等式の格子点", "連立不等式 $x^2 + y^2 \\le 25$、$y \\ge x^2 - 5$ を満たす整数の組 $(x, y)$ は何組あるか。", len(xs),
        "$x$ の値ごとに、$y$ の範囲 $x^2 - 5 \\le y \\le \\sqrt{25 - x^2}$ に入る整数を数えて足す。")
    # ── 統計（難・正規分布の表を使う） ──
    choice("h_statinf", 3, "信頼区間", "母標準偏差が 20 の母集団から大きさ 100 の標本をとり、標本平均が 50 だった。母平均の信頼度 95% の信頼区間はどれか（1.96 を使う）。",
           "$46.08 \\le m \\le 53.92$", ["$48.04 \\le m \\le 51.96$", "$10.8 \\le m \\le 89.2$", "$49.6 \\le m \\le 50.4$"],
           "$50 \\pm 1.96 \\times \\dfrac{20}{\\sqrt{100}} = 50 \\pm 3.92$。")
    choice("h_statinf", 2, "正規分布の確率", "確率変数 $Z$ が標準正規分布 $N(0, 1)$ に従うとき、$P(-1.96 \\le Z \\le 1.96)$ にいちばん近いものはどれか。", "0.95",
           ["0.68", "0.99", "0.90"], "標準正規分布で $|Z| \\le 1.96$ となる確率は約 0.95。")
    # ── グラフ（凹凸・漸近線） ──
    f = X * sp.exp(-X)
    assert sp.solve(sp.diff(f, X, 2), X) == [2]
    add("h_graph", 2, "変曲点", "曲線 $y = xe^{-x}$ の変曲点の $x$ 座標を答えよ。", 2, "$y'' = (x - 2)e^{-x}$。$x = 2$ の前後で符号が変わる。")
    choice("h_graph", 2, "斜めの漸近線", "曲線 $y = \\dfrac{x^2 + 1}{x}$ の漸近線をすべて選んだものはどれか。", "$x = 0$ と $y = x$",
           ["$x = 0$ だけ", "$y = x$ だけ", "$x = 0$ と $y = 0$"], "$y = x + \\dfrac{1}{x}$。$x \\to 0$ で発散するので $x = 0$、$x \\to \\pm\\infty$ で $y - x \\to 0$ なので $y = x$。")
    sols = sp.solve(sp.diff(X ** 4 - 6 * X ** 2, X, 2), X)
    add("h_graph", 2, "変曲点の個数", "曲線 $y = x^4 - 6x^2$ の変曲点は何個あるか。", len(sols), "$y'' = 12x^2 - 12$。$x = \\pm 1$ の前後で符号が変わるので 2 個。")
    sols = sp.solve(sp.diff(sp.log(X ** 2 + 1), X, 2), X)
    add("h_graph", 3, "対数関数の変曲点", "曲線 $y = \\log(x^2 + 1)$ の変曲点のうち、$x$ 座標が正のものの $x$ 座標を答えよ。", int(max(sols)),
        "$y' = \\dfrac{2x}{x^2 + 1}$、$y'' = \\dfrac{2(1 - x^2)}{(x^2 + 1)^2}$。$x = \\pm 1$ で符号が変わる。")
    # ── 分数不等式（難） ──
    xs = [k for k in range(-50, 51) if k != 2 and F(k + 1, k - 2) >= 2]
    add("h_func3", 4, "分数不等式", "不等式 $\\dfrac{x + 1}{x - 2} \\ge 2$ を満たす整数 $x$ は何個あるか。", len(xs),
        "$\\dfrac{x + 1}{x - 2} - 2 = \\dfrac{5 - x}{x - 2} \\ge 0$ より $2 < x \\le 5$。整数は 3、4、5。")
    # ── 媒介変数・極方程式 ──
    choice("h_curve", 2, "媒介変数を消去", "媒介変数表示 $x = t + 1$、$y = t^2$ で表される曲線はどれか。", "$y = (x - 1)^2$",
           ["$y = x^2 + 1$", "$y = (x + 1)^2$", "$y = x^2 - 1$"], "$t = x - 1$ を $y = t^2$ に代入する。")
    add("h_curve", 3, "極方程式と円", "極方程式 $r = 6\\cos\\theta$ が表す円の半径を答えよ。", 3,
        "両辺に $r$ をかけて $x^2 + y^2 = 6x$、$(x - 3)^2 + y^2 = 9$。半径 3。")
    choice("h_curve", 4, "極方程式の直線", "極方程式 $r\\cos\\left(\\theta - \\dfrac{\\pi}{3}\\right) = 2$ が表す図形はどれか。", "直線 $x + \\sqrt{3}y = 4$",
           ["円 $x^2 + y^2 = 4$", "直線 $\\sqrt{3}x + y = 4$", "直線 $x + \\sqrt{3}y = 2$"],
           "加法定理で $\\dfrac{1}{2}r\\cos\\theta + \\dfrac{\\sqrt{3}}{2}r\\sin\\theta = 2$。$x + \\sqrt{3}y = 4$。")
    # ── 正弦定理（難） ──
    a, b, c = 7, 8, 5
    cosA = F(b * b + c * c - a * a, 2 * b * c)
    assert cosA == F(1, 2)
    add("h_sine", 3, "外接円の半径", "三角形 ABC で、BC = 7、CA = 8、AB = 5 のとき、外接円の半径を $R$ とする。$3R^2$ の値を答えよ。", 49,
        "余弦定理で $\\cos A = \\dfrac{1}{2}$、$A = 60^\\circ$。正弦定理で $2R = \\dfrac{7}{\\sin 60^\\circ}$、$R = \\dfrac{7}{\\sqrt{3}}$。$3R^2 = 49$。")
    add("h_sine", 4, "円に内接する四角形", "円に内接する四角形 ABCD で、AB = 2、BC = 3、CD = 1、$\\angle$ABC $= 60^\\circ$ のとき、辺 DA の長さを答えよ。", 3,
        "AC$^2 = 4 + 9 - 6 = 7$。$\\angle$ADC $= 120^\\circ$ なので、DA $= x$ として $7 = 1 + x^2 + x$。$x = 2$ … ではなく、$x^2 + x - 6 = 0$ より $x = 2$。")
    return


def fix_cyclic():
    # 円に内接する四角形：AC^2 = 7、x^2 + x + 1 = 7 → x = 2（答えと解説を正しくする）
    for p in OUT:
        if p["title"] == "円に内接する四角形":
            x_ = sp.Symbol("x_", positive=True)
            sol = sp.solve(x_ ** 2 + x_ + 1 - 7, x_)
            assert sol == [2]
            p["answer"] = 2
            p["explanation"] = ("三角形 ABC で余弦定理：AC$^2 = 2^2 + 3^2 - 2 \\cdot 2 \\cdot 3 \\cos 60^\\circ = 7$。"
                                "円に内接するので $\\angle$ADC $= 120^\\circ$。DA $= x$ として三角形 ACD で余弦定理："
                                "$7 = 1 + x^2 - 2x\\cos 120^\\circ = x^2 + x + 1$。$x > 0$ より $x = 2$。")


PLAN = [
    (e_round_place, 10), (e_round_top2, 8), (e_round_range, 8), (e_round_estimate, 8),
    (e_unit_crowd, 6), (e_unit_density, 8), (e_unit_fuel, 8), (e_unit_price, 8),
    (e_scale_map, 8), (e_scale_tri, 6),
    (m_par_de, 12), (m_par_three, 12), (m_par_mid, 8), (m_par_bis, 10),
    (m_box_q, 14), (m_sample, 10),
    (h_sine_R, 8), (h_sine_area, 10), (h_sine_area60, 10), (h_sine_ratio, 8),
    (h_center_g, 8), (h_center_i, 10), (h_center_o, 8), (h_center_ceva, 12), (h_center_mene, 12),
    (h_cond_basic, 10), (h_cond_draw, 10), (h_cond_test, 10),
    (h_nbase_to10, 12), (h_nbase_digits, 10), (h_nbase_ones, 10), (h_nbase_frac, 10),
    (h_rem_two, 14), (h_rem_factor, 12), (h_rem_vieta, 14), (h_rem_cubic, 10),
    (h_line_dist, 14), (h_line_tangent, 6), (h_line_apollo, 8), (h_line_lp, 12),
    (h_comp_max, 10), (h_comp_min, 6),
    (h_divpt_in, 12), (h_divpt_out, 10), (h_divpt_g, 10), (h_divpt_space, 12),
    (h_stat_binom, 12), (h_stat_table, 10), (h_stat_lin, 12), (h_stat_mean, 10),
    (h_curve_polar, 8), (h_curve_param, 8),
    (h_func3_asym, 12), (h_func3_inv, 10), (h_func3_comp, 10), (h_func3_irr, 10),
    (h_graph_infl, 10),
]


def generate():
    OUT.clear(); _count.clear(); _seen.clear()
    shape_figs(); parallel_figs(); center_figs(); box_figs()
    for fn, n in PLAN:
        make(n, fn)
    hand_items(); fix_cyclic()
    return list(OUT)


if __name__ == "__main__":
    import collections
    ps = generate()
    print(len(ps), collections.Counter(p["difficulty"] for p in ps), collections.Counter(p["unit"] for p in ps))
