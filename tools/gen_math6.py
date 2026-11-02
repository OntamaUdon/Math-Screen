"""展開と因数分解の公式、二次方程式の利用、三平方の定理の利用、微積の応用（面積・速度）。数字を変えて作る問題。"""
from fractions import Fraction
from math import gcd, isqrt
import sympy as sp
import gen_problems as G
from gen_problems import fmt, add, make, poly

R = G.Rng(20261109)
X = sp.Symbol("x")


def sg(n):
    return ("+ %d" % n) if n >= 0 else ("- %d" % -n)


# ═════════ 展開と因数分解の公式 ═════════
def t_sq_mid():
    a = R.choice([-9, -8, -7, -6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 7, 8, 9])
    return add(701, "junior", 1, "展開と因数分解の公式", fmt("$(x «as»)^2$ を展開したとき、$x$ の係数を答えよ。", as_=None, **{"as": sg(a)}), 2 * a,
               fmt("$(x + a)^2 = x^2 + 2ax + a^2$ より、$x$ の係数は $2 \\times («a») = «r»$。", a=a, r=2 * a))


def t_sq_const():
    a = R.choice([-9, -8, -7, -6, -5, -4, -3, 3, 4, 5, 6, 7, 8, 9])
    return add(702, "junior", 1, "展開と因数分解の公式", fmt("$(x «as»)^2$ を展開したとき、定数項を答えよ。", **{"as": sg(a)}), a * a,
               fmt("定数項は $(«a»)^2 = «r»$。", a=a, r=a * a))


def t_diff_sq():
    a = R.randint(2, 15)
    return add(703, "junior", 1, "展開と因数分解の公式", fmt("$(x + «a»)(x - «a»)$ を展開したとき、定数項を答えよ。", a=a), -a * a,
               fmt("和と差の積の公式より $x^2 - «a2»$。定数項は $-«a2»$。", a2=a * a))


def t_factor_diff():
    a = R.randint(2, 15)
    return add(704, "junior", 1, "展開と因数分解の公式", fmt("$x^2 - «n»$ を因数分解すると $(x + a)(x - a)$ となる。$a$ の値を答えよ。", n=a * a), a,
               fmt("$«n» = «a»^2$ なので $(x + «a»)(x - «a»)$。", n=a * a, a=a))


def t_factor_sq():
    a = R.randint(2, 12)
    return add(705, "junior", 2, "展開と因数分解の公式", fmt("$x^2 + «m»x + «n»$ を因数分解すると $(x + a)^2$ となる。$a$ の値を答えよ。", m=2 * a, n=a * a), a,
               fmt("$(x + a)^2 = x^2 + 2ax + a^2$ と比べて $a = «a»$。", a=a))


def t_calc_sq():
    n = R.choice([99, 98, 101, 102, 97, 103, 199, 201, 49, 51, 29, 31]); base = round(n, -1) if n < 100 else round(n, -2)
    d = n - base
    return add(706, "junior", 2, "展開と因数分解の公式", fmt("$«n»^2$ を、くふうして計算せよ。", n=n), n * n,
               fmt("$(«b» «ds»)^2 = «b»^2 «ds2»\\times«b» + «d2» = «r»$。", b=base, ds=sg(d), ds2=sg(2 * d), d2=d * d, r=n * n))


def t_calc_prod():
    k = R.choice([10, 20, 30, 50, 100]); a = R.randint(1, 5)
    if a >= k: return False
    return add(707, "junior", 2, "展開と因数分解の公式", fmt("$«p» \\times «q»$ を、くふうして計算せよ。", p=k + a, q=k - a), k * k - a * a,
               fmt("$(«k» + «a»)(«k» - «a») = «k»^2 - «a»^2 = «r»$。", k=k, a=a, r=k * k - a * a))


def t_expr_val():
    a = R.randint(2, 9); b = R.randint(1, 9)
    x, y = a + b, a - b
    # x = a+b, y = a-b のとき x² - y² = 4ab
    return add(708, "junior", 2, "展開と因数分解の公式", fmt("$x = «x»$、$y = «y»$ のとき、$x^2 - y^2$ の値を答えよ。", x=x, y=y), x * x - y * y,
               fmt("$x^2 - y^2 = (x + y)(x - y) = «s» \\times «d» = «r»$。", s=x + y, d=x - y, r=x * x - y * y))


