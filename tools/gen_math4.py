"""新しく増やす数学の単元（比例・反比例、一次関数、文字式、相似、円、空間図形、データの活用、数列の応用、微分の応用など）。
数字を変えて作る問題。乱数は自前の線形合同法。正解は、別の方法（総当たり・sympy）でも確かめて登録する。"""
from fractions import Fraction
from math import gcd, isqrt, pi
import statistics
import sympy as sp
import gen_problems as G
from gen_problems import fmt, add, make

R = G.Rng(20261107)
X = sp.Symbol("x")


def sg(n):          # + 3 / - 3
    return ("+ %d" % n) if n >= 0 else ("- %d" % -n)


def eqn(a, b):      # a x + b をきれいに（係数1や0を省く）
    return G.poly([(a, "x"), (b, "")])


# ═════════ 比例・反比例 ═════════
def t_prop1():
    a, p, q = R.randint(2, 9), R.randint(2, 9), R.randint(2, 9)
    if p == q: return False
    return add(401, "junior", 1, "比例", fmt("$y$ は $x$ に比例し、$x = «p»$ のとき $y = «yp»$ である。$x = «q»$ のときの $y$ の値を答えよ。", p=p, q=q, yp=a * p), a * q,
               fmt("比例定数は $«yp» \\div «p» = «a»$。$y = «a»x$ に $x = «q»$ を代入して $«y»$。", yp=a * p, p=p, a=a, q=q, y=a * q))


def t_prop2():
    a = R.randint(2, 12); p = R.randint(1, 5) * 2
    return add(402, "junior", 1, "比例", fmt("$y = ax$ のグラフが点 $(«p»,\\ «y»)$ を通るとき、$a$ の値を答えよ。", p=p, y=a * p), a,
               fmt("$«y» = a \\times «p»$ より $a = «a»$。", y=a * p, p=p, a=a))


