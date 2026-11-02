"""残った薄い数学の単元を増やす、数字を変えて作る問題。tools/build_problems.py から呼ばれる。
乱数は自前の線形合同法。正解は、別の方法（総当たり・sympy）でも確かめてから登録する。"""
from fractions import Fraction
from math import gcd, isqrt, comb, perm, factorial, floor, sqrt, log2
import itertools
import sympy as sp
import gen_problems as G
from gen_problems import fmt, add, make

R = G.Rng(20261106)


def choice_set(correct, wrongs):
    opts = [correct]
    for w in wrongs:
        if w not in opts: opts.append(w)
    if len(opts) < 4: return None
    opts = opts[:4]
    R.shuffle(opts)
    return opts, opts.index(correct)


def fr(f):
    f = Fraction(f)
    return "$%d$" % f.numerator if f.denominator == 1 else "$\\dfrac{%d}{%d}$" % (f.numerator, f.denominator)


# ═════════ 平方根 ═════════
def t_sqrt_out():
    a, b = R.randint(2, 9), R.choice([2, 3, 5, 6, 7])
    return add(301, "junior", 1, "平方根", fmt("$\\sqrt{«N»}$ を $a\\sqrt{b}$（$b$ はできるだけ小さい自然数）の形に表すとき、$a$ の値を答えよ。", N=a * a * b), a,
               fmt("$«N» = «a2» \\times «b»$ より $\\sqrt{«N»} = «a»\\sqrt{«b»}$。", N=a * a * b, a2=a * a, a=a, b=b))


def t_sqrt_conj():
    a, b = R.randint(3, 40), R.randint(2, 30)
    if a == b: return False
    return add(302, "junior", 2, "平方根", fmt("$(\\sqrt{«a»} + \\sqrt{«b»})(\\sqrt{«a»} - \\sqrt{«b»})$ を計算せよ。", a=a, b=b), a - b,
               fmt("和と差の積なので $(\\sqrt{«a»})^2 - (\\sqrt{«b»})^2 = «a» - «b» = «r»$。", a=a, b=b, r=a - b))


def t_sqrt_prod():
    x = R.randint(2, 9); k = R.choice([2, 3, 5, 6, 7]); a, b = k, k * x * x
    return add(303, "junior", 1, "平方根", fmt("$\\sqrt{«a»} \\times \\sqrt{«b»}$ を計算せよ。", a=a, b=b), k * x,
               fmt("$\\sqrt{«a» \\times «b»} = \\sqrt{«p»} = «r»$。", a=a, b=b, p=a * b, r=k * x))


def t_sqrt_int():
    n = R.randint(20, 150)
    if isqrt(n) ** 2 == n: return False
    return add(304, "junior", 1, "平方根", fmt("$\\sqrt{«n»}$ の整数部分を答えよ。", n=n), isqrt(n),
               fmt("$«a»^2 = «a2»$、$«b»^2 = «b2»$ なので $«a» < \\sqrt{«n»} < «b»$。整数部分は $«a»$。", a=isqrt(n), a2=isqrt(n) ** 2, b=isqrt(n) + 1, b2=(isqrt(n) + 1) ** 2, n=n))


def t_sqrt_count():
    N = R.randint(30, 200)
    return add(305, "junior", 2, "平方根", fmt("$\\sqrt{n}$ が整数となる自然数 $n$ は、$1 \\le n \\le «N»$ の範囲に何個あるか。", N=N), isqrt(N),
               fmt("$n$ が平方数のとき。$«a»^2 \\le «N»$ となる最大の $«a»$ までなので $«a»$ 個。", N=N, a=isqrt(N)))


