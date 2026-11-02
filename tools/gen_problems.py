"""数字を変えて作る問題（整数で答える問題と、4択問題）。tools/build_problems.py から呼ばれる。

- 乱数は自前の線形合同法。Python のバージョンが変わっても、同じ問題が同じ順で出る（CI で差分を調べるため）。
- 正解は、公式とは別の方法（総当たり・sympy）でも確かめてから登録する。
- 本文・解説は LaTeX（$...$ が数式）。plain は、ブロック画面用の文字だけの問題文。
"""
import re
from fractions import Fraction
from math import comb, gcd, isqrt
import sympy as sp

LABELS = "①②③④"


class Rng:
    def __init__(self, seed): self.s = seed & 0xFFFFFFFF
    def next(self):
        self.s = (1664525 * self.s + 1013904223) & 0xFFFFFFFF
        return self.s >> 8
    def randint(self, a, b): return a + self.next() % (b - a + 1)
    def choice(self, seq): return seq[self.next() % len(seq)]
    def shuffle(self, lst):
        for i in range(len(lst) - 1, 0, -1):
            j = self.next() % (i + 1)
            lst[i], lst[j] = lst[j], lst[i]
        return lst


R = Rng(20261102)
OUT = []
_seen = set()


# ───────── LaTeX の書き方の道具 ─────────
def fmt(template, **v):
    """«name» を値に置き換える（LaTeX の { } をそのまま書けるように）。"""
    return re.sub(r"«(\w+)»", lambda m: str(v[m.group(1)]), template)


def term(c, v):
    if v == "": return str(abs(c))
    return v if abs(c) == 1 else f"{abs(c)}{v}"


def poly(terms):
    s = ""
    for c, v in terms:
        if c == 0: continue
        t = term(c, v)
        s += (("-" if c < 0 else "") + t) if s == "" else f" {'-' if c < 0 else '+'} {t}"
    return s or "0"


def lin(var, c):          # (var + c)
    return poly([(1, var), (c, "")])


def mono(c, e):
    if e == 0: return str(c)
    return term(c, "x" if e == 1 else f"x^{e}")


def fr(f):
    f = Fraction(f)
    return str(f.numerator) if f.denominator == 1 else fr_tex(f)


def fr_tex(f): return "\\dfrac{%d}{%d}" % (f.numerator, f.denominator)


def prod_str(nums): return " \\times ".join(str(n) for n in nums)


# ───────── LaTeX → 文字だけ ─────────
_SUP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
_SUB = {"0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉"}


def _wrap(x): return x if re.fullmatch(r"[\w√π.]+", x) else f"({x})"


def _math_plain(s):
    s = s.replace("^\\circ", "°")
    s = s.replace("\\displaystyle", "").replace("\\left", "").replace("\\right", "")
    s = s.replace("\\,", " ").replace("\\ ", " ").replace("\\;", " ")
    s = re.sub(r"\{\}_\{?(\d+)\}?\\mathrm\{C\}_\{?(\d+)\}?", r"\1C\2", s)
    s = re.sub(r"\\mathrm\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\(?:vec|overrightarrow)\{([^{}]*)\}", r"ベクトル\1", s)
    for _ in range(4):
        s = re.sub(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}", lambda m: f"{_wrap(m.group(1))}/{_wrap(m.group(2))}", s)
        s = re.sub(r"\\sqrt\{([^{}]*)\}", lambda m: "√" + _wrap(m.group(1)), s)
    s = re.sub(r"\\log_\{?(\d+)\}?", lambda m: "log" + "".join(_SUB[c] for c in m.group(1)), s)
    s = re.sub(r"\^\{?(\d+)\}?", lambda m: "".join(_SUP[c] for c in m.group(1)), s)
    s = re.sub(r"\^\{([^{}]*)\}", r"^\1", s)
    s = re.sub(r"_\{(\d+)\}", lambda m: "".join(_SUB[c] for c in m.group(1)), s)
    s = re.sub(r"_\{([^{}]*)\}", r"_(\1)", s)
    s = re.sub(r"_(\d)", lambda m: _SUB[m.group(1)], s)
    for a, b in [("\\cdots", "…"), ("\\cdot", "·"), ("\\times", "×"), ("\\div", "÷"), ("\\leqq", "≦"), ("\\geqq", "≧"),
                 ("\\pm", "±"), ("\\pi", "π"), ("\\theta", "θ"), ("\\omega", "ω"), ("\\Omega", "Ω"), ("\\angle", "∠"), ("\\circ", "°"),
                 ("\\infty", "∞"), ("\\to", "→"), ("\\sin", "sin"), ("\\cos", "cos"), ("\\tan", "tan"),
                 ("\\log", "log"), ("\\int", "∫"), ("\\sum", "Σ"), ("\\equiv", "≡"), ("\\pmod", "mod "),
                 ("\\dots", "…"), ("\\mathrm", "")]:
        s = s.replace(a, b)
    s = s.replace("{", "").replace("}", "").replace("\\", "")
    return re.sub(r" +", " ", s).strip()


def tex2plain(t):
    return re.sub(r"\$([^$]*)\$", lambda m: _math_plain(m.group(1)), t)


# ───────── 登録 ─────────
def add(tpl, cat, diff, title, body, answer, expl, choices=None):
    key = (tpl, body, tuple(choices or []))
    if key in _seen: return False
    _seen.add(key)
    n = sum(1 for p in OUT if p["id"].startswith(f"g{tpl:02d}-")) + 1
    plain = tex2plain(body)
    if choices is not None:
        plain += "　" + "　".join(f"{LABELS[i]} {tex2plain(c)}" for i, c in enumerate(choices))
    p = dict(id=f"g{tpl:02d}-{n}", category=cat, difficulty=diff, title=title, body=body,
             answer=answer, explanation=expl, plain=plain)
    if choices is not None: p["choices"] = choices
    OUT.append(p)
    return True


def make(tpl, n, fn, tries=400):
    """fn() が add(...) を呼ぶ。n 個作れるか、tries 回で打ち切る。"""
    made = 0
    for _ in range(tries):
        if made >= n: break
        if fn(): made += 1