# ═════════ 二次方程式の利用 ═════════
def t_consec():
    n = R.randint(3, 15)
    return add(711, "junior", 2, "二次方程式の利用", fmt("連続する2つの正の整数があり、その積が $«p»$ である。小さいほうの整数を答えよ。", p=n * (n + 1)), n,
               fmt("小さいほうを $x$ とすると $x(x + 1) = «p»$。$x^2 + x - «p» = 0$ を解いて $x = «n»$。", p=n * (n + 1), n=n))


def t_rect():
    w = R.randint(3, 12); d = R.randint(1, 6)
    return add(712, "junior", 2, "二次方程式の利用", fmt("長方形で、たてがよこより $«d»$ cm 短く、面積が $«s»$ cm² のとき、たての長さは何 cm か。", d=d, s=w * (w - d)) if w - d > 0 else "", w - d,
               fmt("たてを $x$ とすると $x(x + «d») = «s»$。解いて $x = «x»$。", d=d, s=w * (w - d), x=w - d)) if w - d > 0 else False


def t_square_num():
    n = R.randint(3, 12); k = R.randint(1, 6)
    # ある正の数 x を2乗した数が、x の (k+n) 倍より... 単純に x² = a x + b 型
    a = R.randint(1, 5)
    x = R.randint(3, 12)
    b = x * x - a * x
    if b <= 0: return False
    return add(713, "junior", 2, "二次方程式の利用", fmt("ある正の数 $x$ を2乗して、$x$ の $«a»$ 倍をひくと $«b»$ になった。$x$ の値を答えよ。", a=a, b=b), x,
               fmt("$x^2 - «a»x = «b»$。$x^2 - «a»x - «b» = 0$ を解いて $x = «x»$。", a=a, b=b, x=x))


def t_path():
    w, h, p = R.randint(8, 15), R.randint(6, 12), R.randint(1, 3)
    return add(714, "junior", 3, "二次方程式の利用", fmt("たて $«h»$ m、よこ $«w»$ m の長方形の土地の中に、まわりに同じ幅の道をつけた。道を除いた内側の面積が $«s»$ m² のとき、道の幅は何 m か。", w=w + 2 * p, h=h + 2 * p, s=w * h), p,
               fmt("道の幅を $x$ とすると $(«w2» - 2x)(«h2» - 2x) = «s»$。解いて $x = «p»$。", w2=w + 2 * p, h2=h + 2 * p, s=w * h, p=p))


def t_ball():
    a = R.randint(2, 6); t = R.randint(2, 6)
    return add(715, "junior", 2, "二次方程式の利用", fmt("ボールを投げ上げたとき、$x$ 秒後の高さ $y$ m は $y = «a»x - x^2$ で表される。ボールが地面に落ちるのは何秒後か。ただし $x > 0$ とする。", a=a + t) if False else fmt("ボールを投げ上げたとき、$x$ 秒後の高さ $y$ m は $y = «a»x - x^2$ で表される。ボールが地面に落ちるのは何秒後か。ただし $x > 0$ とする。", a=a), a,
               fmt("$y = 0$ のとき $x(«a» - x) = 0$。$x > 0$ より $x = «a»$。", a=a))


# ═════════ 三平方の定理の利用 ═════════
def t_diag():
    a = R.randint(2, 12)
    return add(721, "junior", 2, "三平方の定理の利用", fmt("対角線の長さが $«d»\\sqrt{2}$ の正方形の1辺の長さを答えよ。", d=a), a,
               fmt("1辺を $x$ とすると対角線は $\\sqrt{2}\\,x$。$x = «a»$。", a=a))


def t_equi_h():
    a = R.randint(2, 10)
    return add(722, "junior", 2, "三平方の定理の利用", fmt("1辺の長さが $«s»$ の正三角形の高さは $k\\sqrt{3}$ である。$k$ の値を答えよ。", s=2 * a), a,
               fmt("高さは $\\dfrac{\\sqrt{3}}{2}$ 倍なので $«a»\\sqrt{3}$。", a=a))


def t_ladder():
    a, b, c = R.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10), (9, 12, 15)]); k = R.randint(1, 3)
    return add(723, "junior", 2, "三平方の定理の利用", fmt("長さ $«c»$ m のはしごを、かべから $«a»$ m はなして立てかけた。はしごの先は地面から何 m の高さにあるか。", a=a * k, c=c * k), b * k,
               fmt("$\\sqrt{«c»^2 - «a»^2} = «b»$ m。", a=a * k, c=c * k, b=b * k))