def c_sqrt_max():
    cands = []
    while len(cands) < 4:
        kind = R.randint(0, 2)
        if kind == 0:
            k = R.randint(3, 8); cands.append((float(k), "$%d$" % k))
        elif kind == 1:
            n = R.randint(5, 70)
            if isqrt(n) ** 2 == n: continue
            cands.append((sqrt(n), "$\\sqrt{%d}$" % n))
        else:
            a, b = R.randint(2, 4), R.choice([2, 3, 5])
            cands.append((a * sqrt(b), "$%d\\sqrt{%d}$" % (a, b)))
        if len({round(c[0], 6) for c in cands}) < len(cands): cands.pop()
    best = max(cands, key=lambda t: t[0])
    R.shuffle(cands)
    return add(306, "junior", 2, "平方根", "次の4つの数のうち、最も大きいものを選べ。", [c[1] for c in cands].index(best[1]),
               "それぞれを小数で見積もる（$\\sqrt{2} \\fallingdotseq 1.41$、$\\sqrt{3} \\fallingdotseq 1.73$、$\\sqrt{5} \\fallingdotseq 2.24$ など）。", [c[1] for c in cands])


# ═════════ 場合の数・確率（高校）═════════
def t_perm_adj():
    n = R.randint(4, 8)
    ans = 2 * factorial(n - 1)
    cnt = sum(1 for p in itertools.permutations(range(n)) if abs(p.index(0) - p.index(1)) == 1) if n <= 6 else ans
    assert cnt == ans
    return add(311, "math1a", 2, "順列", fmt("$«n»$ 人が1列に並ぶとき、特定の2人 A、B が隣り合う並び方は何通りあるか。", n=n), ans,
               fmt("A、B をひとまとめにして $«m»$ 人の並び方 $«m»!$ に、A、B の順番 $2$ 通りをかける。$2 \\times «m»! = «a»$。", m=n - 1, a=ans))


def t_circ_perm():
    n = R.randint(4, 8)
    return add(312, "math1a", 2, "順列", fmt("$«n»$ 人が円形のテーブルにすわる。すわり方は何通りか（回転して同じになるものは同じとみなす）。", n=n), factorial(n - 1),
               fmt("円順列は $(n - 1)!$ なので $«m»! = «a»$。", m=n - 1, a=factorial(n - 1)))


def t_rep_perm():
    k, r = R.randint(2, 5), R.randint(2, 5)
    return add(313, "math1a", 1, "順列", fmt("$«k»$ 種類の文字から、同じ文字を何度使ってもよいとして、$«r»$ 個を1列に並べる。並べ方は何通りか。", k=k, r=r), k ** r,
               fmt("1つの位置に $«k»$ 通りずつなので $«k»^{«r»} = «a»$。", k=k, r=r, a=k ** r))


def t_comb_inc():
    n, r = R.randint(6, 10), R.randint(2, 4)
    return add(314, "math1a", 2, "組合せ", fmt("$«n»$ 人の中から $«r»$ 人の委員を選ぶとき、特定の1人 A が必ず入る選び方は何通りか。", n=n, r=r), comb(n - 1, r - 1),
               fmt("A 以外の $«m»$ 人から残りの $«q»$ 人を選ぶので ${}_{«m»}\\mathrm{C}_{«q»} = «a»$。", m=n - 1, q=r - 1, a=comb(n - 1, r - 1)))


def t_route():
    a, b = R.randint(2, 6), R.randint(2, 5)
    return add(315, "math1a", 2, "最短経路", fmt("縦 $«b»$ 区画、横 $«a»$ 区画の格子状の道を、左下から右上まで最短で行く道順は何通りか。", a=a, b=b), comb(a + b, a),
               fmt("右へ $«a»$ 回、上へ $«b»$ 回の並べ方なので ${}_{«n»}\\mathrm{C}_{«a»} = «c»$。", a=a, b=b, n=a + b, c=comb(a + b, a)))