def choice_set(correct, wrongs):
    """正解と間違いの選択肢を、重複なく並べ替えて (選択肢, 正解の番号) を返す。"""
    opts = [correct]
    for w in wrongs:
        if w not in opts: opts.append(w)
    if len(opts) < 4: return None
    opts = opts[:4]
    R.shuffle(opts)
    return opts, opts.index(correct)


# ═════════ 整数で答える問題 ═════════
def t_linear():
    a, c = R.randint(2, 9), None
    c = R.randint(1, a - 1); x = R.choice([v for v in range(-9, 13) if v]); b = R.randint(-9, 9)
    d = b + (a - c) * x
    if abs(d) > 30: return False
    assert a * x + b == c * x + d
    return add(1, "junior", 1, "一次方程式",
               fmt("方程式 $«l» = «r»$ を解け。$x$ の値を答えよ。", l=poly([(a, "x"), (b, "")]), r=poly([(c, "x"), (d, "")])),
               x, fmt("$x$ の項を左辺、数を右辺に集めると $«l» = «r»$ より $x = «x»$。", l=poly([(a - c, "x")]), r=d - b, x=x))


def t_simul():
    x, y = R.randint(-6, 9), R.randint(-6, 9)
    if x == 0 or y == 0 or x == y: return False
    s, d = x + y, x - y
    return add(2, "junior", 1, "連立方程式",
               fmt("$x + y = «s»$、$x - y = «d»$ のとき、$xy$ の値を答えよ。", s=s, d=d), x * y,
               fmt("2式を足して $2x = «a»$ より $x = «x»$、$y = «y»$。よって $xy = «p»$。", a=s + d, x=x, y=y, p=x * y))


def t_signs():
    a, b, c = R.randint(2, 9), R.randint(2, 9), R.randint(2, 9)
    return add(3, "junior", 1, "正負の数", fmt("$(-«a»)^2 - «b» \\times (-«c»)$ を計算せよ。", a=a, b=b, c=c), a * a + b * c,
               fmt("$(-«a»)^2 = «aa»$、$-«b» \\times (-«c») = +«bc»$ なので $«aa» + «bc» = «t»$。", a=a, b=b, c=c, aa=a * a, bc=b * c, t=a * a + b * c))


def t_sqrt():
    b, a = R.choice([2, 3, 5, 6, 7]), R.randint(2, 9); N = a * a * b
    assert isqrt(N // b) ** 2 == N // b
    return add(4, "junior", 1, "平方根", fmt("$\\sqrt{«N»} \\div \\sqrt{«b»}$ を計算せよ。", N=N, b=b), a,
               fmt("$\\sqrt{«N»} \\div \\sqrt{«b»} = \\sqrt{«N» \\div «b»} = \\sqrt{«q»} = «a»$。", N=N, b=b, q=a * a, a=a))


def t_quad_roots():
    p, q = R.randint(-8, 9), R.randint(-8, 9)
    if p == 0 or q == 0 or p == q: return False
    eq = poly([(1, "x^2"), (-(p + q), "x"), (p * q, "")])
    assert sorted(sp.solve(sp.Symbol("x") ** 2 - (p + q) * sp.Symbol("x") + p * q, sp.Symbol("x"))) == sorted([p, q])
    return add(5, "junior", 2, "二次方程式", fmt("二次方程式 $«eq» = 0$ の、大きいほうの解を答えよ。", eq=eq), max(p, q),
               fmt("$(«a»)(«b») = 0$ より $x = «p»,\\ «q»$。大きいほうは $«m»$。", a=lin("x", -p), b=lin("x", -q), p=p, q=q, m=max(p, q)))


def t_pythag():
    a, b, c = R.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29)]); k = R.randint(1, 4)
    a, b, c = a * k, b * k, c * k
    if R.randint(0, 1): a, b = b, a
    assert a * a + b * b == c * c
    return add(6, "junior", 2, "三平方の定理", fmt("直角三角形の斜辺が $«c»$、他の1辺が $«a»$ のとき、残りの辺の長さを答えよ。", c=c, a=a), b,
               fmt("$«c»^2 - «a»^2 = «cc» - «aa» = «bb» = «b»^2$。", c=c, a=a, cc=c * c, aa=a * a, bb=b * b, b=b))


def t_parabola():
    a = R.choice([1, 2, 3, 4, -1, -2, -3]); x0 = R.choice([1, 2, 3, 4, -1, -2, -3]); x1 = R.choice([v for v in range(-4, 6) if v not in (0, x0)])
    y0 = a * x0 * x0
    return add(7, "junior", 2, "関数 y = ax²",
               fmt("関数 $y = ax^2$ のグラフが点 $(«x0»,\\ «y0»)$ を通る。$x = «x1»$ のときの $y$ の値を答えよ。", x0=x0, y0=y0, x1=x1), a * x1 * x1,
               fmt("$«y0» = a \\times («x0»)^2$ より $a = «a»$。$y = «a» \\times («x1»)^2 = «r»$。", y0=y0, x0=x0, a=a, x1=x1, r=a * x1 * x1))


def _dice_ways(s): return sum(1 for i in range(1, 7) for j in range(1, 7) if i + j == s)


def t_dice():
    s = R.randint(2, 12); w = _dice_ways(s); p = Fraction(w, 36)
    return add(8, "junior", 2, "確率",
               fmt("大小2つのさいころを投げるとき、出た目の和が $«s»$ になる確率を既約分数 $\\dfrac{a}{b}$ で表す。$a + b$ を答えよ。", s=s),
               p.numerator + p.denominator,
               fmt("和が $«s»$ になるのは $«w»$ 通り、全体は $36$ 通り。$\\dfrac{«w»}{36} = «f»$ より $a + b = «t»$。", s=s, w=w, f=fr(p), t=p.numerator + p.denominator))


