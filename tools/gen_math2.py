"""問題数が少ない単元を増やす、数字を変えて作る数学の問題（整数で答える問題と4択問題）。
tools/build_problems.py から呼ばれる。乱数は自前の線形合同法で、同じ問題が同じ順で出る。
正解は、別の方法（総当たり・sympy）でも確かめてから登録する。
"""
from fractions import Fraction
from math import gcd, isqrt, comb
import itertools
import sympy as sp
import gen_problems as G
from gen_problems import fmt, add, make, poly, lin

R = G.Rng(20261105)


def choice_set(correct, wrongs):
    opts = [correct]
    for w in wrongs:
        if w not in opts: opts.append(w)
    if len(opts) < 4: return None
    opts = opts[:4]
    R.shuffle(opts)
    return opts, opts.index(correct)


def frac_str(f):
    f = Fraction(f)
    return "$%d$" % f.numerator if f.denominator == 1 else "$\\dfrac{%d}{%d}$" % (f.numerator, f.denominator)


# ═════════ 中学：正負の数・式の値 ═════════
def t_signed_a():
    a, b, c = R.randint(2, 15), R.randint(2, 15), R.randint(2, 15)
    ans = -a - (-b) + c
    return add(201, "junior", 1, "正負の数", fmt("$(-«a») - (-«b») + «c»$ を計算せよ。", a=a, b=b, c=c), ans,
               fmt("$-«a» + «b» + «c» = «x»$。", a=a, b=b, c=c, x=ans))