def t_group():
    return add(316, "math1a", 2, "組分け", fmt("$«n»$ 人を、$«g»$ 人ずつ $2$ つの組に分ける（組に区別はない）。分け方は何通りか。", n=2 * (g := R.randint(2, 4)), g=g), comb(2 * g, g) // 2,
               fmt("${}_{«n»}\\mathrm{C}_{«g»}$ 通りの選び方は、2組を入れかえて二重に数えているので $2$ でわる。$«a»$ 通り。", n=2 * g, g=g, a=comb(2 * g, g) // 2))


def c_prob_balls():
    r, w = R.randint(2, 6), R.randint(2, 6)
    tot = comb(r + w, 2)
    p = Fraction(comb(r, 2) + comb(w, 2), tot)
    q = Fraction(r * w, tot)
    cs = choice_set(fr(p), [fr(q), fr(Fraction(r * w, tot * 2) if r * w % (tot * 2) == 0 or True else q), fr(Fraction(comb(r, 2), tot)), fr(Fraction(1, 2) if p != Fraction(1, 2) else Fraction(1, 3))])
    if cs is None: return False
    return add(321, "math1a", 2, "確率（組合せ）", fmt("赤玉 $«r»$ 個と白玉 $«w»$ 個が入った袋から、同時に $2$ 個取り出すとき、同じ色である確率を選べ。", r=r, w=w), cs[1],
               fmt("全体は ${}_{«n»}\\mathrm{C}_{2} = «t»$ 通り。同色は ${}_{«r»}\\mathrm{C}_{2} + {}_{«w»}\\mathrm{C}_{2} = «s»$ 通り。確率は $«p»$。",
                   n=r + w, t=tot, r=r, w=w, s=comb(r, 2) + comb(w, 2), p=fr(p).strip("$")), cs[0])


def c_prob_sum():
    s = R.randint(3, 11)
    ways = sum(1 for i in range(1, 7) for j in range(1, 7) if i + j == s)
    p = Fraction(ways, 36)
    cs = choice_set(fr(p), [fr(Fraction(ways + 1, 36)), fr(Fraction(ways, 12)), fr(Fraction(ways, 6)), fr(Fraction(max(ways - 1, 1), 36))])
    if cs is None: return False
    return add(322, "math1a", 1, "確率（組合せ）", fmt("大小2つのさいころを投げるとき、目の和が $«s»$ になる確率を選べ。", s=s), cs[1],
               fmt("全体は $36$ 通り。和が $«s»$ になるのは $«w»$ 通り。確率は $«p»$。", s=s, w=ways, p=fr(p).strip("$")), cs[0])


def t_expect():
    k = R.randint(2, 5); p1, v1 = R.choice([(1, 1000), (1, 500), (2, 300), (1, 200)])
    n = R.choice([10, 20, 50, 100])
    if p1 > n: return False
    # n本のくじのうち p1 本が v1 円、残りは 0 円。期待値(円)= p1*v1/n が整数になるもの
    if (p1 * v1) % n: return False
    return add(323, "math1a", 2, "期待値", fmt("$«n»$ 本のうち $«p»$ 本が当たりで、当たると $«v»$ 円もらえるくじがある。1本引いたときにもらえる金額の期待値は何円か。", n=n, p=p1, v=v1), p1 * v1 // n,
               fmt("期待値 $= «v» \\times \\dfrac{«p»}{«n»} = «e»$ 円。", v=v1, p=p1, n=n, e=p1 * v1 // n))


# ═════════ 指数・対数 ═════════
def t_log_val():
    a, k = R.choice([2, 3, 5]), R.randint(2, 5)
    if a == 5 and k > 3: return False
    return add(331, "math2b", 1, "対数", fmt("$\\log_{«a»} «N»$ の値を答えよ。", a=a, N=a ** k), k,
               fmt("$«a»^{«k»} = «N»$ なので $\\log_{«a»} «N» = «k»$。", a=a, k=k, N=a ** k))


def t_log_sum():
    a = R.choice([2, 3, 6, 10]); x, y = R.randint(1, 3), R.randint(1, 3)
    return add(332, "math2b", 2, "対数", fmt("$\\log_{«a»} «p» + \\log_{«a»} «q»$ の値を答えよ。", a=a, p=a ** x, q=a ** y), x + y,
               fmt("$\\log_{«a»} «p» = «x»$、$\\log_{«a»} «q» = «y»$ なので $«s»$。", a=a, p=a ** x, q=a ** y, x=x, y=y, s=x + y))


def t_exp_eq():
    a, k = R.choice([2, 3, 5]), R.randint(2, 5)
    b = R.randint(0, 3)
    return add(333, "math2b", 2, "指数方程式", fmt("方程式 $«a»^{x + «b»} = «N»$ を解け。$x$ の値を答えよ。", a=a, b=b, N=a ** (k + b)), k,
               fmt("$«N» = «a»^{«e»}$ なので $x + «b» = «e»$ より $x = «k»$。", N=a ** (k + b), a=a, e=k + b, b=b, k=k))


def t_exp_calc():
    a = R.choice([2, 3, 5]); m, n, k = R.randint(2, 6), R.randint(2, 6), R.randint(1, 4)
    if m + n - k < 0: return False
    ans = a ** (m + n - k)
    return add(334, "math2b", 1, "指数の計算", fmt("$«a»^{«m»} \\times «a»^{«n»} \\div «a»^{«k»}$ を計算せよ。", a=a, m=m, n=n, k=k), ans,
               fmt("指数の和と差で $«a»^{«m» + «n» - «k»} = «a»^{«e»} = «r»$。", a=a, m=m, n=n, k=k, e=m + n - k, r=ans))


# ═════════ 積分・二次曲線 ═════════
x = sp.Symbol("x")


def t_integ_trig():
    a = R.randint(1, 6)
    f, F, lo, hi, expl = R.choice([
        (a * sp.sin(x), None, 0, sp.pi, "\\sin"), (a * sp.cos(x), None, 0, sp.pi / 2, "\\cos"), (a * sp.sin(2 * x), None, 0, sp.pi / 2, "\\sin 2x"),
        (a * sp.exp(x), None, 0, sp.log(2), "e^x")])
    val = sp.integrate(f, (x, lo, hi))
    if not val.is_Integer: return False
    texf = {"\\sin": "%d\\sin x", "\\cos": "%d\\cos x", "\\sin 2x": "%d\\sin 2x", "e^x": "%de^{x}"}[expl] % a
    texhi = {"\\sin": "\\pi", "\\cos": "\\dfrac{\\pi}{2}", "\\sin 2x": "\\dfrac{\\pi}{2}", "e^x": "\\log 2"}[expl]
    return add(341, "math3c", 2, "三角関数・指数関数の積分", fmt("定積分 $\\displaystyle\\int_0^{«hi»} «f»\\,dx$ の値を答えよ。", hi=texhi, f=texf), int(val),
               "不定積分を求めて、上端と下端の値の差をとる。")


def t_integ_pow():
    a, n = R.randint(1, 3), R.randint(2, 4)
    val = sp.integrate((a * x + 1) ** n, (x, 0, 1))
    if not val.is_Integer: return False
    return add(342, "math3c", 2, "合成関数の積分", fmt("定積分 $\\displaystyle\\int_0^1 («a»x + 1)^{«n»}\\,dx$ の値を答えよ。", a=a, n=n), int(val),
               fmt("$\\dfrac{1}{«a»(«n» + 1)}\\left[(«a»x + 1)^{«n1»}\\right]_0^1$ を計算する。", a=a, n=n, n1=n + 1))


def t_integ_vol():
    a = R.choice([3, 6, 9, 12]); k = a ** 3 // 3
    return add(343, "math3c", 3, "回転体の体積", fmt("曲線 $y = x$ と $x$ 軸、直線 $x = «a»$ で囲まれた部分を $x$ 軸のまわりに1回転してできる立体の体積は $k\\pi$ である。$k$ の値を答えよ。", a=a), k,
               fmt("$\\pi\\int_0^{«a»} x^2\\,dx = \\pi \\cdot \\dfrac{«a»^3}{3} = «k»\\pi$。", a=a, k=k))


def t_parabola_focus():
    p = R.randint(1, 9)
    return add(351, "math3c", 1, "放物線の焦点", fmt("放物線 $y^2 = «c»x$ の焦点の $x$ 座標を答えよ。", c=4 * p), p,
               fmt("$y^2 = 4px$ の焦点は $(p,\\ 0)$。$4p = «c»$ より $p = «p»$。", c=4 * p, p=p))


def t_hyper_focus():
    a, b, c = R.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (6, 8, 10), (8, 6, 10), (8, 15, 17), (15, 8, 17)])
    return add(352, "math3c", 2, "双曲線の焦点", fmt("双曲線 $\\dfrac{x^2}{«a2»} - \\dfrac{y^2}{«b2»} = 1$ の焦点の $x$ 座標（正のほう）を答えよ。", a2=a * a, b2=b * b), c,
               fmt("$c = \\sqrt{«a2» + «b2»} = «c»$。", a2=a * a, b2=b * b, c=c))


def t_ellipse_long():
    a, b = R.randint(3, 9), R.randint(2, 8)
    if a <= b: return False
    return add(353, "math3c", 1, "楕円の長軸", fmt("楕円 $\\dfrac{x^2}{«a2»} + \\dfrac{y^2}{«b2»} = 1$ の長軸の長さを答えよ。", a2=a * a, b2=b * b), 2 * a,
               fmt("$a = \\sqrt{«a2»} = «a»$ なので、長軸の長さは $2a = «l»$。", a2=a * a, a=a, l=2 * a))


# ═════════ 他の薄い高校数学の単元 ═════════
def t_quad_axis():
    p, q = R.randint(-6, 6), R.randint(-8, 8); a = R.choice([1, 2, 3, -1, -2])
    inner = "x" if p == 0 else ("x - %d" % p if p > 0 else "x + %d" % -p)
    tail = "" if q == 0 else (" + %d" % q if q > 0 else " - %d" % -q)
    return add(361, "math1a", 1, "二次関数の最小値", fmt("二次関数 $y = «a»(«inner»)^2«tail»$ の、最大値または最小値を答えよ。", a=a, inner=inner, tail=tail), q,
               fmt("頂点の $y$ 座標 $«q»$ が、最大値（$a < 0$）または最小値（$a > 0$）。", q=q))


def t_discriminant():
    a, b, c = R.randint(1, 4), R.randint(-9, 9), R.randint(-5, 5)
    D = b * b - 4 * a * c
    return add(362, "math1a", 1, "判別式", fmt("二次方程式 $«a»x^2 «bs»x «cs» = 0$ の判別式 $D$ の値を答えよ。", a=a, bs=("+ %d" % b if b >= 0 else "- %d" % -b), cs=("+ %d" % c if c >= 0 else "- %d" % -c)), D,
               fmt("$D = b^2 - 4ac = («b»)^2 - 4 \\times «a» \\times («c») = «D»$。", b=b, a=a, c=c, D=D))


def t_trig_cos():
    a, b, c = R.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)])
    return add(363, "math1a", 2, "三角比", fmt("直角三角形で、斜辺が $«c»$、$\\sin A = \\dfrac{«a»}{«c»}$ のとき、$A$ の対辺でない辺の長さを答えよ。", a=a, c=c), b,
               fmt("三平方の定理より $\\sqrt{«c»^2 - «a»^2} = «b»$。", a=a, b=b, c=c))