def t_consecutive():
    n = R.randint(10, 60)
    if R.randint(0, 1):
        return add(9, "junior", 2, "整数の文章題", fmt("連続する3つの整数の和が $«S»$ のとき、最も大きい数を答えよ。", S=3 * n), n + 1,
                   fmt("真ん中を $n$ とすると $3n = «S»$ より $n = «n»$。最大は $«m»$。", S=3 * n, n=n, m=n + 1))
    return add(9, "junior", 2, "整数の文章題", fmt("連続する5つの整数の和が $«S»$ のとき、最も小さい数を答えよ。", S=5 * n), n - 2,
               fmt("真ん中を $n$ とすると $5n = «S»$ より $n = «n»$。最小は $«m»$。", S=5 * n, n=n, m=n - 2))


def t_sumsq_xy():
    s = R.randint(3, 9); p = R.randint(1, (s * s - 1) // 2)
    return add(10, "junior", 2, "式の値", fmt("$x + y = «s»$、$xy = «p»$ のとき、$x^2 + y^2$ の値を答えよ。", s=s, p=p), s * s - 2 * p,
               fmt("$x^2 + y^2 = (x + y)^2 - 2xy = «a» - «b» = «r»$。", a=s * s, b=2 * p, r=s * s - 2 * p))


def t_polygon():
    n = R.choice([5, 6, 8, 9, 10, 12]); v = 180 * (n - 2) // n
    assert 180 * (n - 2) % n == 0
    return add(11, "junior", 1, "多角形の角", fmt("正$«n»$角形の1つの内角は何度か。", n=n), v,
               fmt("内角の和は $180^\\circ \\times («n» - 2) = «t»^\\circ$。1つ分は $«t»^\\circ \\div «n» = «v»^\\circ$。", n=n, t=180 * (n - 2), v=v))


def t_notdiv():
    N = R.choice([60, 100, 120, 150, 200]); a, b = R.choice([(2, 3), (3, 4), (2, 5), (3, 5), (4, 6), (3, 7), (2, 7)])
    cnt = sum(1 for i in range(1, N + 1) if i % a and i % b); l = a * b // gcd(a, b)
    return add(12, "junior", 3, "倍数の個数", fmt("$1$ から $«N»$ までの整数のうち、$«a»$ でも $«b»$ でも割り切れない数はいくつあるか。", N=N, a=a, b=b), cnt,
               fmt("$«a»$ の倍数は $«A»$ 個、$«b»$ の倍数は $«B»$ 個、$«l»$ の倍数は $«L»$ 個。どちらかで割り切れるのは $«A» + «B» - «L» = «U»$ 個。$«N» - «U» = «c»$。",
                   a=a, b=b, l=l, A=N // a, B=N // b, L=N // l, U=N // a + N // b - N // l, N=N, c=cnt))


def t_min():
    p, m = R.randint(1, 7), R.randint(-6, 9)
    return add(13, "math1a", 1, "二次関数の最小値", fmt("二次関数 $y = «f»$ の最小値を答えよ。", f=poly([(1, "x^2"), (-2 * p, "x"), (p * p + m, "")])), m,
               fmt("$y = («l»)^2 «s»$ と平方完成でき、最小値は $«m»$。", l=lin("x", -p), s=f"+ {m}" if m >= 0 else f"- {-m}", m=m))


def t_comb():
    n, r = R.randint(5, 11), R.randint(2, 4)
    num = [n - i for i in range(r)]; den = [r - i for i in range(r)]
    return add(14, "math1a", 1, "組合せ", fmt("${}_{«n»}\\mathrm{C}_{«r»}$ の値を答えよ。", n=n, r=r), comb(n, r),
               fmt("${}_{«n»}\\mathrm{C}_{«r»} = \\dfrac{«a»}{«b»} = «v»$。", n=n, r=r, a=prod_str(num), b=prod_str(den), v=comb(n, r)))


def t_absineq():
    a, b = R.randint(-3, 5), R.randint(2, 8)
    cnt = sum(1 for x in range(-30, 31) if abs(x - a) < b); assert cnt == 2 * b - 1
    return add(15, "math1a", 1, "絶対値と不等式", fmt("$|«l»| < «b»$ を満たす整数 $x$ はいくつあるか。", l=lin("x", -a), b=b), cnt,
               fmt("$-«b» < «l» < «b»$ より $«lo» < x < «hi»$。整数は $«l1»$ から $«h1»$ の $«c»$ 個。",
                   b=b, l=lin("x", -a), lo=a - b, hi=a + b, l1=a - b + 1, h1=a + b - 1, c=cnt))


def t_cosine():
    a, b = R.randint(2, 15), R.randint(2, 15); ang = R.choice([60, 120])
    c2 = a * a + b * b - a * b if ang == 60 else a * a + b * b + a * b
    c = isqrt(c2)
    if c * c != c2 or a == b: return False
    return add(16, "math1a", 2, "余弦定理",
               fmt("三角形 $\\mathrm{ABC}$ で $\\mathrm{AB} = «a»$、$\\mathrm{AC} = «b»$、$\\angle \\mathrm{A} = «g»^\\circ$ のとき、$\\mathrm{BC}$ の長さを答えよ。", a=a, b=b, g=ang), c,
               fmt("$\\mathrm{BC}^2 = «a»^2 + «b»^2 - 2 \\cdot «a» \\cdot «b» \\cos «g»^\\circ = «s» «o» «p» = «c2»$ より $\\mathrm{BC} = «c»$。",
                   a=a, b=b, g=ang, s=a * a + b * b, o="-" if ang == 60 else "+", p=a * b, c2=c2, c=c))


def t_divisors():
    N = R.choice([12, 18, 20, 24, 28, 30, 36, 40, 45, 48, 50, 60, 72, 90, 100, 120, 180, 200, 240, 360, 720])
    f = sp.factorint(N); cnt = sp.divisor_count(N)
    fac = " \\times ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    pr = "".join(f"({e} + 1)" for _, e in sorted(f.items()))
    return add(17, "math1a", 2, "約数の個数", fmt("$«N»$ の正の約数はいくつあるか。", N=N), int(cnt),
               fmt("$«N» = «fac»$ なので $«pr» = «c»$ 個。", N=N, fac=fac, pr=pr, c=int(cnt)))


def t_double_root():
    r1, r2 = R.randint(2, 6), R.randint(-5, -1); c, d = r1 + r2, -r1 * r2
    eq = poly([(1, "x^2"), (2, "kx"), (c, "k"), (d, "")]); rest = poly([(c, "k"), (d, "")])
    k = sp.Symbol("k"); assert sorted(sp.solve(k * k - (c * k + d), k)) == sorted([r1, r2])
    return add(18, "math1a", 2, "重解条件", fmt("$x$ の二次方程式 $«eq» = 0$ が重解をもつような、正の定数 $k$ の値を答えよ。", eq=eq), r1,
               fmt("判別式 $\\dfrac{D}{4} = k^2 - («rest») = 0$ より $(«a»)(«b») = 0$。正なので $k = «r1»$。",
                   rest=rest, a=lin("k", -r1), b=lin("k", -r2), r1=r1))


def t_diophantine():
    a, b = R.randint(2, 9), R.randint(2, 9)
    if gcd(a, b) != 1 or a == b: return False
    x = next(v for v in range(1, 100) if (1 - a * v) % b == 0); y = (1 - a * x) // b
    assert a * x + b * y == 1
    return add(19, "math1a", 2, "不定方程式",
               fmt("$«eq» = 1$ を満たす整数 $x,\\ y$ のうち、$x$ が正で最小となるものについて $x - y$ の値を答えよ。", eq=poly([(a, "x"), (b, "y")])), x - y,
               fmt("$«a»x \\equiv 1 \\pmod «b»$ を満たす最小の正の整数は $x = «x»$。このとき $y = «y»$。$x - y = «r»$。", a=a, b=b, x=x, y=y, r=x - y))


def t_balls():
    r, w = R.randint(3, 5), R.randint(2, 4); p = Fraction(comb(r, 2) * w, comb(r + w, 3))
    return add(20, "math1a", 2, "確率（組合せ）",
               fmt("赤玉$«r»$個、白玉$«w»$個が入った袋から同時に3個取り出す。赤玉2個・白玉1個となる確率を既約分数 $\\dfrac{a}{b}$ で表す。$a + b$ を答えよ。", r=r, w=w),
               p.numerator + p.denominator,
               fmt("${}_{«r»}\\mathrm{C}_2 \\times {}_{«w»}\\mathrm{C}_1 = «x»$ 通り、全体は ${}_{«n»}\\mathrm{C}_3 = «y»$ 通り。$«f»$ より $a + b = «t»$。",
                   r=r, w=w, x=comb(r, 2) * w, n=r + w, y=comb(r + w, 3), f=fr(p), t=p.numerator + p.denominator))


def t_log():
    a, m, c, n = R.choice([2, 3, 5]), R.randint(2, 5), R.choice([2, 3, 4, 5, 10]), R.randint(2, 4)
    return add(21, "math2b", 1, "対数", fmt("$\\log_{«a»} «A» + \\log_{«c»} «C»$ の値を答えよ。", a=a, A=a ** m, c=c, C=c ** n), m + n,
               fmt("$\\log_{«a»} «A» = «m»$、$\\log_{«c»} «C» = «n»$ なので $«t»$。", a=a, A=a ** m, m=m, c=c, C=c ** n, n=n, t=m + n))


def t_arith():
    a1, d, n = R.randint(2, 9), R.randint(2, 9), R.randint(10, 30)
    return add(22, "math2b", 1, "等差数列", fmt("初項 $«a»$、公差 $«d»$ の等差数列の第 $«n»$ 項を答えよ。", a=a1, d=d, n=n), a1 + (n - 1) * d,
               fmt("$a_n = «a» + (n - 1) \\times «d»$。$a_{«n»} = «a» + «x» = «r»$。", a=a1, d=d, n=n, x=(n - 1) * d, r=a1 + (n - 1) * d))


def t_binomial():
    n, k, b = R.randint(4, 6), R.randint(2, 3), R.randint(2, 3)
    if k >= n: return False
    v = comb(n, k) * b ** (n - k)
    x = sp.Symbol("x"); assert sp.Poly(sp.expand((x + b) ** n), x).coeff_monomial(x ** k) == v
    return add(23, "math2b", 2, "二項定理", fmt("$(x + «b»)^{«n»}$ を展開したときの $x^{«k»}$ の係数を答えよ。", b=b, n=n, k=k), v,
               fmt("${}_{«n»}\\mathrm{C}_{«k»} \\times «b»^{«e»} = «c» \\times «p» = «v»$。", n=n, k=k, b=b, e=n - k, c=comb(n, k), p=b ** (n - k), v=v))


def t_integral():
    a, p, t = R.choice([3, 6]), R.choice([2, 4, 6]), R.randint(1, 4)
    x = sp.Symbol("x"); v = sp.integrate(a * x ** 2 + p * x, (x, 0, t)); assert v == int(v)
    return add(24, "math2b", 2, "定積分", fmt("定積分 $\\displaystyle\\int_0^{«t»} («f»)\\,dx$ の値を答えよ。", t=t, f=poly([(a, "x^2"), (p, "x")])), int(v),
               fmt("$\\left[«g»\\right]_0^{«t»} = «x» + «y» = «v»$。", g=poly([(a // 3, "x^3"), (p // 2, "x^2")]), t=t, x=a // 3 * t ** 3, y=p // 2 * t ** 2, v=int(v)))


def t_derivative_value():
    c, t = R.randint(2, 9), R.randint(-3, 4); v = 3 * t * t - c
    return add(25, "math2b", 1, "微分係数", fmt("$f(x) = «f»$ の $x = «t»$ における微分係数 $f'(«t»)$ を答えよ。", f=poly([(1, "x^3"), (-c, "x")]), t=t), v,
               fmt("$f'(x) = 3x^2 - «c»$ より $f'(«t») = «a» - «c» = «v»$。", c=c, t=t, a=3 * t * t, v=v))


def t_local_max():
    p, q = R.randint(-4, 5), R.randint(-4, 6)
    if q - p < 2 or (q - p) % 2: return False
    d = R.randint(-3, 6); x = sp.Symbol("x")
    f = x ** 3 - sp.Rational(3 * (p + q), 2) * x ** 2 + 3 * p * q * x + d
    assert sp.expand(sp.diff(f, x) - 3 * (x - p) * (x - q)) == 0
    v = int(f.subs(x, p))
    return add(26, "math2b", 2, "極大値",
               fmt("$f(x) = «f»$ の極大値を答えよ。", f=poly([(1, "x^3"), (-3 * (p + q) // 2, "x^2"), (3 * p * q, "x"), (d, "")])), v,
               fmt("$f'(x) = 3(«a»)(«b»)$。$x = «p»$ で極大となり $f(«p») = «v»$。", a=lin("x", -p), b=lin("x", -q), p=p, v=v))


def t_sigma():
    n = R.randint(5, 14)
    if R.randint(0, 1):
        v = n * (n + 1) * (2 * n + 1) // 6
        return add(27, "math2b", 2, "Σの計算", fmt("$1^2 + 2^2 + 3^2 + \\cdots + «n»^2$ の値を答えよ。", n=n), v,
                   fmt("$\\displaystyle\\sum_{k=1}^{n} k^2 = \\dfrac{n(n + 1)(2n + 1)}{6}$ より $\\dfrac{«n» \\cdot «a» \\cdot «b»}{6} = «v»$。", n=n, a=n + 1, b=2 * n + 1, v=v))
    v = (n * (n + 1) // 2) ** 2
    return add(27, "math2b", 2, "Σの計算", fmt("$1^3 + 2^3 + 3^3 + \\cdots + «n»^3$ の値を答えよ。", n=n), v,
               fmt("$\\displaystyle\\sum_{k=1}^{n} k^3 = \\left\\{\\dfrac{n(n + 1)}{2}\\right\\}^2$ より $«h»^2 = «v»$。", h=n * (n + 1) // 2, v=v))


def t_geometric():
    a, r, M = R.randint(1, 3), R.choice([2, 3]), R.randint(100, 5000)
    S = lambda n: a * (r ** n - 1) // (r - 1)
    n = next(i for i in range(1, 40) if S(i) > M)
    if n < 3: return False
    sn = fmt("«a»(«r»^n - 1)", a=a if a > 1 else "", r=r) if r == 2 else fmt("\\dfrac{«a»(«r»^n - 1)}{2}", a=a if a > 1 else "", r=r)
    return add(28, "math2b", 3, "等比数列の和", fmt("初項 $«a»$、公比 $«r»$ の等比数列の初項から第 $n$ 項までの和が、初めて $«M»$ を超える $n$ を答えよ。", a=a, r=r, M=M), n,
               fmt("$S_n = «sn»$。$S_{«p»} = «sp»$、$S_{«n»} = «sn2»$ より $n = «n»$。", sn=sn, p=n - 1, sp=S(n - 1), n=n, sn2=S(n)))


def t_recurrence():
    c, m = R.randint(1, 3), R.randint(5, 10); v = (1 + c) * 2 ** (m - 1) - c
    a = 1
    for _ in range(m - 1): a = 2 * a + c
    assert a == v
    return add(29, "math2b", 3, "漸化式", fmt("$a_1 = 1$、$a_{n+1} = 2a_n + «c»$ で定まる数列の $a_{«m»}$ を答えよ。", c=c, m=m), v,
               fmt("$a_{n+1} + «c» = 2(a_n + «c»)$ より $a_n + «c» = «k» \\cdot 2^{n-1}$。$a_{«m»} = «k» \\times «p» - «c» = «v»$。", c=c, k=1 + c, m=m, p=2 ** (m - 1), v=v))


def t_circle():
    a, b, r = R.randint(-4, 4), R.randint(-4, 4), R.randint(3, 9)
    if a == 0 or b == 0: return False
    eq = poly([(1, "x^2"), (1, "y^2"), (-2 * a, "x"), (-2 * b, "y"), (a * a + b * b - r * r, "")])
    return add(30, "math2b", 1, "円の方程式", fmt("円 $«eq» = 0$ の半径を答えよ。", eq=eq), r,
               fmt("$(«a»)^2 + («b»)^2 = «r2»$ と変形でき、半径は $«r»$。", a=lin("x", -a), b=lin("y", -b), r2=r * r, r=r))


def t_parabola_area():
    m = R.choice([2, 3, 4, 5]); p = Fraction(m ** 3, 6)
    return add(31, "math2b", 3, "囲まれた面積", fmt("放物線 $y = «f»$ と $x$ 軸で囲まれた部分の面積を既約分数 $\\dfrac{a}{b}$ で表す。$a + b$ を答えよ。", f=poly([(1, "x^2"), (-m, "x")])),
               p.numerator + p.denominator,
               fmt("$\\displaystyle\\int_0^{«m»} («g»)\\,dx = \\dfrac{«m»^3}{6} = «f»$。$a + b = «t»$。", m=m, g=poly([(m, "x"), (-1, "x^2")]), f=fr(p), t=p.numerator + p.denominator))


def t_limit_seq():
    c, q = R.randint(1, 3), R.randint(2, 5); a = c * q; b, d = R.randint(1, 5), R.randint(1, 5)
    return add(32, "math3c", 1, "数列の極限",
               fmt("$n \\to \\infty$ のとき、$\\dfrac{«u»}{«l»}$ の極限値を答えよ。", u=poly([(a, "n^2"), (b, "")]), l=poly([(c, "n^2"), (d, "n")])), q,
               fmt("分母分子を $n^2$ で割ると $\\dfrac{«a» + «b»/n^2}{«c» + «d»/n} \\to \\dfrac{«a»}{«c»} = «q»$。", a=a, b=b, c=c, d=d, q=q))


def t_complex_power():
    n, plus = R.choice([4, 8, 12]), R.randint(0, 1); z = complex(1, 1 if plus else -1) ** n
    v = int(z.real); assert abs(z.imag) < 1e-9
    s = "+" if plus else "-"
    return add(33, "math3c", 1, "複素数の累乗", fmt("$i$ を虚数単位とする。$(1 «s» i)^{«n»}$ の値を答えよ。", s=s, n=n), v,
               fmt("$(1 «s» i)^2 = «w»$ なので $(1 «s» i)^{«n»} = («w»)^{«h»} = «v»$。", s=s, w="2i" if plus else "-2i", n=n, h=n // 2, v=v))


def t_sin_limit():
    k = R.randint(2, 9)
    return add(34, "math3c", 1, "三角関数の極限", fmt("$x \\to 0$ のとき、$\\dfrac{\\sin «k»x}{x}$ の極限値を答えよ。", k=k), k,
               fmt("$\\dfrac{\\sin «k»x}{«k»x} \\times «k» \\to 1 \\times «k» = «k»$。", k=k))


def t_chain():
    a, b, n, t = R.randint(2, 4), R.randint(1, 3), R.randint(3, 5), R.randint(0, 2)
    v = n * a * (a * t + b) ** (n - 1)
    return add(35, "math3c", 1, "合成関数の微分", fmt("$y = («l»)^{«n»}$ の $x = «t»$ における微分係数を答えよ。", l=poly([(a, "x"), (b, "")]), n=n, t=t), v,
               fmt("$y' = «n»(«l»)^{«m»} \\times «a»$。$x = «t»$ で $«n» \\times «u»^{«m»} \\times «a» = «v»$。", n=n, l=poly([(a, "x"), (b, "")]), m=n - 1, a=a, t=t, u=a * t + b, v=v))


def t_inf_series():
    a = R.randint(2, 12); p, q = R.choice([(1, 2), (1, 3), (2, 3), (3, 4), (2, 5), (3, 5), (4, 5), (1, 4)])
    if (a * q) % (q - p): return False
    v = a * q // (q - p)
    return add(36, "math3c", 2, "無限等比級数", fmt("初項 $«a»$、公比 $\\dfrac{«p»}{«q»}$ の無限等比級数の和を答えよ。", a=a, p=p, q=q), v,
               fmt("$\\dfrac{«a»}{1 - \\frac{«p»}{«q»}} = \\dfrac{«a»}{\\frac{«d»}{«q»}} = «v»$。", a=a, p=p, q=q, d=q - p, v=v))


def t_ellipse():
    a, b, c = R.choice([(5, 3, 4), (13, 5, 12), (10, 6, 8), (15, 9, 12), (17, 8, 15), (25, 7, 24), (26, 10, 24), (5, 4, 3), (10, 8, 6), (13, 12, 5), (15, 12, 9), (17, 15, 8), (20, 16, 12)])
    assert a * a - b * b == c * c
    return add(37, "math3c", 2, "楕円の焦点", fmt("楕円 $\\dfrac{x^2}{«A»} + \\dfrac{y^2}{«B»} = 1$ の2つの焦点の間の距離を答えよ。", A=a * a, B=b * b), 2 * c,
               fmt("$c = \\sqrt{«A» - «B»} = «c»$。焦点は $(\\pm «c»,\\ 0)$ で、距離は $«d»$。", A=a * a, B=b * b, c=c, d=2 * c))


def t_revolution():
    a = R.choice([2, 4, 6, 8, 10]); v = a * a // 2
    return add(38, "math3c", 3, "回転体の体積",
               fmt("曲線 $y = \\sqrt{x}$（$0 \\leqq x \\leqq «a»$）と $x$ 軸、直線 $x = «a»$ で囲まれた部分を $x$ 軸のまわりに1回転させた立体の体積を $k\\pi$ と表す。$k$ を答えよ。", a=a), v,
               fmt("$V = \\pi\\displaystyle\\int_0^{«a»} (\\sqrt{x})^2\\,dx = \\pi\\left[\\dfrac{x^2}{2}\\right]_0^{«a»} = «v»\\pi$。", a=a, v=v))


def t_dot():
    p, q, r, s = (R.randint(-5, 5) for _ in range(4))
    if 0 in (p, q, r, s): return False
    return add(39, "math3c", 1, "内積", fmt("$\\vec{a} = («p»,\\ «q»)$、$\\vec{b} = («r»,\\ «s»)$ のとき、内積 $\\vec{a} \\cdot \\vec{b}$ の値を答えよ。", p=p, q=q, r=r, s=s), p * r + q * s,
               fmt("$(«p») \\times («r») + («q») \\times («s») = «v»$。", p=p, q=q, r=r, s=s, v=p * r + q * s))


def t_modulus():
    a, b, c = R.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10), (7, 24, 25), (9, 12, 15)])
    sa, sb = R.choice([1, -1]), R.choice([1, -1])
    return add(40, "math3c", 1, "複素数の絶対値", fmt("複素数 $z = «z»$ のとき、$|z|$ の値を答えよ。", z=poly([(sa * a, ""), (sb * b, "i")])), c,
               fmt("$|z| = \\sqrt{«a»^2 + «b»^2} = \\sqrt{«s»} = «c»$。", a=a, b=b, s=a * a + b * b, c=c))


INTEGER_TEMPLATES = [t_linear, t_simul, t_signs, t_sqrt, t_quad_roots, t_pythag, t_parabola, t_dice, t_consecutive, t_sumsq_xy, t_polygon,
                     t_notdiv, t_min, t_comb, t_absineq, t_cosine, t_divisors, t_double_root, t_diophantine, t_balls, t_log, t_arith,
                     t_binomial, t_integral, t_derivative_value, t_local_max, t_sigma, t_geometric, t_recurrence, t_circle,
                     t_parabola_area, t_limit_seq, t_complex_power, t_sin_limit, t_chain, t_inf_series, t_ellipse, t_revolution,
                     t_dot, t_modulus]


# ═════════ 4択問題 ═════════
def c_factor():
    p, q = R.randint(-6, 6), R.randint(-6, 6)
    if 0 in (p, q) or p == q or p == -q: return False
    f = lambda a, b: f"$({lin('x', a)})({lin('x', b)})$"
    cs = choice_set(f(p, q), [f(-p, -q), f(-p, q), f(p, -q)])
    return add(41, "junior", 1, "因数分解", fmt("$«e»$ を因数分解したものを選べ。", e=poly([(1, "x^2"), (p + q, "x"), (p * q, "")])), cs[1],
               fmt("和が $«s»$、積が $«m»$ になる2数は $«p»,\\ «q»$ なので $«a»$。", s=p + q, m=p * q, p=p, q=q, a=f(p, q).strip("$")), cs[0])


def c_quad_solution():
    p, q = R.randint(-6, 6), R.randint(-6, 6)
    if 0 in (p, q) or p == q or p == -q: return False
    f = lambda a, b: f"$x = {a},\\ {b}$"
    cs = choice_set(f(p, q), [f(-p, -q), f(-p, q), f(p, -q)])
    return add(42, "math1a", 1, "二次方程式の解",
               fmt("二次方程式 $«e» = 0$ の解を選べ。", e=poly([(1, "x^2"), (-(p + q), "x"), (p * q, "")])), cs[1],
               fmt("$(«a»)(«b») = 0$ より $x = «p»,\\ «q»$。", a=lin("x", -p), b=lin("x", -q), p=p, q=q), cs[0])


def c_vertex():
    p, q = R.randint(-5, 5), R.randint(-6, 6)
    if p == 0 or q == 0: return False
    f = lambda a, b: f"$({a},\\ {b})$"
    cs = choice_set(f(p, q), [f(-p, q), f(p, -q), f(-p, -q)])
    return add(43, "math1a", 2, "放物線の頂点", fmt("二次関数 $y = «e»$ のグラフの頂点の座標を選べ。", e=poly([(1, "x^2"), (-2 * p, "x"), (p * p + q, "")])), cs[1],
               fmt("$y = («l»)^2 «s»$ と平方完成できるので、頂点は $(«p»,\\ «q»)$。", l=lin("x", -p), s=f"+ {q}" if q >= 0 else f"- {-q}", p=p, q=q), cs[0])


_TRIG = {("\\sin", 30): "\\dfrac{1}{2}", ("\\sin", 45): "\\dfrac{\\sqrt{2}}{2}", ("\\sin", 60): "\\dfrac{\\sqrt{3}}{2}",
         ("\\cos", 30): "\\dfrac{\\sqrt{3}}{2}", ("\\cos", 45): "\\dfrac{\\sqrt{2}}{2}", ("\\cos", 60): "\\dfrac{1}{2}",
         ("\\tan", 30): "\\dfrac{1}{\\sqrt{3}}", ("\\tan", 45): "1", ("\\tan", 60): "\\sqrt{3}"}
_TRIG_POOL = ["\\dfrac{1}{2}", "\\dfrac{\\sqrt{2}}{2}", "\\dfrac{\\sqrt{3}}{2}", "1", "\\dfrac{1}{\\sqrt{3}}", "\\sqrt{3}"]


def c_trig():
    fn, ang = R.choice(list(_TRIG)); good = _TRIG[(fn, ang)]
    others = [v for v in _TRIG_POOL if v != good]; R.shuffle(others)
    cs = choice_set(f"${good}$", [f"${o}$" for o in others[:3]])
    return add(44, "math1a", 1, "三角比", fmt("$«f» «a»^\\circ$ の値を選べ。", f=fn, a=ang), cs[1],
               fmt("三角比の表より $«f» «a»^\\circ = «v»$。", f=fn, a=ang, v=good), cs[0])


def c_derivative():
    c, n = R.randint(1, 5), R.randint(3, 6)
    f = lambda k, e: f"$f'(x) = {mono(k, e)}$"
    cs = choice_set(f(c * n, n - 1), [f(c, n - 1), f(c * n, n), f(c * (n - 1), n - 1)])
    return add(45, "math2b", 1, "導関数", fmt("$f(x) = «e»$ の導関数 $f'(x)$ を選べ。", e=mono(c, n)), cs[1],
               fmt("$(x^n)' = nx^{n-1}$ より $f'(x) = «k»$。", k=mono(c * n, n - 1)), cs[0])


def c_indefinite():
    n, k = R.randint(1, 4), R.randint(1, 3); c = k * (n + 1)
    f = lambda kk, e: f"${mono(kk, e)} + C$"
    cs = choice_set(f(k, n + 1), [f(c, n + 1), f(k, n), f(c * n, n - 1) if n > 1 else f(c * 2, 2)])
    return add(46, "math2b", 2, "不定積分", fmt("$\\displaystyle\\int «e»\\,dx$ を選べ。ただし $C$ は積分定数。", e=mono(c, n)), cs[1],
               fmt("$\\displaystyle\\int x^n\\,dx = \\dfrac{x^{n+1}}{n+1} + C$ より $\\dfrac{«c»}{«m»} x^{«e»} + C = «k»$。", c=c, m=n + 1, e=n + 1, k=f(k, n + 1).strip("$")), cs[0])


def c_prob():
    s = R.randint(2, 12); w = _dice_ways(s); p = Fraction(w, 36)
    cand = [Fraction(w + 1, 36), Fraction(max(w - 1, 1), 36), Fraction(w, 12), Fraction(w, 18), Fraction(w + 2, 36), Fraction(w, 6)]
    wrongs = []
    for f in cand:
        t = f"${fr(f)}$"
        if f != p and t not in wrongs: wrongs.append(t)
    cs = choice_set(f"${fr(p)}$", wrongs)
    if cs is None: return False
    return add(47, "junior", 2, "確率の値", fmt("大小2つのさいころを投げるとき、出た目の和が $«s»$ になる確率を選べ。", s=s), cs[1],
               fmt("和が $«s»$ になるのは $«w»$ 通り、全体は $36$ 通り。$\\dfrac{«w»}{36} = «f»$。", s=s, w=w, f=fr(p)), cs[0])


def c_linear_ineq():
    a = R.choice([2, 3, 4, -2, -3, -4]); t = R.choice([v for v in range(-6, 7) if v]); b = R.randint(-6, 6)
    c = a * t + b
    sign = ">" if a > 0 else "<"
    f = lambda s, v: f"$x {s} {v}$"
    cs = choice_set(f(sign, t), [f(">" if sign == "<" else "<", t), f(sign, -t), f(">" if sign == "<" else "<", -t)])
    return add(48, "junior", 1, "不等式", fmt("不等式 $«l» > «c»$ の解を選べ。", l=poly([(a, "x"), (b, "")]), c=c), cs[1],
               fmt("$«l2» > «r»$。両辺を $«a»$ で割る" + ("と、負の数で割るので不等号の向きが変わり " if a < 0 else "と ") + "$x «s» «t»$。",
                   l2=poly([(a, "x")]), r=c - b, a=a, s=sign, t=t), cs[0])


_NEC = ["必要条件であるが十分条件ではない", "十分条件であるが必要条件ではない", "必要十分条件である", "必要条件でも十分条件でもない"]
_NEC_ITEMS = [  # (命題, 正解の番号, 解説)
    ("$x = 2$ は $x^2 = 4$ であるための", 1, "$x = 2$ ならば $x^2 = 4$ は成り立つが、$x^2 = 4$ でも $x = -2$ があるので逆は成り立たない。"),
    ("$x^2 = 4$ は $x = 2$ であるための", 0, "$x = 2$ ならば $x^2 = 4$ は成り立つが、逆は $x = -2$ があるので成り立たない。$x^2 = 4$ は必要条件。"),
    ("$x > 3$ は $x > 1$ であるための", 1, "$x > 3$ ならば $x > 1$ は成り立つが、逆は成り立たない。"),
    ("$x > 1$ は $x > 3$ であるための", 0, "$x > 3$ ならば $x > 1$ は成り立つが、逆は成り立たない。$x > 1$ は必要条件。"),
    ("$xy = 0$ は「$x = 0$ かつ $y = 0$」であるための", 0, "「$x = 0$ かつ $y = 0$」ならば $xy = 0$ だが、逆は $x = 0$, $y = 1$ のとき成り立たない。"),
    ("「$x = 0$ かつ $y = 0$」は $x^2 + y^2 = 0$ であるための", 2, "$x^2 + y^2 = 0$ ならば $x = 0$ かつ $y = 0$ で、逆も成り立つ。"),
    ("$a > 0$ は $a^2 > 0$ であるための", 1, "$a > 0$ ならば $a^2 > 0$ だが、$a = -1$ のとき逆は成り立たない。"),
    ("$x$ が 6 の倍数であることは、$x$ が 3 の倍数であるための", 1, "6 の倍数は 3 の倍数だが、$x = 3$ のとき逆は成り立たない。"),
    ("$|x| < 1$ は $x^2 < 1$ であるための", 2, "$|x| < 1 \\iff x^2 < 1$ で、どちらからも言える。"),
    ("$x^2 - 3x + 2 = 0$ は $x = 1$ であるための", 0, "$x = 1$ ならば成り立つが、$x = 2$ でも成り立つので逆は成り立たない。"),
]


def c_necessary():
    stmt, idx, expl = R.choice(_NEC_ITEMS)
    return add(49, "math1a", 2, "必要条件・十分条件", f"{stmt}、次のどれか。", idx, expl, [f"{c}" for c in _NEC])


_ARG = [("1 + i", "\\dfrac{\\pi}{4}"), ("1 + \\sqrt{3}i", "\\dfrac{\\pi}{3}"), ("-1 + i", "\\dfrac{3\\pi}{4}"),
        ("\\sqrt{3} + i", "\\dfrac{\\pi}{6}"), ("-1 + \\sqrt{3}i", "\\dfrac{2\\pi}{3}"), ("-\\sqrt{3} + i", "\\dfrac{5\\pi}{6}")]


def c_arg():
    z, good = R.choice(_ARG)
    others = [a for _, a in _ARG if a != good]; R.shuffle(others)
    cs = choice_set(f"${good}$", [f"${o}$" for o in others[:3]])
    return add(50, "math3c", 2, "複素数の偏角", fmt("複素数 $z = «z»$ の偏角 $\\theta$（$0 \\leqq \\theta < 2\\pi$）を選べ。", z=z), cs[1],
               fmt("$z$ を複素数平面に図示して、実軸の正の向きとなす角を調べると $\\theta = «g»$。", g=good), cs[0])


_DERIV = [("\\sin x", "\\cos x"), ("\\cos x", "-\\sin x"), ("e^x", "e^x"), ("\\log x", "\\dfrac{1}{x}"),
          ("\\tan x", "\\dfrac{1}{\\cos^2 x}"), ("e^{2x}", "2e^{2x}")]
_DERIV_WRONG = ["\\cos x", "-\\sin x", "\\sin x", "e^x", "\\dfrac{1}{x}", "x e^{x-1}", "-\\cos x", "\\dfrac{1}{\\sin^2 x}"]


def c_deriv_funcs():
    f, good = R.choice(_DERIV)
    others = [w for w in _DERIV_WRONG if w != good]; R.shuffle(others)
    cs = choice_set(f"${good}$", [f"${o}$" for o in others[:3]])
    return add(51, "math3c", 1, "いろいろな関数の微分", fmt("$f(x) = «f»$ の導関数 $f'(x)$ を選べ。", f=f), cs[1],
               fmt("公式より $(«f»)' = «g»$。", f=f, g=good), cs[0])


CHOICE_TEMPLATES = [c_factor, c_quad_solution, c_vertex, c_trig, c_derivative, c_indefinite, c_prob, c_linear_ineq,
                    c_necessary, c_arg, c_deriv_funcs]


def generate(per_template=8, per_choice=8):
    OUT.clear(); _seen.clear()
    for fn in INTEGER_TEMPLATES: make(0, per_template, fn)
    for fn in CHOICE_TEMPLATES: make(0, per_choice, fn)
    return list(OUT)


if __name__ == "__main__":
    ps = generate()
    print(len(ps), "問")
    for p in ps[::17]:
        print(p["id"], p["category"], p["difficulty"], "|", p["plain"][:90], "->", p["answer"])