def t_inv1():
    k = R.choice([12, 18, 20, 24, 30, 36, 48, 60]); divs = [d for d in range(1, k + 1) if k % d == 0 and d > 1]
    p, q = R.choice(divs), R.choice(divs)
    if p == q: return False
    return add(403, "junior", 2, "反比例", fmt("$y$ は $x$ に反比例し、$x = «p»$ のとき $y = «yp»$ である。$x = «q»$ のときの $y$ の値を答えよ。", p=p, q=q, yp=k // p), k // q,
               fmt("$xy = «k»$ が一定。$x = «q»$ のとき $y = «k» \\div «q» = «y»$。", k=k, q=q, y=k // q))


def t_inv2():
    p, q = R.randint(2, 9), R.randint(2, 9)
    return add(404, "junior", 1, "反比例", fmt("$y = \\dfrac{a}{x}$ のグラフが点 $(«p»,\\ «q»)$ を通るとき、$a$ の値を答えよ。", p=p, q=q), p * q,
               fmt("$a = xy = «p» \\times «q» = «a»$。", p=p, q=q, a=p * q))


def t_prop_word():
    n, price = R.randint(3, 9), R.randint(30, 150); m = R.randint(10, 20)
    if n == m: return False
    return add(405, "junior", 1, "比例", fmt("同じ品物 $«n»$ 個で $«t»$ 円のとき、$«m»$ 個では何円か。", n=n, t=n * price, m=m), m * price,
               fmt("1個 $«price»$ 円なので $«price» \\times «m» = «a»$ 円。", price=price, m=m, a=m * price))


# ═════════ 一次関数 ═════════
def t_lin_val():
    a, b, c = R.choice([-4, -3, -2, 2, 3, 4, 5]), R.randint(-8, 8), R.randint(-5, 6)
    return add(411, "junior", 1, "一次関数", fmt("一次関数 $y = «a»x «bs»$ で、$x = «c»$ のときの $y$ の値を答えよ。", a=a, bs=sg(b), c=c), a * c + b,
               fmt("$y = «a» \\times («c») «bs» = «y»$。", a=a, c=c, bs=sg(b), y=a * c + b))


def t_lin_int():
    a, b = R.choice([-3, -2, -1, 1, 2, 3]), R.randint(-9, 9); x1 = R.randint(-3, 3); dx = R.randint(1, 3)
    return add(412, "junior", 2, "一次関数", fmt("2点 $(«x1»,\\ «y1»)$、$(«x2»,\\ «y2»)$ を通る直線の $y$ 切片を答えよ。", x1=x1, y1=a * x1 + b, x2=x1 + dx, y2=a * (x1 + dx) + b), b,
               fmt("傾きは $«a»$。$y = «a»x + b$ に点を代入して $b = «b»$。", a=a, b=b))


def t_lin_rate():
    a = R.choice([-5, -4, -3, -2, 2, 3, 4, 5, 6]); b = R.randint(-5, 5); p, q = R.randint(-3, 1), R.randint(2, 6)
    return add(413, "junior", 1, "一次関数", fmt("一次関数 $y = «a»x «bs»$ で、$x$ の値が $«p»$ から $«q»$ まで増加するとき、$y$ の増加量を答えよ。", a=a, bs=sg(b), p=p, q=q), a * (q - p),
               fmt("増加量 $= «a» \\times («q» - («p»)) = «r»$。", a=a, q=q, p=p, r=a * (q - p)))


def t_lin_cross():
    xs, ys = R.randint(-4, 6), R.randint(-6, 8); a, c = R.choice([-3, -2, -1, 1, 2, 3]), R.choice([-3, -2, -1, 1, 2, 3])
    if a == c: return False
    b, d = ys - a * xs, ys - c * xs
    return add(414, "junior", 2, "一次関数", fmt("2直線 $y = «e1»$ と $y = «e2»$ の交点の $x$ 座標を答えよ。", e1=eqn(a, b), e2=eqn(c, d)), xs,
               fmt("$«e1» = «e2»$ を解いて $x = «x»$。", e1=eqn(a, b), e2=eqn(c, d), x=xs))


def t_lin_area():
    a = R.choice([1, 2, 3, 4, -1, -2, -3]); b = R.choice([2, 4, 6, 8, 10, 12, -2, -4, -6])
    if a * b > 0: pass
    x0 = Fraction(-b, a)
    area = Fraction(abs(b)) * abs(x0) / 2
    if area.denominator != 1: return False
    return add(415, "junior", 3, "一次関数", fmt("直線 $y = «e»$ と、$x$ 軸、$y$ 軸で囲まれた三角形の面積を答えよ。", e=eqn(a, b)), int(area),
               fmt("$x$ 切片は $«x0»$、$y$ 切片は $«b»$。面積は $\\dfrac{1}{2} \\times «ax» \\times «ab» = «ar»$。", x0=("%s" % x0), b=b, ax=abs(x0), ab=abs(b), ar=int(area)))


# ═════════ 文字式の計算 ═════════
def t_like():
    a, b, c, d = R.randint(2, 9), R.randint(-9, 9), R.randint(-6, 7), R.randint(-9, 9)
    if c == 0 or b + d == 0: return False
    return add(421, "junior", 1, "文字式の計算", fmt("$(«a»x «bs») + («c»x «ds»)$ を計算したとき、$x$ の係数を答えよ。", a=a, bs=sg(b), c=c, ds=sg(d)), a + c,
               fmt("$x$ の項を足して $(«a» + «c»)x = «s»x$。", a=a, c=c, s=a + c))


def t_dist():
    a, b, c, d, e = R.randint(2, 5), R.randint(1, 6), R.randint(2, 4), R.randint(1, 6), R.randint(1, 5)
    # a(x + b) - c(x - d) + e = (a - c)x + (ab + cd + e)
    return add(422, "junior", 2, "文字式の計算", fmt("$«a»(x + «b») - «c»(x - «d») + «e»$ を計算すると $px + q$ となる。$p + q$ の値を答えよ。", a=a, b=b, c=c, d=d, e=e),
               (a - c) + (a * b + c * d + e),
               fmt("展開して $(«a» - «c»)x + («ab» + «cd» + «e»)$。$p = «p»$、$q = «q»$。", a=a, c=c, ab=a * b, cd=c * d, e=e, p=a - c, q=a * b + c * d + e))


def t_mono():
    k, m, a, b = R.randint(2, 5), R.randint(2, 4), R.randint(1, 4), R.randint(1, 4)
    # (k*m a² b) ÷ (m a b) = k a。a=a のときの値
    return add(423, "junior", 2, "文字式の計算", fmt("$a = «a»$ のとき、$«km»a^2b \\div «m»ab$ の値を答えよ。", a=a, km=k * m, m=m), k * a,
               fmt("約分すると $«k»a$。$a = «a»$ を代入して $«v»$。", k=k, a=a, v=k * a))


def t_trans():
    a, b, c, x = R.randint(2, 6), R.randint(2, 6), None, R.randint(1, 5)
    y = R.randint(1, 9); c = a * x + b * y
    return add(424, "junior", 1, "文字式の計算", fmt("$«a»x + «b»y = «c»$ を $y$ について解いた式で、$x = «x»$ のときの $y$ の値を答えよ。", a=a, b=b, c=c, x=x), y,
               fmt("$y = \\dfrac{«c» - «a»x}{«b»}$ に $x = «x»$ を代入して $y = «y»$。", c=c, a=a, b=b, x=x, y=y))


# ═════════ 相似 ═════════
def t_sim_len():
    a, b = R.choice([(2, 3), (3, 4), (2, 5), (3, 5), (1, 2), (3, 7)]); k = R.randint(2, 6)
    return add(431, "junior", 1, "相似", fmt("相似比が $«a» : «b»$ の2つの三角形で、小さいほうの辺が $«s»$ cm のとき、対応する大きいほうの辺は何 cm か。", a=a, b=b, s=a * k), b * k,
               fmt("$«a» : «b» = «s» : x$ より $x = «x»$。", a=a, b=b, s=a * k, x=b * k))


def t_sim_area():
    a, b = R.choice([(1, 2), (2, 3), (1, 3), (2, 5), (3, 4)]); k = R.randint(1, 6)
    s = a * a * k
    return add(432, "junior", 2, "相似", fmt("相似比が $«a» : «b»$ の2つの図形で、小さいほうの面積が $«s»$ cm² のとき、大きいほうの面積は何 cm² か。", a=a, b=b, s=s), b * b * k,
               fmt("面積比は $«a2» : «b2»$。大きいほうは $«s» \\times \\dfrac{«b2»}{«a2»} = «x»$。", a2=a * a, b2=b * b, s=s, x=b * b * k))


def t_sim_vol():
    a, b = R.choice([(1, 2), (2, 3), (1, 3), (2, 5)]); k = R.randint(1, 5)
    return add(433, "junior", 3, "相似", fmt("相似比が $«a» : «b»$ の2つの立体で、小さいほうの体積が $«s»$ cm³ のとき、大きいほうの体積は何 cm³ か。", a=a, b=b, s=a ** 3 * k), b ** 3 * k,
               fmt("体積比は $«a3» : «b3»$。大きいほうは $«x»$。", a3=a ** 3, b3=b ** 3, x=b ** 3 * k))


def t_parallel():
    a, b = R.randint(1, 5), R.randint(1, 5); k = R.randint(2, 6)
    # AD:DB = a:b, DE // BC なら DE:BC = a:(a+b)。BC = (a+b)k → DE = a k
    return add(434, "junior", 2, "相似", fmt("三角形 $\\mathrm{ABC}$ で、辺 $\\mathrm{AB}$、$\\mathrm{AC}$ 上の点 $\\mathrm{D}$、$\\mathrm{E}$ について $\\mathrm{DE} \\parallel \\mathrm{BC}$、$\\mathrm{AD} : \\mathrm{DB} = «a» : «b»$、$\\mathrm{BC} = «bc»$ のとき、$\\mathrm{DE}$ の長さを答えよ。", a=a, b=b, bc=(a + b) * k), a * k,
               fmt("$\\mathrm{AD} : \\mathrm{AB} = «a» : «ab»$ なので $\\mathrm{DE} = «bc» \\times \\dfrac{«a»}{«ab»} = «de»$。", a=a, ab=a + b, bc=(a + b) * k, de=a * k))


# ═════════ 円と角 ═════════
def t_inscribed():
    c = R.choice([40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150])
    return add(441, "junior", 1, "円周角", fmt("1つの弧に対する中心角が $«c»^\\circ$ のとき、同じ弧に対する円周角は何度か。", c=c), c // 2,
               fmt("円周角は中心角の半分なので $«c» \\div 2 = «a»$ 度。", c=c, a=c // 2))


def t_semicircle():
    a = R.randint(20, 70)
    return add(442, "junior", 1, "円周角", fmt("$\\mathrm{AB}$ を直径とする円の周上に点 $\\mathrm{C}$ をとる。$\\angle \\mathrm{CAB} = «a»^\\circ$ のとき、$\\angle \\mathrm{ABC}$ は何度か。", a=a), 90 - a,
               fmt("直径に対する円周角は $90^\\circ$。三角形の内角の和より $180 - 90 - «a» = «b»$ 度。", a=a, b=90 - a))


def t_arc():
    r = R.randint(2, 12); th = R.choice([30, 45, 60, 90, 120, 180, 270])
    l = Fraction(2 * r * th, 360)
    if l.denominator != 1: return False
    return add(443, "junior", 2, "円周角", fmt("半径 $«r»$ cm、中心角 $«th»^\\circ$ のおうぎ形の弧の長さは $k\\pi$ cm である。$k$ の値を答えよ。", r=r, th=th), int(l),
               fmt("$2\\pi \\times «r» \\times \\dfrac{«th»}{360} = «k»\\pi$。", r=r, th=th, k=int(l)))


def t_sector():
    r = R.randint(2, 12); th = R.choice([30, 45, 60, 90, 120, 180, 270, 40, 72])
    s = Fraction(r * r * th, 360)
    if s.denominator != 1: return False
    return add(444, "junior", 2, "円周角", fmt("半径 $«r»$ cm、中心角 $«th»^\\circ$ のおうぎ形の面積は $k\\pi$ cm² である。$k$ の値を答えよ。", r=r, th=th), int(s),
               fmt("$\\pi \\times «r»^2 \\times \\dfrac{«th»}{360} = «k»\\pi$。", r=r, th=th, k=int(s)))


def t_cyclic():
    a = R.randint(50, 130)
    return add(445, "junior", 2, "円周角", fmt("円に内接する四角形で、1つの内角が $«a»^\\circ$ のとき、その向かいにある内角は何度か。", a=a), 180 - a,
               fmt("円に内接する四角形の向かい合う角の和は $180^\\circ$。$180 - «a» = «b»$ 度。", a=a, b=180 - a))


# ═════════ 空間図形 ═════════
def t_cyl():
    r, h = R.randint(2, 9), R.randint(2, 12)
    return add(451, "junior", 1, "立体の体積と表面積", fmt("底面の半径が $«r»$ cm、高さが $«h»$ cm の円柱の体積は $k\\pi$ cm³ である。$k$ の値を答えよ。", r=r, h=h), r * r * h,
               fmt("$\\pi r^2 h = \\pi \\times «r»^2 \\times «h» = «k»\\pi$。", r=r, h=h, k=r * r * h))


def t_cone():
    r, h = R.randint(2, 9), R.randint(3, 12)
    if (r * r * h) % 3: return False
    return add(452, "junior", 2, "立体の体積と表面積", fmt("底面の半径が $«r»$ cm、高さが $«h»$ cm の円錐の体積は $k\\pi$ cm³ である。$k$ の値を答えよ。", r=r, h=h), r * r * h // 3,
               fmt("$\\dfrac{1}{3}\\pi r^2 h = \\dfrac{1}{3}\\pi \\times «r»^2 \\times «h» = «k»\\pi$。", r=r, h=h, k=r * r * h // 3))


def t_cyl_surf():
    r, h = R.randint(2, 9), R.randint(2, 10)
    return add(453, "junior", 2, "立体の体積と表面積", fmt("底面の半径が $«r»$ cm、高さが $«h»$ cm の円柱の表面積は $k\\pi$ cm² である。$k$ の値を答えよ。", r=r, h=h), 2 * r * r + 2 * r * h,
               fmt("底面2つ $2\\pi r^2 = «a»\\pi$、側面 $2\\pi r h = «b»\\pi$。合計 $«k»\\pi$。", a=2 * r * r, b=2 * r * h, k=2 * r * r + 2 * r * h))


def t_prism():
    n = R.randint(3, 8); kind = R.choice(["面", "辺", "頂点"])
    ans = {"面": n + 2, "辺": 3 * n, "頂点": 2 * n}[kind]
    return add(454, "junior", 1, "立体の体積と表面積", fmt("$«n»$ 角柱の«kind»の数を答えよ。", n=n, kind=kind), ans,
               fmt("$«n»$ 角柱は、面が $«f»$、辺が $«e»$、頂点が $«v»$。", n=n, f=n + 2, e=3 * n, v=2 * n))


# ═════════ データの活用・平均 ═════════
def _data(n, lo=1, hi=20):
    return [R.randint(lo, hi) for _ in range(n)]


def t_mean():
    n = R.randint(4, 7); data = _data(n - 1, 3, 20); s = R.randint(4, 15) * n
    last = s - sum(data)
    if not 1 <= last <= 30: return False
    d = data + [last]
    return add(461, "junior", 1, "平均値と中央値", fmt("$«d»$ の平均値を答えよ。", d=",\\ ".join(map(str, d))), s // n,
               fmt("合計 $«s»$ を個数 $«n»$ でわって $«m»$。", s=s, n=n, m=s // n))


def t_median():
    n = R.choice([5, 7, 9]); d = _data(n, 1, 30)
    if len(set(d)) < n: return False
    return add(462, "junior", 1, "平均値と中央値", fmt("$«d»$ の中央値（メジアン）を答えよ。", d=",\\ ".join(map(str, d))), int(statistics.median(d)),
               fmt("小さい順に並べると $«s»$。真ん中の値は $«m»$。", s=",\\ ".join(map(str, sorted(d))), m=int(statistics.median(d))))


def t_mode():
    d = _data(R.randint(7, 10), 1, 6)
    cnt = {v: d.count(v) for v in set(d)}; m = max(cnt.values())
    if list(cnt.values()).count(m) != 1: return False
    mode = [v for v, c in cnt.items() if c == m][0]
    return add(463, "junior", 1, "平均値と中央値", fmt("$«d»$ の最頻値（モード）を答えよ。", d=",\\ ".join(map(str, d))), mode,
               fmt("いちばん多く出てくる値は $«m»$（$«c»$ 回）。", m=mode, c=m))


def t_range():
    d = _data(R.randint(6, 9), 1, 50)
    return add(464, "junior", 1, "平均値と中央値", fmt("$«d»$ の範囲（レンジ）を答えよ。", d=",\\ ".join(map(str, d))), max(d) - min(d),
               fmt("最大値 $«a»$ − 最小値 $«b»$ $= «r»$。", a=max(d), b=min(d), r=max(d) - min(d)))


def t_mean_back():
    n, m = R.randint(3, 6), R.randint(60, 90); k = R.randint(2, 4)
    # 平均 m の n 人。あと k 人（平均 m2）が加わると全体の平均は？ → 整数になるよう設計
    m2 = R.randint(50, 95); tot = n * m + k * m2
    if tot % (n + k) or m2 == m: return False
    return add(465, "junior", 2, "平均値と中央値", fmt("$«n»$ 人の平均点が $«m»$ 点、$«k»$ 人の平均点が $«m2»$ 点のとき、$«N»$ 人全体の平均点は何点か。", n=n, m=m, k=k, m2=m2, N=n + k), tot // (n + k),
               fmt("合計は $«n» \\times «m» + «k» \\times «m2» = «t»$。$«t» \\div «N» = «a»$。", n=n, m=m, k=k, m2=m2, t=tot, N=n + k, a=tot // (n + k)))


# ═════════ 数列の応用・微分の応用・図形の性質・統計・複素数 ═════════
def t_diff_seq():
    a1, d, k = R.randint(1, 5), R.randint(1, 4), R.randint(5, 8)
    # 階差数列 b_n = d*n + e
    e = R.randint(-1, 3)
    seq = [a1]
    for n in range(1, k): seq.append(seq[-1] + d * n + e)
    return add(471, "math2b", 2, "階差数列", fmt("数列 $\\{a_n\\}$ は $a_1 = «a1»$、$a_{n+1} - a_n = «d»n «es»$ を満たす。$a_{«k»}$ の値を答えよ。", a1=a1, d=d, es=sg(e), k=k), seq[-1],
               fmt("階差を順に足して、$a_{«k»} = «a1» + \\sum_{n=1}^{«k1»}(«d»n «es»)= «v»$。", k=k, a1=a1, k1=k - 1, d=d, es=sg(e), v=seq[-1]))


def t_arith_sum():
    a, d, n = R.randint(1, 9), R.randint(1, 6), R.randint(5, 15)
    return add(472, "math2b", 1, "階差数列", fmt("初項 $«a»$、公差 $«d»$ の等差数列の、初項から第 $«n»$ 項までの和を答えよ。", a=a, d=d, n=n), n * (2 * a + (n - 1) * d) // 2,
               fmt("$S_n = \\dfrac{n(2a + (n - 1)d)}{2} = \\dfrac{«n» \\times «t»}{2} = «s»$。", n=n, t=2 * a + (n - 1) * d, s=n * (2 * a + (n - 1) * d) // 2))


def t_geo_term():
    a, r, n = R.randint(1, 4), R.choice([2, 3]), R.randint(4, 7)
    return add(473, "math2b", 2, "階差数列", fmt("初項 $«a»$、公比 $«r»$ の等比数列の第 $«n»$ 項を答えよ。", a=a, r=r, n=n), a * r ** (n - 1),
               fmt("$a_n = «a» \\times «r»^{«n1»} = «v»$。", a=a, r=r, n1=n - 1, v=a * r ** (n - 1)))


def t_tangent():
    a, b, c, p = R.randint(1, 3), R.randint(-4, 4), R.randint(-5, 5), R.randint(-3, 4)
    f = a * X ** 2 + b * X + c
    return add(481, "math2b", 1, "微分の応用", fmt("曲線 $y = «e»$ 上の $x = «p»$ の点における接線の傾きを答えよ。", e=G.poly([(a, "x^2"), (b, "x"), (c, "")]), p=p), int(sp.diff(f, X).subs(X, p)),
               fmt("$y' = «d»$ に $x = «p»$ を代入して $«v»$。", d=G.poly([(2 * a, "x"), (b, "")]), p=p, v=int(sp.diff(f, X).subs(X, p))))


def t_tan_int():
    a, p = R.randint(1, 3), R.randint(-3, 3); b, c = R.randint(-4, 4), R.randint(-5, 5)
    f = a * X ** 2 + b * X + c
    slope = int(sp.diff(f, X).subs(X, p)); y0 = int(f.subs(X, p))
    return add(482, "math2b", 2, "微分の応用", fmt("曲線 $y = «e»$ の $x = «p»$ における接線の $y$ 切片を答えよ。", e=G.poly([(a, "x^2"), (b, "x"), (c, "")]), p=p), y0 - slope * p,
               fmt("接線は $y - «y0» = «m»(x - («p»))$。$x = 0$ とすると $y = «v»$。", y0=y0, m=slope, p=p, v=y0 - slope * p))


def t_cubic_ext():
    a = R.randint(1, 4); f = X ** 3 - 3 * a * a * X
    return add(483, "math2b", 3, "微分の応用", fmt("関数 $f(x) = x^3 - «c»x$ の極大値を答えよ。", c=3 * a * a), int(f.subs(X, -a)),
               fmt("$f'(x) = 3x^2 - «c»= 0$ より $x = \\pm «a»$。極大値は $f(-«a») = «v»$。", c=3 * a * a, a=a, v=int(f.subs(X, -a))))


def t_max_quad():
    b, c = R.choice([2, 4, 6, 8, 10]), R.randint(-5, 9); f = -X ** 2 + b * X + c
    return add(484, "math2b", 2, "微分の応用", fmt("関数 $f(x) = -x^2 «bs»x «cs»$ の最大値を答えよ。", bs=sg(b), cs=sg(c)), int(f.subs(X, b // 2)),
               fmt("$f'(x) = -2x + «b» = 0$ より $x = «x»$。最大値は $f(«x») = «v»$。", b=b, x=b // 2, v=int(f.subs(X, b // 2))))


def t_bisector():
    # 三角形が成り立つ（|AB − AC| < BC < AB + AC）ように BC を選び、BD = BC · AB ÷ (AB + AC) が整数になる組だけを使う
    cands = [(a, b, bc) for a in range(2, 13) for b in range(2, 13) if a != b
             for bc in range(abs(a - b) + 1, a + b) if (bc * a) % (a + b) == 0]
    a, b, bc = R.choice(cands)
    bd = bc * a // (a + b)
    return add(491, "math1a", 2, "角の二等分線", fmt("三角形 $\\mathrm{ABC}$ で、$\\angle \\mathrm{A}$ の二等分線が辺 $\\mathrm{BC}$ と点 $\\mathrm{D}$ で交わる。$\\mathrm{AB} = «a»$、$\\mathrm{AC} = «b»$、$\\mathrm{BC} = «bc»$ のとき、$\\mathrm{BD}$ の長さを答えよ。", a=a, b=b, bc=bc), bd,
               fmt("$\\mathrm{BD} : \\mathrm{DC} = \\mathrm{AB} : \\mathrm{AC} = «a» : «b»$。$\\mathrm{BD} = «bc» \\times \\dfrac{«a»}{«ab»} = «bd»$。", a=a, b=b, bc=bc, ab=a + b, bd=bd))


def t_power_pt():
    pa, pb = R.randint(2, 6), R.randint(2, 8); prod = pa * pb
    if pa >= pb: return False
    divs = [d for d in range(1, prod + 1) if prod % d == 0 and d not in (pa, pb) and d > 1]
    if not divs: return False
    pc = R.choice(divs)
    if pc >= prod // pc: return False
    return add(492, "math1a", 2, "方べきの定理", fmt("円の外の点 $\\mathrm{P}$ から2本の直線を引き、円との交点をそれぞれ $\\mathrm{A}$、$\\mathrm{B}$ と $\\mathrm{C}$、$\\mathrm{D}$ とする（$\\mathrm{PA} < \\mathrm{PB}$、$\\mathrm{PC} < \\mathrm{PD}$）。$\\mathrm{PA} = «pa»$、$\\mathrm{PB} = «pb»$、$\\mathrm{PC} = «pc»$ のとき、$\\mathrm{PD}$ の長さを答えよ。", pa=pa, pb=pb, pc=pc), prod // pc,
               fmt("方べきの定理 $\\mathrm{PA} \\cdot \\mathrm{PB} = \\mathrm{PC} \\cdot \\mathrm{PD}$ より $«p» = «pc» \\times \\mathrm{PD}$。$\\mathrm{PD} = «pd»$。", p=prod, pc=pc, pd=prod // pc))


def t_incircle():
    a, b, c = R.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17)])
    return add(493, "math1a", 2, "三角形の性質", fmt("直角をはさむ2辺が $«a»$、$«b»$ で、斜辺が $«c»$ の直角三角形の内接円の半径を答えよ。", a=a, b=b, c=c), (a + b - c) // 2,
               fmt("面積を2通りに表すと $\\dfrac{1}{2}«a»«b» = \\dfrac{1}{2}r(«a» + «b» + «c»)$。$r = «r»$。", a=a, b=b, c=c, r=(a + b - c) // 2))


def t_variance():
    d = _data(R.randint(4, 6), 1, 12); n = len(d); m = Fraction(sum(d), n)
    var = sum((Fraction(x) - m) ** 2 for x in d) / n
    if m.denominator != 1 or var.denominator != 1: return False
    return add(501, "math1a", 2, "データの分散", fmt("$«d»$ の分散を答えよ。", d=",\\ ".join(map(str, d))), int(var),
               fmt("平均は $«m»$。偏差の2乗の平均は $«v»$。", m=int(m), v=int(var)))


def t_stdev():
    s = R.randint(1, 6); d = [10 - s, 10 + s, 10 - s, 10 + s]
    return add(502, "math1a", 2, "データの分散", fmt("$«d»$ の標準偏差を答えよ。", d=",\\ ".join(map(str, d))), s,
               fmt("平均は $10$、偏差はすべて $\\pm «s»$。分散は $«v»$、標準偏差は $«s»$。", s=s, v=s * s))


def t_quartile():
    d = sorted(R.randint(1, 40) for _ in range(8))
    if len(set(d)) < 8: return False
    lo, hi = d[:4], d[4:]
    q1, q3 = Fraction(lo[1] + lo[2], 2), Fraction(hi[1] + hi[2], 2)
    if q1.denominator != 1 or q3.denominator != 1: return False
    return add(503, "math1a", 2, "データの分散", fmt("$«d»$ の四分位範囲（第3四分位数 $-$ 第1四分位数）を答えよ。", d=",\\ ".join(map(str, d))), int(q3 - q1),
               fmt("下半分の中央値 $Q_1 = «q1»$、上半分の中央値 $Q_3 = «q3»$。四分位範囲は $«r»$。", q1=int(q1), q3=int(q3), r=int(q3 - q1)))


def t_var_formula():
    m, v = R.randint(3, 12), R.randint(1, 9)
    return add(504, "math1a", 2, "データの分散", fmt("あるデータの平均が $«m»$、2乗の平均が $«s»$ のとき、分散を答えよ。", m=m, s=m * m + v), v,
               fmt("分散 $=$ （2乗の平均）$-$（平均）$^2$ $= «s» - «m2» = «v»$。", s=m * m + v, m2=m * m, v=v))


def t_complex_mul():
    a, b, c, d = [R.choice([-4, -3, -2, -1, 1, 2, 3, 4, 5]) for _ in range(4)]
    z = sp.expand((a + b * sp.I) * (c + d * sp.I)); re, im = int(sp.re(z)), int(sp.im(z))
    return add(511, "math2b", 1, "複素数の計算", fmt("$(«a» «bs»i)(«c» «ds»i)$ を計算したとき、実部を答えよ。", a=a, bs=sg(b), c=c, ds=sg(d)), re,
               fmt("展開して $i^2 = -1$ を使うと、実部は $«a» \\times «c» - «b» \\times «d» = «re»$。", a=a, b=b, c=c, d=d, re=re))


def t_imag_pow():
    n = R.randint(5, 40); val = [1, sp.I, -1, -sp.I][n % 4]
    cs = {0: "1", 1: "i", 2: "-1", 3: "-i"}[n % 4]
    # 4択ではなく、 i^n の実部と虚部の和: 1→1, i→1, -1→-1, -i→-1
    ans = int(sp.re(val) + sp.im(val))
    return add(512, "math2b", 2, "複素数の計算", fmt("$i^{«n»}$ の実部と虚部の和を答えよ。ただし $i^2 = -1$ とする。", n=n), ans,
               fmt("$i^4 = 1$ より、$«n»$ を $4$ でわったあまり $«r»$ で考えて $i^{«n»} = «cs»$。", n=n, r=n % 4, cs=cs))


def t_root_coef():
    p, q = R.randint(-9, 9), R.randint(-9, 9)
    return add(513, "math2b", 2, "複素数の計算", fmt("二次方程式 $«e» = 0$ の2つの解を $\\alpha$、$\\beta$ とするとき、$\\alpha^2 + \\beta^2$ の値を答えよ。", e=G.poly([(1, "x^2"), (p, "x"), (q, "")])), p * p - 2 * q,
               fmt("解と係数の関係より $\\alpha + \\beta = «s»$、$\\alpha\\beta = «m»$。$(\\alpha + \\beta)^2 - 2\\alpha\\beta = «a»$。", s=-p, m=q, a=p * p - 2 * q))


def t_e_avg1():
    n = R.randint(3, 6); m = R.randint(5, 40); s = n * m
    d = [R.randint(1, 2 * m - 1) for _ in range(n - 1)]; last = s - sum(d)
    if not 1 <= last <= 3 * m: return False
    d.append(last)
    return add(521, "elem", 1, "平均", fmt("$«d»$ の平均を答えよ。", d=",\\ ".join(map(str, d))), m,
               fmt("合計 $«s»$ を個数 $«n»$ でわって $«m»$。", s=s, n=n, m=m))


def t_e_avg2():
    n, m = R.randint(3, 8), R.randint(10, 80)
    return add(522, "elem", 2, "平均", fmt("$«n»$ 回のテストの平均点が $«m»$ 点だった。合計点は何点か。", n=n, m=m), n * m,
               fmt("合計 $=$ 平均 $\\times$ 個数 なので $«m» \\times «n» = «t»$ 点。", m=m, n=n, t=n * m))


def t_e_avg3():
    n, m, nxt = R.randint(3, 6), R.randint(60, 80), R.randint(81, 100)
    tot = (n + 1) * (m + 2) - n * m
    return add(523, "elem", 3, "平均", fmt("$«n»$ 回のテストの平均点が $«m»$ 点だった。次のテストで何点とると、$«n1»$ 回の平均が $«m2»$ 点になるか。", n=n, m=m, n1=n + 1, m2=m + 2), tot,
               fmt("$«n1»$ 回の合計は $«n1» \\times «m2» = «a»$、これまでの合計は $«n» \\times «m» = «b»$。差の $«t»$ 点。", n1=n + 1, m2=m + 2, a=(n + 1) * (m + 2), n=n, m=m, b=n * m, t=tot))


INTEGER_TEMPLATES = [t_quartile, t_var_formula, t_e_avg1, t_e_avg2, t_e_avg3, t_prop1, t_prop2, t_inv1, t_inv2, t_prop_word, t_lin_val, t_lin_int, t_lin_rate, t_lin_cross, t_lin_area,
                     t_like, t_dist, t_mono, t_trans, t_sim_len, t_sim_area, t_sim_vol, t_parallel,
                     t_inscribed, t_semicircle, t_arc, t_sector, t_cyclic, t_cyl, t_cone, t_cyl_surf, t_prism,
                     t_mean, t_median, t_mode, t_range, t_mean_back,
                     t_diff_seq, t_arith_sum, t_geo_term, t_tangent, t_tan_int, t_cubic_ext, t_max_quad,
                     t_bisector, t_power_pt, t_incircle, t_variance, t_stdev, t_complex_mul, t_imag_pow, t_root_coef]


def generate(per_template=8):
    G.OUT.clear(); G._seen.clear()
    for fn in INTEGER_TEMPLATES: make(0, per_template, fn)
    return list(G.OUT)


if __name__ == "__main__":
    ps = generate()
    print(len(ps), "問")
    import collections
    print(sorted(collections.Counter(p["title"] for p in ps).items()))
    for p in ps[::10]: print(p["id"], p["title"], "|", p["plain"][:80], "->", p["answer"])