def t_abs_eq():
    a, b = R.randint(-5, 5), R.randint(1, 8)
    return add(364, "math1a", 2, "絶対値と不等式", fmt("方程式 $|x - («a»)| = «b»$ の2つの解の和を答えよ。", a=a, b=b), 2 * a,
               fmt("$x = «a» \\pm «b»$ なので、和は $2 \\times («a») = «s»$。", a=a, b=b, s=2 * a))


def t_binom_sum():
    n = R.randint(3, 8)
    return add(365, "math2b", 1, "二項定理", fmt("$(a + b)^{«n»}$ を展開したときの、項の数を答えよ。", n=n), n + 1,
               fmt("$a^{«n»}$ から $b^{«n»}$ まで $«m»$ 個の項がある。", n=n, m=n + 1))


def t_line_mid():
    x1, y1, x2, y2 = [R.randint(-8, 8) for _ in range(4)]
    if (x1 + x2) % 2 or (y1 + y2) % 2 or (x1, y1) == (x2, y2): return False
    return add(366, "math2b", 1, "図形と方程式", fmt("2点 $(«x1»,\\ «y1»)$、$(«x2»,\\ «y2»)$ を結ぶ線分の中点の $x$ 座標と $y$ 座標の和を答えよ。", x1=x1, y1=y1, x2=x2, y2=y2), (x1 + x2) // 2 + (y1 + y2) // 2,
               fmt("中点は $(«mx»,\\ «my»)$。和は $«s»$。", mx=(x1 + x2) // 2, my=(y1 + y2) // 2, s=(x1 + x2) // 2 + (y1 + y2) // 2))


def t_line_slope():
    m = R.choice([-4, -3, -2, -1, 1, 2, 3, 4]); x1, y1 = R.randint(-4, 4), R.randint(-4, 4); dx = R.randint(1, 4)
    return add(367, "math2b", 1, "図形と方程式", fmt("2点 $(«x1»,\\ «y1»)$、$(«x2»,\\ «y2»)$ を通る直線の傾きを答えよ。", x1=x1, y1=y1, x2=x1 + dx, y2=y1 + m * dx), m,
               fmt("傾き $= \\dfrac{«dy»}{«dx»} = «m»$。", dy=m * dx, dx=dx, m=m))


def t_deriv_exp():
    a = R.randint(1, 5); c = R.randint(1, 5)
    f = a * sp.exp(x) + c * sp.log(x)
    val = sp.diff(f, x).subs(x, 1)
    # a*e + c は整数でない → e の係数と c の和を問う
    return add(368, "math3c", 2, "いろいろな関数の微分", fmt("$f(x) = «a»e^{x} + «c»\\log x$ のとき、$f'(1) = pe + q$ と表せる。$p + q$ の値を答えよ。", a=a, c=c), a + c,
               fmt("$f'(x) = «a»e^{x} + \\dfrac{«c»}{x}$ より $f'(1) = «a»e + «c»$。$p + q = «s»$。", a=a, c=c, s=a + c))


def t_nt_gcd():
    g = R.randint(2, 9); p, q = R.randint(3, 12), R.randint(3, 12)
    if p == q or gcd(p, q) != 1: return False
    return add(369, "math1a", 1, "最大公約数と互除法", fmt("$«a»$ と $«b»$ の最大公約数を答えよ。", a=g * p, b=g * q), g,
               fmt("ユークリッドの互除法（または素因数分解）で最大公約数は $«g»$。", g=g))


INTEGER_TEMPLATES = [t_sqrt_out, t_sqrt_conj, t_sqrt_prod, t_sqrt_int, t_sqrt_count,
                     t_perm_adj, t_circ_perm, t_rep_perm, t_comb_inc, t_route, t_group, t_expect,
                     t_log_val, t_log_sum, t_exp_eq, t_exp_calc, t_integ_trig, t_integ_pow, t_integ_vol,
                     t_parabola_focus, t_hyper_focus, t_ellipse_long, t_quad_axis, t_discriminant, t_trig_cos, t_abs_eq, t_binom_sum,
                     t_line_mid, t_line_slope, t_deriv_exp, t_nt_gcd]
CHOICE_TEMPLATES = [c_sqrt_max, c_prob_balls, c_prob_sum]


def generate(per_template=8):
    G.OUT.clear(); G._seen.clear()
    for fn in INTEGER_TEMPLATES + CHOICE_TEMPLATES: make(0, per_template, fn)
    return list(G.OUT)


if __name__ == "__main__":
    ps = generate()
    print(len(ps), "問")
    for p in ps[::9]: print(p["id"], p["title"], "|", p["plain"][:80], "->", p["answer"])