def t_cube_diag():
    a = R.randint(2, 10)
    return add(724, "junior", 3, "三平方の定理の利用", fmt("1辺の長さが $«a»$ の立方体の対角線の長さは $k\\sqrt{3}$ である。$k$ の値を答えよ。", a=a), a,
               fmt("立方体の対角線は $\\sqrt{3}\\,a = «a»\\sqrt{3}$。", a=a))


def t_cone_h():
    r, h, l = R.choice([(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17), (9, 12, 15)])
    return add(725, "junior", 3, "三平方の定理の利用", fmt("底面の半径が $«r»$、母線の長さが $«l»$ の円錐の高さを答えよ。", r=r, l=l), h,
               fmt("$\\sqrt{«l»^2 - «r»^2} = «h»$。", l=l, r=r, h=h))


# ═════════ 微積の応用 ═════════
def t_area_para():
    a = R.choice([2, 4, 6, 8, 10, 12]); area = Fraction(a ** 3, 6)
    if area.denominator != 1: return False
    return add(731, "math2b", 2, "面積と速度", fmt("放物線 $y = x(«a» - x)$ と $x$ 軸で囲まれた部分の面積を答えよ。", a=a), int(area),
               fmt("$\\displaystyle\\int_0^{«a»} x(«a» - x)\\,dx = \\dfrac{«a»^3}{6} = «r»$。", a=a, r=int(area)))


def t_area_curves():
    a = R.choice([2, 3, 4, 5, 6]); area = Fraction(a ** 3, 6)
    if area.denominator != 1: return False
    return add(732, "math2b", 3, "面積と速度", fmt("放物線 $y = x^2$ と直線 $y = «a»x$ で囲まれた部分の面積を答えよ。", a=a), int(area),
               fmt("交点は $x = 0,\\ «a»$。$\\displaystyle\\int_0^{«a»}(«a»x - x^2)\\,dx = \\dfrac{«a»^3}{6} = «r»$。", a=a, r=int(area)))


def t_area_cubic():
    a = R.choice([1, 2, 3, 4]); area = Fraction(a ** 4, 4)
    if area.denominator != 1: return False
    return add(733, "math2b", 2, "面積と速度", fmt("曲線 $y = x^3$ と $x$ 軸、直線 $x = «a»$ で囲まれた部分の面積を答えよ。", a=a), int(area),
               fmt("$\\displaystyle\\int_0^{«a»} x^3\\,dx = \\dfrac{«a»^4}{4} = «r»$。", a=a, r=int(area)))


def t_velocity():
    a, b = R.randint(1, 5), R.randint(1, 6); t = R.randint(2, 6)
    pos = a * t ** 2 + b * t
    return add(734, "math2b", 2, "面積と速度", fmt("原点を出発した点 P の、時刻 $t$ における速度が $v = «v»$ である。$t = 0$ から $t = «t»$ までに進んだ道のり（位置の変化）を答えよ。", v=poly([(2 * a, "t"), (b, "")]), t=t), pos,
               fmt("$\\displaystyle\\int_0^{«t»}(«v»)\\,dt = «a»\\cdot«t»^2 + «b»\\cdot«t» = «r»$。", v=poly([(2 * a, "t"), (b, "")]), t=t, a=a, b=b, r=pos))


def t_def_int():
    a, b = R.randint(1, 4), R.randint(1, 6); p, q = R.randint(0, 2), R.randint(3, 5)
    f = a * X ** 2 + b
    val = sp.integrate(f, (X, p, q))
    if not val.is_Integer: return False
    return add(735, "math2b", 2, "面積と速度", fmt("定積分 $\\displaystyle\\int_{«p»}^{«q»}(«f»)\\,dx$ の値を答えよ。", p=p, q=q, f=poly([(a, "x^2"), (b, "")])), int(val),
               "不定積分を求めて、上端と下端の値の差をとる。")


INTEGER_TEMPLATES = [t_sq_mid, t_sq_const, t_diff_sq, t_factor_diff, t_factor_sq, t_calc_sq, t_calc_prod, t_expr_val,
                     t_consec, t_rect, t_square_num, t_path, t_ball,
                     t_diag, t_equi_h, t_ladder, t_cube_diag, t_cone_h,
                     t_area_para, t_area_curves, t_area_cubic, t_velocity, t_def_int]


def generate(per_template=8):
    G.OUT.clear(); G._seen.clear()
    for fn in INTEGER_TEMPLATES: make(0, per_template, fn)
    return list(G.OUT)


if __name__ == "__main__":
    ps = generate()
    import collections
    print(len(ps), collections.Counter(p["title"] for p in ps))
    for p in ps[::7]: print(p["id"], p["plain"][:90], "->", p["answer"])