def t_signed_b():
    c, q, b = R.randint(2, 9), R.randint(2, 9), R.randint(2, 9)
    a = c * q
    return add(202, "junior", 1, "正負の数", fmt("$(-«a») \\times «b» \\div (-«c»)$ を計算せよ。", a=a, b=b, c=c), (-a) * b // (-c),
               fmt("$(-«a») \\times «b» = -«p»$、$-«p» \\div (-«c») = «q2»$。", a=a, b=b, c=c, p=a * b, q2=a * b // c))


def t_signed_c():
    a, b = R.randint(2, 5), R.randint(2, 4)
    m = R.randint(1, 20)
    ans = (-a) ** 3 + b ** 2 * m
    return add(203, "junior", 2, "正負の数", fmt("$(-«a»)^3 + «b»^2 \\times «m»$ を計算せよ。", a=a, b=b, m=m), ans,
               fmt("$(-«a»)^3 = «x»$、$«b»^2 \\times «m» = «y»$。合計は $«z»$。", a=a, b=b, m=m, x=(-a) ** 3, y=b * b * m, z=ans))


def t_value_a():
    x, a, b, c = R.randint(-5, 5), R.randint(1, 4), R.randint(1, 9), R.randint(1, 9)
    ans = a * x * x - b * x + c
    return add(204, "junior", 1, "式の値", fmt("$x = «x»$ のとき、$«e»$ の値を答えよ。", x=x, e=poly([(a, "x^2"), (-b, "x"), (c, "")])), ans,
               fmt("$x = «x»$ を代入して $«a» \\times «x2» - «b» \\times («x») + «c» = «ans»$。", x=x, a=a, b=b, c=c, x2=x * x, ans=ans))


def t_value_b():
    x, y = R.randint(-6, 8), R.randint(-6, 8)
    if x == y or x == 0 or y == 0: return False
    ans = (x + y) ** 2 - x * y
    return add(205, "junior", 2, "式の値", fmt("$x = «x»$、$y = «y»$ のとき、$(x + y)^2 - xy$ の値を答えよ。", x=x, y=y), ans,
               fmt("$(«x» + («y»))^2 - («x»)\\times(«y») = «s2» - («p») = «ans»$。", x=x, y=y, s2=(x + y) ** 2, p=x * y, ans=ans))


# ═════════ 中学：方程式・不等式 ═════════
def t_linear_b():
    x = R.randint(-8, 10); a = R.randint(2, 6); b = R.randint(-6, 6)
    if b == 0: return False
    c = a * (x + b)
    return add(206, "junior", 1, "一次方程式", fmt("方程式 $«a»(x «bs») = «c»$ を解け。$x$ の値を答えよ。", a=a, bs=("+ %d" % b if b > 0 else "- %d" % -b), c=c), x,
               fmt("両辺を $«a»$ でわると $x «bs» = «q»$。よって $x = «x»$。", a=a, bs=("+ %d" % b if b > 0 else "- %d" % -b), q=c // a, x=x))


def t_linear_c():
    a, c = R.randint(2, 9), R.randint(1, 9)
    x = a * R.randint(-6, 8)
    if x == 0: return False
    b = R.randint(-5, 9)
    rhs = x // a + b
    if b == 0: return False
    return add(207, "junior", 1, "一次方程式", fmt("方程式 $\\dfrac{x}{«a»} «bs» = «r»$ を解け。$x$ の値を答えよ。", a=a, bs=("+ %d" % b if b > 0 else "- %d" % -b), r=rhs), x,
               fmt("$\\dfrac{x}{«a»} = «r» «bn»$ より $x = «x»$。", a=a, r=rhs, bn=("- %d" % b if b > 0 else "+ %d" % -b), x=x))


def t_linear_d():
    x = R.randint(2, 15); p, q = R.randint(2, 5), R.randint(2, 5)
    if p == q: return False
    # (x + a)/p = (x + b)/q を満たす x になるように a, b を決める
    a = R.randint(-5, 9); b = (x + a) * q // p - x
    if (x + a) * q % p != 0: return False
    assert Fraction(x + a, p) == Fraction(x + b, q)
    return add(208, "junior", 2, "一次方程式",
               fmt("方程式 $\\dfrac{x «a»}{«p»} = \\dfrac{x «b»}{«q»}$ を解け。$x$ の値を答えよ。", a=("+ %d" % a if a >= 0 else "- %d" % -a), b=("+ %d" % b if b >= 0 else "- %d" % -b), p=p, q=q), x,
               fmt("両辺に $«l»$ をかけて整理すると $x = «x»$。", l=p * q // gcd(p, q), x=x))


def t_simul_b():
    x, y = R.randint(1, 9), R.randint(1, 9)
    a, b = R.randint(2, 5), R.randint(2, 5)
    c, d = R.randint(1, 4), R.randint(1, 4)
    if a * d == b * c: return False
    return add(209, "junior", 2, "連立方程式",
               fmt("連立方程式 $«a»x + «b»y = «p»$、$«c»x - «d»y = «q»$ の解を $x = m$、$y = n$ とするとき、$m + n$ の値を答えよ。", a=a, b=b, c=c, d=d, p=a * x + b * y, q=c * x - d * y), x + y,
               fmt("2式から $y$ を消して解くと $x = «x»$、$y = «y»$。よって $m + n = «s»$。", x=x, y=y, s=x + y))


def t_simul_word():
    n, a, b = R.randint(8, 20), R.randint(80, 150), R.randint(100, 250)
    if a >= b: return False
    x = R.randint(2, n - 2)               # a 円の品の個数
    total = a * x + b * (n - x)
    return add(210, "junior", 2, "連立方程式",
               fmt("1個 $«a»$ 円のあめと、1個 $«b»$ 円のチョコを、合わせて $«n»$ 個買ったら、代金は $«t»$ 円だった。あめは何個買ったか。", a=a, b=b, n=n, t=total), x,
               fmt("あめを $x$ 個、チョコを $y$ 個とすると $x + y = «n»$、$«a»x + «b»y = «t»$。解くと $x = «x»$。", n=n, a=a, b=b, t=total, x=x))


def t_ineq_b():
    a, c = R.randint(2, 6), R.randint(10, 40); b = R.randint(-5, 8)
    # a*x + b < c  を満たす最大の整数 x
    top = max(x for x in range(-50, 50) if a * x + b < c)
    return add(211, "junior", 1, "不等式", fmt("不等式 $«a»x «bs» < «c»$ を満たす最大の整数 $x$ を答えよ。", a=a, bs=("+ %d" % b if b >= 0 else "- %d" % -b), c=c), top,
               fmt("$«a»x < «r»$ より $x < «f»$。これを満たす最大の整数は $«t»$。", a=a, r=c - b, f=frac_str(Fraction(c - b, a)).strip("$"), t=top))


def t_ineq_c():
    a, b = R.randint(-9, -1), R.randint(2, 9)
    lo, hi = a, b
    cnt = sum(1 for x in range(-50, 51) if lo <= x <= hi)
    return add(212, "junior", 2, "不等式", fmt("不等式 $«lo» \\le x \\le «hi»$ を満たす整数 $x$ は何個あるか。", lo=lo, hi=hi), cnt,
               fmt("$«lo»$ から $«hi»$ までの整数なので $«hi» - («lo») + 1 = «c»$ 個。", lo=lo, hi=hi, c=cnt))


# ═════════ 中学：式の計算・二次方程式 ═════════
def t_expand():
    a, b = R.randint(-9, 9), R.randint(-9, 9)
    if 0 in (a, b) or a == -b: return False
    return add(213, "junior", 1, "因数分解", fmt("$(x «a»)(x «b»)$ を展開したとき、$x$ の係数を答えよ。", a=("+ %d" % a if a > 0 else "- %d" % -a), b=("+ %d" % b if b > 0 else "- %d" % -b)), a + b,
               fmt("展開すると $x^2 «s»x «m»$ なので、$x$ の係数は $«ans»$。", s=("+ %d" % (a + b) if a + b > 0 else "- %d" % -(a + b)), m=("+ %d" % (a * b) if a * b > 0 else "- %d" % -(a * b)), ans=a + b))


def t_square_diff():
    m = R.randint(11, 60); d = R.choice([1, 2, 3, 4, 5, 6])
    n = m + d
    return add(214, "junior", 2, "因数分解", fmt("$«n»^2 - «m»^2$ を、くふうして計算せよ。", n=n, m=m), n * n - m * m,
               fmt("$a^2 - b^2 = (a + b)(a - b)$ より $(«n» + «m»)(«n» - «m») = «s» \\times «d» = «ans»$。", n=n, m=m, s=n + m, d=d, ans=n * n - m * m))


def t_quad_b():
    p, q = R.randint(-8, 9), R.randint(-8, 9)
    if p == q or 0 in (p, q): return False
    eq = poly([(1, "x^2"), (-(p + q), "x"), (p * q, "")])
    return add(215, "junior", 2, "二次方程式", fmt("二次方程式 $«eq» = 0$ の2つの解の積を答えよ。", eq=eq), p * q,
               fmt("解は $x = «p»,\\ «q»$。積は $«p» \\times («q») = «m»$。", p=p, q=q, m=p * q))


def t_quad_c():
    k = R.randint(2, 15)
    return add(216, "junior", 1, "二次方程式", fmt("二次方程式 $x^2 = «n»$ の、正の解を答えよ。", n=k * k), k,
               fmt("$x = \\pm\\sqrt{«n»} = \\pm «k»$。正の解は $«k»$。", n=k * k, k=k))


def t_quad_d():
    p, q = R.randint(-9, 9), R.randint(-9, 9)
    if p == q: return False
    eq = poly([(1, "x^2"), (-(p + q), "x"), (p * q, "")])
    if eq.strip() == "": return False
    return add(217, "junior", 2, "二次方程式", fmt("二次方程式 $«eq» = 0$ の2つの解の差（大きいほう $-$ 小さいほう）を答えよ。", eq=eq), abs(p - q),
               fmt("解は $x = «p»,\\ «q»$。差は $«d»$。", p=p, q=q, d=abs(p - q)))


# ═════════ 中学：関数・図形 ═════════
def t_func2_a():
    a = R.randint(1, 5); x = R.randint(-6, 6)
    if x == 0: return False
    return add(218, "junior", 1, "関数 y = ax²", fmt("関数 $y = «a»x^2$ で、$x = «x»$ のときの $y$ の値を答えよ。", a=a, x=x), a * x * x,
               fmt("$y = «a» \\times («x»)^2 = «y»$。", a=a, x=x, y=a * x * x))


def t_func2_b():
    a = R.randint(1, 4); p, q = R.randint(-4, 2), R.randint(3, 6)
    if p == q: return False
    return add(219, "junior", 2, "関数 y = ax²", fmt("関数 $y = «a»x^2$ で、$x$ の値が $«p»$ から $«q»$ まで増加するときの、変化の割合を答えよ。", a=a, p=p, q=q), a * (p + q),
               fmt("変化の割合は $\\dfrac{«a»(«q»^2 - («p»)^2)}{«q» - («p»)} = «a»(«q» + («p»)) = «ans»$。", a=a, p=p, q=q, ans=a * (p + q)))


def t_func2_c():
    a = R.randint(1, 5); x = R.randint(2, 6)
    return add(220, "junior", 2, "関数 y = ax²", fmt("関数 $y = ax^2$ のグラフが点 $(«x»,\\ «y»)$ を通るとき、$a$ の値を答えよ。", x=x, y=a * x * x), a,
               fmt("$«y» = a \\times «x»^2$ より $a = «a»$。", y=a * x * x, x=x, a=a))


def t_pythag_b():
    a, b, c = R.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (9, 12, 15), (7, 24, 25)]); k = R.randint(1, 3)
    return add(221, "junior", 1, "三平方の定理", fmt("たて $«a»$ cm、よこ $«b»$ cm の長方形の対角線の長さは何 cm か。", a=a * k, b=b * k), c * k,
               fmt("$«a»^2 + «b»^2 = «s»$ なので対角線は $\\sqrt{«s»} = «c»$ cm。", a=a * k, b=b * k, s=(a * k) ** 2 + (b * k) ** 2, c=c * k))


def t_pythag_c():
    x0, y0 = R.randint(-4, 3), R.randint(-4, 3)
    a, b, c = R.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13)])
    return add(222, "junior", 2, "三平方の定理", fmt("座標平面上の2点 $(«x0»,\\ «y0»)$、$(«x1»,\\ «y1»)$ の間の距離を答えよ。", x0=x0, y0=y0, x1=x0 + a, y1=y0 + b), c,
               fmt("$\\sqrt{«a»^2 + «b»^2} = «c»$。", a=a, b=b, c=c))


def t_angle_a():
    n = R.choice([5, 6, 8, 9, 10, 12])
    return add(223, "junior", 1, "多角形の角", fmt("正 $«n»$ 角形の1つの外角の大きさは何度か。", n=n), 360 // n,
               fmt("外角の和は $360^\\circ$ なので $360 \\div «n» = «a»$ 度。", n=n, a=360 // n)) if 360 % n == 0 else False


def t_angle_b():
    a, b = R.randint(30, 80), R.randint(30, 80)
    if a + b >= 170 or a == b: return False
    return add(224, "junior", 1, "多角形の角", fmt("三角形の2つの内角が $«a»^\\circ$、$«b»^\\circ$ のとき、残りの角の外角は何度か。", a=a, b=b), a + b,
               fmt("外角は、それととなり合わない2つの内角の和に等しいので $«a» + «b» = «s»$ 度。", a=a, b=b, s=a + b))


def t_angle_c():
    n = R.choice([5, 6, 7, 8, 9, 10])
    return add(225, "junior", 2, "多角形の角", fmt("$«n»$ 角形の内角の和は何度か。", n=n), 180 * (n - 2),
               fmt("$180 \\times («n» - 2) = «s»$ 度。", n=n, s=180 * (n - 2)))


def t_prob_cnt():
    n = R.randint(3, 5); k = R.randint(1, n - 1)
    ans = sum(1 for t in itertools.product([0, 1], repeat=n) if sum(t) == k)
    assert ans == comb(n, k)
    return add(226, "junior", 2, "確率", fmt("$«n»$ 枚の硬貨を同時に投げる。表がちょうど $«k»$ 枚出る場合は何通りか。", n=n, k=k), ans,
               fmt("$«n»$ 枚のうち表になる $«k»$ 枚の選び方なので $«a»$ 通り。", n=n, k=k, a=ans))


def c_prob_dice():
    kind = R.choice([("偶数", lambda v: v % 2 == 0), ("3の倍数", lambda v: v % 3 == 0), ("4以上", lambda v: v >= 4), ("素数", lambda v: v in (2, 3, 5)), ("2以下", lambda v: v <= 2)])
    name, f = kind
    n = sum(1 for v in range(1, 7) if f(v))
    good = frac_str(Fraction(n, 6))
    wr = [frac_str(Fraction(n + 1, 6)) if n < 6 else frac_str(Fraction(5, 6)), frac_str(Fraction(n, 5)) if n != 5 else frac_str(Fraction(1, 5)), frac_str(Fraction(max(n - 1, 0), 6))]
    cs = choice_set(good, wr + [frac_str(Fraction(1, 6)), frac_str(Fraction(1, 3)), frac_str(Fraction(2, 3))])
    if cs is None: return False
    return add(227, "junior", 1, "確率", fmt("さいころを1個投げるとき、«nm»の目が出る確率を選べ。", nm=name), cs[1],
               fmt("«nm»の目は $«n»$ 通り。全体は $6$ 通りなので、確率は $«p»$。", nm=name, n=n, p=good.strip("$")), cs[0])


def t_int_a():
    base = R.choice([2, 3, 5, 6, 7, 10, 12, 15, 18])
    # √(base * n) が整数となる最小の n は、base の平方因子を除いた部分
    n = 1
    for p in sp.factorint(base):
        if sp.factorint(base)[p] % 2: n *= p
    assert isqrt(base * n) ** 2 == base * n and all(isqrt(base * m) ** 2 != base * m for m in range(1, n))
    return add(228, "junior", 2, "整数の文章題", fmt("$\\sqrt{«b»n}$ が整数となる、最小の自然数 $n$ を答えよ。", b=base), n,
               fmt("$«b»n$ が平方数になる最小の $n$ は $«n»$（$«b»\\times«n» = «m»$）。", b=base, n=n, m=base * n))


def t_int_b():
    a, b = R.randint(2, 9), R.randint(2, 9)
    if a == b or gcd(a, b) != 1: return False
    N = R.randint(5, 20) * a * b
    ans = N // a + N // b - 2 * (N // (a * b))
    return add(229, "junior", 2, "倍数の個数", fmt("$1$ から $«N»$ までの整数のうち、$«a»$ の倍数または $«b»$ の倍数であるものは何個あるか。ただし両方の倍数は 1 回だけ数える。", N=N, a=a, b=b),
               N // a + N // b - N // (a * b),
               fmt("$«N»\\div«a» = «x»$、$«N»\\div«b» = «y»$、両方は $«N»\\div«ab» = «z»$。$«x» + «y» - «z» = «t»$。", N=N, a=a, b=b, ab=a * b, x=N // a, y=N // b, z=N // (a * b), t=N // a + N // b - N // (a * b)))


# ═════════ 高校：thin な単元 ═════════
def t_radian():
    n, d = R.choice([(1, 6), (1, 4), (1, 3), (1, 2), (2, 3), (3, 4), (5, 6), (3, 2), (5, 4)])
    deg = 180 * n // d
    if 180 * n % d: return False
    return add(230, "math2b", 1, "弧度法", fmt("$\\dfrac{«n»}{«d»}\\pi$ ラジアンは何度か。", n=n if n != 1 else "", d=d) if n != 1 else fmt("$\\dfrac{\\pi}{«d»}$ ラジアンは何度か。", d=d), deg,
               fmt("$\\pi$ ラジアン $= 180^\\circ$ なので $180 \\times \\dfrac{«n»}{«d»} = «deg»$ 度。", n=n, d=d, deg=deg))


_SINV = {0: "0", 30: "\\dfrac{1}{2}", 45: "\\dfrac{\\sqrt{2}}{2}", 60: "\\dfrac{\\sqrt{3}}{2}", 90: "1", 120: "\\dfrac{\\sqrt{3}}{2}", 135: "\\dfrac{\\sqrt{2}}{2}", 150: "\\dfrac{1}{2}", 180: "0",
         210: "-\\dfrac{1}{2}", 225: "-\\dfrac{\\sqrt{2}}{2}", 240: "-\\dfrac{\\sqrt{3}}{2}", 270: "-1", 300: "-\\dfrac{\\sqrt{3}}{2}", 315: "-\\dfrac{\\sqrt{2}}{2}", 330: "-\\dfrac{1}{2}"}


def c_sin_value():
    ang = R.choice([120, 135, 150, 210, 225, 240, 300, 315, 330])
    good = _SINV[ang]
    pool = ["\\dfrac{1}{2}", "-\\dfrac{1}{2}", "\\dfrac{\\sqrt{2}}{2}", "-\\dfrac{\\sqrt{2}}{2}", "\\dfrac{\\sqrt{3}}{2}", "-\\dfrac{\\sqrt{3}}{2}"]
    wrongs = [v for v in pool if v != good]; R.shuffle(wrongs)
    cs = choice_set("$%s$" % good, ["$%s$" % w for w in wrongs[:3]])
    return add(231, "math2b", 2, "三角関数の値", fmt("$\\sin «a»^\\circ$ の値を選べ。", a=ang), cs[1],
               fmt("単位円で考えると $\\sin «a»^\\circ = «v»$。", a=ang, v=good), cs[0])


def t_trig_count():
    eqs = [("\\sin \\theta = \\dfrac{1}{2}", 2), ("\\sin \\theta = -1", 1), ("\\cos \\theta = 1", 1), ("\\sin \\theta = 0", 2),
           ("\\cos \\theta = 0", 2), ("\\tan \\theta = 1", 2), ("\\tan \\theta = -1", 2), ("\\cos \\theta = -1", 1),
           ("\\sin \\theta = 1", 1), ("\\cos \\theta = \\dfrac{\\sqrt{3}}{2}", 2), ("\\sin \\theta = 2", 0), ("\\cos \\theta = -\\dfrac{1}{2}", 2)]
    eq, n = R.choice(eqs)
    if R.randint(0, 1):
        return add(232, "math2b", 2, "三角方程式の解の個数", fmt("$0^\\circ \\le \\theta < 360^\\circ$ のとき、方程式 $«eq»$ を満たす $\\theta$ は何個あるか。", eq=eq), n,
                   "単位円（または $y = \\tan\\theta$ のグラフ）で、条件に合う角を数える。")
    return add(232, "math2b", 3, "三角方程式の解の個数", fmt("$0^\\circ \\le \\theta < 720^\\circ$ のとき、方程式 $«eq»$ を満たす $\\theta$ は何個あるか。", eq=eq), 2 * n,
               "$0^\\circ \\le \\theta < 360^\\circ$ の個数を数え、2周ぶんなので2倍する。")


def t_box_diag():
    a, b, c, d = R.choice([(1, 2, 2, 3), (2, 3, 6, 7), (2, 6, 9, 11), (4, 4, 7, 9), (3, 4, 12, 13), (1, 4, 8, 9)]); k = R.randint(1, 3)
    assert a * a + b * b + c * c == d * d
    return add(233, "math2b", 2, "直方体の対角線", fmt("たて $«a»$、よこ $«b»$、高さ $«c»$ の直方体の対角線の長さを答えよ。", a=a * k, b=b * k, c=c * k), d * k,
               fmt("$\\sqrt{«a»^2 + «b»^2 + «c»^2} = \\sqrt{«s»} = «d»$。", a=a * k, b=b * k, c=c * k, s=(d * k) ** 2, d=d * k))


def t_pyramid():
    a, h = R.randint(2, 9), R.randint(2, 9)
    if (a * a * h) % 3: return False
    return add(234, "math2b", 2, "角錐の体積", fmt("底面が1辺 $«a»$ の正方形で、高さが $«h»$ の四角錐の体積を答えよ。", a=a, h=h), a * a * h // 3,
               fmt("体積 $= \\dfrac{1}{3} \\times «a»^2 \\times «h» = «v»$。", a=a, h=h, v=a * a * h // 3))


def t_sphere():
    r = R.choice([3, 6, 9, 12]); kind = R.choice(["体積", "表面積"])
    if kind == "体積":
        return add(235, "math2b", 2, "球の体積と表面積", fmt("半径 $«r»$ の球の体積は $k\\pi$ である。$k$ の値を答えよ。", r=r), 4 * r ** 3 // 3,
                   fmt("$\\dfrac{4}{3}\\pi r^3 = \\dfrac{4}{3}\\pi \\times «r»^3 = «k»\\pi$。", r=r, k=4 * r ** 3 // 3))
    return add(235, "math2b", 2, "球の体積と表面積", fmt("半径 $«r»$ の球の表面積は $k\\pi$ である。$k$ の値を答えよ。", r=r), 4 * r * r,
               fmt("$4\\pi r^2 = 4\\pi \\times «r»^2 = «k»\\pi$。", r=r, k=4 * r * r))


def t_set_count():
    a, b, both = R.randint(10, 30), R.randint(10, 30), R.randint(2, 9)
    return add(236, "math1a", 1, "集合の要素の個数", fmt("$n(A) = «a»$、$n(B) = «b»$、$n(A \\cap B) = «c»$ のとき、$n(A \\cup B)$ を答えよ。", a=a, b=b, c=both), a + b - both,
               fmt("$n(A \\cup B) = n(A) + n(B) - n(A \\cap B) = «a» + «b» - «c» = «s»$。", a=a, b=b, c=both, s=a + b - both))


def c_contrapositive():
    items = [("$x > 2$ ならば $x^2 > 4$", "$x^2 \\le 4$ ならば $x \\le 2$"), ("$x = 3$ ならば $x^2 = 9$", "$x^2 \\ne 9$ ならば $x \\ne 3$"),
             ("$a > 0$ かつ $b > 0$ ならば $ab > 0$", "$ab \\le 0$ ならば $a \\le 0$ または $b \\le 0$"), ("$n$ が $6$ の倍数ならば $n$ は偶数", "$n$ が奇数ならば $n$ は $6$ の倍数でない")]
    p, good = R.choice(items)
    wrongs = ["$%s$" % w for w in ["逆", "裏", "命題そのもの"]]
    # 対偶を問う（選択肢は、他の命題の形）
    others = [q for (_, q) in items if q != good] + ["（どれも対偶ではない）"]
    cs = choice_set(good, others[:3])
    if cs is None: return False
    return add(237, "math1a", 2, "命題の対偶", fmt("命題「«p»」の対偶を選べ。", p=p), cs[1],
               "対偶は、仮定と結論を入れかえて、両方を否定したもの。", cs[0])


def t_abs():
    a, b = R.randint(-6, 6), R.randint(2, 8)
    lo, hi = a - b + 1, a + b - 1
    cnt = hi - lo + 1
    return add(238, "math1a", 2, "絶対値と不等式", fmt("不等式 $|x - («a»)| < «b»$ を満たす整数 $x$ は何個あるか。", a=a, b=b), cnt,
               fmt("$«lo» \\le x \\le «hi»$ の整数なので $«c»$ 個。", lo=lo, hi=hi, c=cnt))


def t_binom_coef():
    n = R.randint(4, 7); k = R.randint(1, n - 1); a, b = R.randint(1, 3), R.randint(1, 3)
    x = sp.Symbol("x")
    coef = sp.Poly(sp.expand((a * x + b) ** n), x).coeff_monomial(x ** k)
    return add(239, "math2b", 2, "二項定理", fmt("$(«ax» + «b»)^{«n»}$ を展開したとき、$x^{«k»}$ の係数を答えよ。", ax=("x" if a == 1 else "%dx" % a), b=b, n=n, k=k), int(coef),
               fmt("${}_{«n»}\\mathrm{C}_{«k»} \\cdot «a»^{«k»} \\cdot «b»^{«nk»} = «c»$。", n=n, k=k, a=a, b=b, nk=n - k, c=int(coef)))


def t_circle_b():
    a, b, r = R.randint(-5, 5), R.randint(-5, 5), R.randint(2, 9)
    return add(240, "math2b", 1, "円の方程式", fmt("円 $(x «ax»)^2 + (y «by»)^2 = «r2»$ の半径を答えよ。", ax=("- %d" % a if a > 0 else "+ %d" % -a), by=("- %d" % b if b > 0 else "+ %d" % -b), r2=r * r), r,
               fmt("$r^2 = «r2»$ より半径は $«r»$。", r2=r * r, r=r))


def t_vec_dot():
    a1, a2, b1, b2 = [R.randint(-5, 6) for _ in range(4)]
    return add(241, "math3c", 1, "内積", fmt("$\\vec{a} = («a1»,\\ «a2»)$、$\\vec{b} = («b1»,\\ «b2»)$ のとき、内積 $\\vec{a} \\cdot \\vec{b}$ を答えよ。", a1=a1, a2=a2, b1=b1, b2=b2), a1 * b1 + a2 * b2,
               fmt("$«a1» \\times («b1») + («a2») \\times («b2») = «v»$。", a1=a1, a2=a2, b1=b1, b2=b2, v=a1 * b1 + a2 * b2))


def t_vec_len():
    a, b, c = R.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)]); sa, sb = R.choice([1, -1]), R.choice([1, -1])
    return add(242, "math2b", 1, "ベクトルの大きさ", fmt("$\\vec{a} = («x»,\\ «y»)$ の大きさ $|\\vec{a}|$ を答えよ。", x=sa * a, y=sb * b), c,
               fmt("$\\sqrt{(«x»)^2 + («y»)^2} = «c»$。", x=sa * a, y=sb * b, c=c))


def t_ellipse_b():
    a, b = R.choice([(5, 4), (5, 3), (13, 12), (10, 8), (10, 6), (17, 15), (25, 24)])
    # x^2/a^2 + y^2/b^2 = 1 の焦点（±c, 0）の c
    c = isqrt(a * a - b * b)
    return add(243, "math3c", 2, "楕円の焦点", fmt("楕円 $\\dfrac{x^2}{«a2»} + \\dfrac{y^2}{«b2»} = 1$ の焦点の1つのx座標（正のほう）を答えよ。", a2=a * a, b2=b * b), c,
               fmt("$c = \\sqrt{«a2» - «b2»} = «c»$。", a2=a * a, b2=b * b, c=c))


INTEGER_TEMPLATES = [t_signed_a, t_signed_b, t_signed_c, t_value_a, t_value_b, t_linear_b, t_linear_c, t_linear_d, t_simul_b, t_simul_word,
                     t_ineq_b, t_ineq_c, t_expand, t_square_diff, t_quad_b, t_quad_c, t_quad_d, t_func2_a, t_func2_b, t_func2_c,
                     t_pythag_b, t_pythag_c, t_angle_a, t_angle_b, t_angle_c, t_prob_cnt, t_int_a, t_int_b,
                     t_radian, t_trig_count, t_box_diag, t_pyramid, t_sphere, t_set_count, t_abs, t_binom_coef, t_circle_b,
                     t_vec_dot, t_vec_len, t_ellipse_b]
CHOICE_TEMPLATES = [c_prob_dice, c_sin_value, c_contrapositive]


def generate(per_template=8):
    G.OUT.clear(); G._seen.clear()
    for fn in INTEGER_TEMPLATES + CHOICE_TEMPLATES: make(0, per_template, fn)
    return list(G.OUT)


if __name__ == "__main__":
    ps = generate()
    print(len(ps), "問")
    for p in ps[::12]: print(p["id"], p["title"], "|", p["plain"][:70], "->", p["answer"])
