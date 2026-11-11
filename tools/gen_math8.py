"""最上級（難易度 4）の数学の問題を、1問ずつ手で書いたもの。

- 数字を変えて作る問題ではなく、発想や工夫が要る問題（難関大の入試の、易しめ〜標準くらいを目安にした自作問題）。
- 実際の入試問題をそのまま写したものではない（有名な定番の考え方を使った自作）。
- どの問題も、答えをコード（総当たり・sympy・分数の計算）で確かめてから登録する。
"""
import math
import itertools
from fractions import Fraction as F
import sympy as sp
from gen_problems import tex2plain
import gen_math7 as G7

OUT = []
_count = {}
x, t, n_ = sp.symbols("x t n", real=True)


def _add(unit, title, body, answer, expl, choices=None):
    _count[unit] = _count.get(unit, 0) + 1
    plain = tex2plain(body)
    p = dict(id=f"x8-{unit}-{_count[unit]}", category=G7.CAT[unit], difficulty=4, title=title, body=body,
             answer=answer, explanation=expl, plain=plain, unit=unit, rate_hint=1.8)
    if choices is not None:
        labels = ["①", "②", "③", "④"]
        p["choices"] = choices
        p["plain"] += "　" + "　".join(f"{labels[i]} {tex2plain(c)}" for i, c in enumerate(choices))
    else:
        assert isinstance(answer, int)
    OUT.append(p)


def num(unit, title, body, ans, expl):
    _add(unit, title, body, int(ans), expl)


def frac(unit, title, body, f, expl):
    f = F(f)
    assert f > 0 and f.denominator > 1, (body, f)
    _add(unit, title, body + "既約分数 $\\dfrac{p}{q}$ で表したとき、$p + q$ を答えよ。", f.numerator + f.denominator, expl)


def choice(unit, title, body, correct, wrongs, expl):
    opts = [correct] + list(wrongs)
    assert len(set(opts)) == 4
    G7.R.shuffle(opts)
    _add(unit, title, body, opts.index(correct), expl, opts)


def generate():
    OUT.clear(); _count.clear()

    # ───────── 整数 ─────────
    k = next(m for m in range(1, 2000) if sum(m // 5 ** i for i in range(1, 6)) == 100)
    num("h_nt", "階乗の末尾の 0", "$n!$ の末尾に並ぶ 0 の個数が、ちょうど 100 個になる最小の正の整数 $n$ を答えよ。", k,
        "末尾の 0 の個数は $\\left[\\dfrac{n}{5}\\right] + \\left[\\dfrac{n}{25}\\right] + \\left[\\dfrac{n}{125}\\right] + \\cdots$。$n = 400$ で 99 個、$n = 405$ で 100 個になる。")
    k = next(m for m in range(1, 5000) if (3 ** m - 1) % 2 ** 10 == 0)
    assert k == 256
    num("h_nt", "2 で何回割り切れるか", "$3^n - 1$ が $2^{10}$ で割り切れるような、最小の正の整数 $n$ を答えよ。", k,
        "$n$ が偶数のとき、$3^n - 1$ が 2 で割り切れる回数は、$n$ が 2 で割り切れる回数より 2 多い（$3^{2m} - 1 = (3^m - 1)(3^m + 1)$ をくり返す）。$n$ が奇数なら 1 回だけ。よって $n$ は $2^8 = 256$ の倍数。")
    k = next(m for m in range(1, 100) if int("1" * m) % 41 == 0)
    num("h_nt", "1 が並んだ数", "1 を $n$ 個並べた数 $11\\cdots1$ が 41 で割り切れるような、最小の正の整数 $n$ を答えよ。", k,
        "$11\\cdots1 = \\dfrac{10^n - 1}{9}$。$10^5 = 100000 = 41 \\times 2439 + 1$ より、$10^5 \\equiv 1 \\pmod{41}$ で、5 より小さい $n$ では成り立たない。")
    sols = [m for m in range(1, 1000) if math.isqrt(m * m + 2 * m + 12) ** 2 == m * m + 2 * m + 12]
    assert sols == [4]
    num("h_nt", "平方数になる条件", "$n^2 + 2n + 12$ が平方数になるような正の整数 $n$ を答えよ。", 4,
        "$(n + 1)^2 + 11 = m^2$ より $(m - n - 1)(m + n + 1) = 11$。11 は素数なので $m - n - 1 = 1$、$m + n + 1 = 11$。$n = 4$。")
    s = sum(m for m in range(1, 1000) if math.isqrt(m * m + 120) ** 2 == m * m + 120)
    num("h_nt", "根号が整数になる条件", "$\\sqrt{n^2 + 120}$ が整数となるような、すべての正の整数 $n$ の和を答えよ。", s,
        "$m^2 - n^2 = 120$、$(m - n)(m + n) = 120$。2 つの因数は偶奇が同じなので、ともに偶数。$(2, 60), (4, 30), (6, 20), (10, 12)$ から $n = 29, 13, 7, 1$。")
    sols = [(p, q) for p in sp.primerange(2, 500) for q in sp.primerange(2, 500) if p * p - 2 * q * q == 1]
    assert sols == [(3, 2)]
    num("h_nt", "素数の方程式", "素数 $p$、$q$ が $p^2 - 2q^2 = 1$ を満たすとき、$p + q$ を答えよ。", 5,
        "$p$ は奇数。$2q^2 = (p - 1)(p + 1)$ の右辺は 8 の倍数なので、$q^2$ は偶数で $q = 2$。このとき $p = 3$。")
    c = sum(1 for a in range(-50, 51) for b in range(-50, 51) if a * a + b * b == 2025)
    num("h_nt", "2 つの平方数の和", "$a^2 + b^2 = 2025$ を満たす整数の組 $(a, b)$ は何組あるか。", c,
        "$2025 = 3^4 \\cdot 5^2$。$3$ は 2 つの平方数の和に分けにくい素数なので、$a$、$b$ はともに 9 の倍数になる。$a = 9a'$、$b = 9b'$ として $a'^2 + b'^2 = 25$。整数解は 12 組。")
    s = sum(m for m in range(1, 101) if math.gcd(m, 100) == 1)
    num("h_nt", "互いに素な数の和", "100 以下の正の整数のうち、100 と互いに素なものすべての和を答えよ。", s,
        "100 と互いに素な数は 40 個あり、$m$ と $100 - m$ が組になる。和は $40 \\times 50 = 2000$。")
    c = sum(1 for a in range(1, 21) for b in range(a, 21) for cc in range(b, 21) if a + b + cc == 20)
    num("h_count", "和の分け方", "$a + b + c = 20$、$1 \\le a \\le b \\le c$ を満たす整数の組 $(a, b, c)$ は何組あるか。", c,
        "$a$ の値ごとに数える。$a = 1$ で 9 組、$a = 2$ で 8 組、$a = 3$ で 6 組、$a = 4$ で 5 組、$a = 5$ で 3 組、$a = 6$ で 2 組。合計 33 組。")
    c = sum(1 for a in range(1, 3000) for b in range(1, 3000) if a * a - b * b == 2025)
    num("h_nt", "平方の差", "$a^2 - b^2 = 2025$ を満たす正の整数の組 $(a, b)$ は何組あるか。", c,
        "$(a - b)(a + b) = 2025$。2025 は奇数なので、約数の組 $(d, \\tfrac{2025}{d})$（$d < 45$）がそのまま使える。2025 の約数は 15 個で、$d < 45$ は 7 個。")

    # ───────── 場合の数・確率 ─────────
    num("h_count", "立方体の塗り分け", "立方体の 6 つの面を、6 色すべてを 1 回ずつ使って塗る。回転して重なるものは同じとみなすと、何通りあるか。", 30,
        "1 つの色を上に固定すると、下の色は 5 通り。横の 4 面は円順列で $3! = 6$ 通り。$5 \\times 6 = 30$ 通り。")
    num("h_count", "正四面体の塗り分け", "異なる 6 色から 4 色を選び、正四面体の 4 つの面を 1 色ずつ塗る。回転して重なるものは同じとみなすと、何通りあるか。", math.comb(6, 4) * 2,
        "4 色の選び方は ${}_6\\mathrm{C}_4 = 15$ 通り。4 色の塗り方は、1 面を下に固定して残り 3 面の円順列 $2! = 2$ 通り。$15 \\times 2 = 30$ 通り。")
    pa = F(1, 6) / (1 - F(25, 36))
    frac("h_prob", "交互に投げるさいころ", "A、B が A から交互にさいころを投げ、先に 6 を出した人の勝ちとする。A が勝つ確率を", pa,
         "A が $k$ 回目に勝つ確率は $\\left(\\dfrac{25}{36}\\right)^{k-1} \\cdot \\dfrac{1}{6}$。無限等比級数の和で $\\dfrac{1/6}{1 - 25/36} = \\dfrac{6}{11}$。")
    w = sum(1 for s in itertools.product([0, 1], repeat=10) if "111" not in "".join(map(str, s)))
    frac("h_prob", "表が 3 回続かない確率", "硬貨を 10 回投げる。表が 3 回以上続けて出ることが一度もない確率を", F(w, 1024),
         "表が続かない列の数 $a_n$ は $a_n = a_{n-1} + a_{n-2} + a_{n-3}$（最後の裏の位置で分ける）を満たす。$a_{10} = 504$。$\\dfrac{504}{1024} = \\dfrac{63}{128}$。")
    d = sum(1 for p in itertools.permutations(range(7)) if all(p[i] != i for i in range(7)))
    num("h_count", "完全順列", "1 から 7 の番号のついた 7 枚のカードを、1 から 7 の番号のついた 7 つの箱に 1 枚ずつ入れる。どのカードも、同じ番号の箱に入らない入れ方は何通りか。", d,
        "完全順列の数 $W_n$ は $W_n = (n - 1)(W_{n-1} + W_{n-2})$、$W_1 = 0$、$W_2 = 1$。$W_7 = 1854$。")
    c = sum(1 for v in itertools.product(range(6), repeat=4) if sum(v) == 12)
    num("h_count", "上限のある分け方", "$x + y + z + w = 12$、$0 \\le x, y, z, w \\le 5$ を満たす整数の組は何組あるか。", c,
        "上限なしで ${}_{15}\\mathrm{C}_3 = 455$。1 つが 6 以上の場合 $4 \\times {}_{9}\\mathrm{C}_3 = 336$、2 つが 6 以上の場合 $6 \\times {}_{3}\\mathrm{C}_3 = 6$。包除原理で $455 - 336 + 6 = 125$。")
    num("h_count", "正多角形と長方形", "正十二角形の 12 個の頂点から 4 個を選んで四角形をつくる。長方形になるものは何個あるか。", math.comb(6, 2),
        "長方形の対角線は、外接円の直径。直径は 6 本あり、そのうち 2 本を選ぶと長方形が 1 つ決まる。${}_6\\mathrm{C}_2 = 15$ 個。")
    cat = math.comb(12, 6) // 7
    num("h_count", "対角線を越えない道順", "座標平面で、点 $(0, 0)$ から点 $(6, 6)$ まで、$x$ 軸方向か $y$ 軸方向に 1 ずつ進む最短の道順のうち、途中で直線 $y = x$ より上（$y > x$ の部分）に出ないものは何通りあるか。", cat,
        "カタラン数。全体 ${}_{12}\\mathrm{C}_6$ から、$y = x + 1$ に触れる道（折り返すと $(5, 7)$ への道 ${}_{12}\\mathrm{C}_5$ 通り）を引く。$924 - 792 = 132$。")
    E = {}
    for s_ in range(5, -1, -1):
        E[s_] = 1 + sum(F(1, 6) * (E[s_ + k] if s_ + k < 6 else 0) for k in range(1, 7))
    frac("h_prob", "和が 6 以上になるまで", "さいころを投げ、出た目の合計が 6 以上になったらやめる。投げる回数の期待値を", E[0],
         "合計が $s$ のときの、あと何回投げるかの期待値を $E_s$ とすると、$E_s = 1 + \\dfrac{1}{6}\\sum E_{s+k}$（$s + k \\ge 6$ なら 0）。$s = 5$ から順に求めると $E_0 = \\dfrac{16807}{7776}$。")
    w = sum(1 for p in itertools.permutations([1, 2, 3, 4, 5, 6, 7, 8, 9], 3) if (100 * p[0] + 10 * p[1] + p[2]) % 3 == 0)
    frac("h_prob", "3 けたの数が 3 の倍数", "1 から 9 の数字が書かれた 9 枚のカードから 3 枚を取り出して並べ、3 けたの数をつくる。それが 3 の倍数になる確率を", F(w, 9 * 8 * 7),
         "3 で割った余りが 0、1、2 のカードは 3 枚ずつ。和が 3 の倍数になるのは、余りが全部同じ（$3 \\times {}_3\\mathrm{C}_3$）か、全部ちがう（$3^3$）選び方で、30 通り。全体 ${}_9\\mathrm{C}_3 = 84$ で $\\dfrac{30}{84} = \\dfrac{5}{14}$。")

    # ───────── 微分・積分 ─────────
    v = sp.integrate(sp.sin(x) ** 4, (x, 0, sp.pi / 2)) / sp.pi
    frac("h_integ3", "sin の 4 乗の積分", "$\\displaystyle\\int_0^{\\pi/2} \\sin^4 x\\,dx = a\\pi$ とする。$a$ を", F(str(v)),
         "$\\sin^4 x = \\dfrac{3 - 4\\cos 2x + \\cos 4x}{8}$。積分すると $\\dfrac{3}{8} \\cdot \\dfrac{\\pi}{2} = \\dfrac{3\\pi}{16}$。")
    v = sp.integrate(x ** 2 * sp.sqrt(1 - x ** 2), (x, 0, 1)) / sp.pi
    frac("h_integ3", "置換積分", "$\\displaystyle\\int_0^{1} x^2\\sqrt{1 - x^2}\\,dx = a\\pi$ とする。$a$ を", F(str(sp.nsimplify(v))),
         "$x = \\sin\\theta$ とおくと $\\displaystyle\\int_0^{\\pi/2} \\sin^2\\theta\\cos^2\\theta\\,d\\theta = \\dfrac{1}{4}\\int_0^{\\pi/2}\\sin^2 2\\theta\\,d\\theta = \\dfrac{\\pi}{16}$。")
    assert abs(sum(1000 / (1000 ** 2 + k * k) for k in range(1, 1001)) - math.pi / 4) < 1e-3
    choice("h_limit", "区分求積法", "$\\displaystyle\\lim_{n \\to \\infty} \\sum_{k=1}^{n} \\dfrac{n}{n^2 + k^2}$ の値はどれか。", "$\\dfrac{\\pi}{4}$",
           ["$\\dfrac{\\pi}{2}$", "$\\log 2$", "$1$"], "$\\dfrac{1}{n}\\sum \\dfrac{1}{1 + (k/n)^2} \\to \\displaystyle\\int_0^1 \\dfrac{dx}{1 + x^2} = \\dfrac{\\pi}{4}$。")
    v = sp.integrate(sp.exp(x) - sp.E * x, (x, 0, 1))
    assert sp.simplify(v - (sp.E / 2 - 1)) == 0
    choice("h_integ_app", "曲線と接線と y 軸", "曲線 $y = e^x$ と、その上の点 $(1, e)$ における接線、および $y$ 軸で囲まれた部分の面積はどれか。", "$\\dfrac{e}{2} - 1$",
           ["$e - 2$", "$\\dfrac{e - 1}{2}$", "$e - 1$"], "接線は $y = ex$。$\\displaystyle\\int_0^1 (e^x - ex)\\,dx = (e - 1) - \\dfrac{e}{2} = \\dfrac{e}{2} - 1$。")
    v = sp.integrate(sp.Abs(sp.sin(x) - sp.cos(x)), (x, 0, sp.pi))
    v2 = sp.integrate(sp.cos(x) - sp.sin(x), (x, 0, sp.pi / 4)) + sp.integrate(sp.sin(x) - sp.cos(x), (x, sp.pi / 4, sp.pi))
    assert sp.simplify(v2 - 2 * sp.sqrt(2)) == 0
    choice("h_integ3", "絶対値の積分", "$\\displaystyle\\int_0^{\\pi} |\\sin x - \\cos x|\\,dx$ の値はどれか。", "$2\\sqrt{2}$",
           ["$2$", "$\\sqrt{2}$", "$2\\sqrt{2} - 1$"], "$x = \\dfrac{\\pi}{4}$ で符号が変わる。$\\left[\\sin x + \\cos x\\right]_0^{\\pi/4} + \\left[-\\cos x - \\sin x\\right]_{\\pi/4}^{\\pi} = (\\sqrt{2} - 1) + (1 + \\sqrt{2}) = 2\\sqrt{2}$。")
    v = sp.integrate(sp.log(x) ** 2, (x, 1, sp.E))
    assert sp.simplify(v - (sp.E - 2)) == 0
    choice("h_integ3", "log の 2 乗の積分", "$\\displaystyle\\int_1^{e} (\\log x)^2\\,dx$ の値はどれか。", "$e - 2$",
           ["$e - 1$", "$2e - 3$", "$1$"], "部分積分を 2 回。$\\left[x(\\log x)^2\\right]_1^e - 2\\displaystyle\\int_1^e \\log x\\,dx = e - 2 \\cdot 1 = e - 2$。")
    choice("h_diff3", "曲線と直線の距離", "曲線 $y = \\log x$ 上の点と、直線 $y = x$ の距離の最小値はどれか。", "$\\dfrac{\\sqrt{2}}{2}$",
           ["$1$", "$\\sqrt{2}$", "$\\dfrac{1}{2}$"], "接線の傾きが 1 になるのは $x = 1$、点 $(1, 0)$。直線 $x - y = 0$ との距離は $\\dfrac{|1 - 0|}{\\sqrt{2}} = \\dfrac{\\sqrt{2}}{2}$。")
    frac("h_quadfunc", "放物線と直線の距離", "放物線 $y = x^2$ 上の点と、直線 $y = 2x - 5$ の距離の最小値を $d$ とする。$d^2$ を", F(16, 5),
         "接線の傾きが 2 になる点は $(1, 1)$。直線 $2x - y - 5 = 0$ との距離は $\\dfrac{|2 - 1 - 5|}{\\sqrt{5}} = \\dfrac{4}{\\sqrt{5}}$。$d^2 = \\dfrac{16}{5}$。")
    assert sp.limit((sp.exp(x) - 1 - x) / x ** 2, x, 0) == sp.Rational(1, 2)
    frac("h_limit", "テイラー展開の考え方", "$\\displaystyle\\lim_{x \\to 0} \\dfrac{e^x - 1 - x}{x^2}$ を", F(1, 2),
         "ロピタルの定理を 2 回（または $e^x = 1 + x + \\dfrac{x^2}{2} + \\cdots$）で $\\dfrac{1}{2}$。")
    a_ = sp.Symbol("a", real=True)
    g = sp.Piecewise((sp.Rational(1, 2) - a_ + a_ ** 2, True))
    assert sp.integrate(sp.Abs(t - sp.Rational(1, 2)), (t, 0, 1)) == sp.Rational(1, 4)
    frac("h_integ", "絶対値を含む関数の最小値", "$f(a) = \\displaystyle\\int_0^1 |x - a|\\,dx$ の最小値を", F(1, 4),
         "$0 \\le a \\le 1$ のとき $f(a) = a^2 - a + \\dfrac{1}{2}$。$a = \\dfrac{1}{2}$ で最小値 $\\dfrac{1}{4}$。範囲の外では $f(a)$ はもっと大きい。")
    v = sp.integrate(2 * sp.pi * x * sp.sin(x), (x, 0, sp.pi))
    assert sp.simplify(v - 2 * sp.pi ** 2) == 0
    choice("h_integ3", "y 軸のまわりの回転体", "曲線 $y = \\sin x$（$0 \\le x \\le \\pi$）と $x$ 軸で囲まれた部分を、$y$ 軸のまわりに 1 回転させてできる立体の体積はどれか。", "$2\\pi^2$",
           ["$\\pi^2$", "$\\dfrac{\\pi^2}{2}$", "$4\\pi$"], "バウムクーヘン型：$\\displaystyle 2\\pi\\int_0^{\\pi} x\\sin x\\,dx = 2\\pi \\cdot \\pi = 2\\pi^2$。")
    choice("h_diff3", "解の個数と定数の範囲", "方程式 $e^x = kx$ が、異なる 2 つの実数解をもつような定数 $k$ の範囲はどれか。", "$k > e$",
           ["$k > 1$", "$0 < k < e$", "$k \\ge e$"], "$x \\neq 0$ で $k = \\dfrac{e^x}{x}$。右辺は $x > 0$ で $x = 1$ のとき最小値 $e$、$x < 0$ では負。$k > e$ で 2 つ。")
    choice("h_diff3", "最大となる点", "$x > 0$ のとき、関数 $y = x^{\\frac{1}{x}}$ が最大になる $x$ の値はどれか。", "$e$",
           ["$1$", "$2$", "$\\dfrac{1}{e}$"], "対数をとると $\\log y = \\dfrac{\\log x}{x}$。微分すると $\\dfrac{1 - \\log x}{x^2}$ で、$x = e$ で最大。")

    # ───────── 三角関数・図形・ベクトル・複素数 ─────────
    v = sp.nsimplify(sp.sin(sp.pi / 18) * sp.sin(5 * sp.pi / 18) * sp.sin(7 * sp.pi / 18))
    assert abs(float(v) - 1 / 8) < 1e-12
    frac("h_addition", "積の値", "$\\sin 10^\\circ \\sin 50^\\circ \\sin 70^\\circ$ を", F(1, 8),
         "$\\sin\\theta\\sin(60^\\circ - \\theta)\\sin(60^\\circ + \\theta) = \\dfrac{1}{4}\\sin 3\\theta$ を使う。$\\theta = 10^\\circ$ で $\\dfrac{1}{4}\\sin 30^\\circ = \\dfrac{1}{8}$。")
    assert abs(sum(math.cos(2 * k * math.pi / 7) for k in (1, 2, 3)) + 0.5) < 1e-12
    choice("h_complex", "cos の和", "$\\cos\\dfrac{2\\pi}{7} + \\cos\\dfrac{4\\pi}{7} + \\cos\\dfrac{6\\pi}{7}$ の値はどれか。", "$-\\dfrac{1}{2}$",
           ["$\\dfrac{1}{2}$", "$0$", "$-1$"], "$\\omega = \\cos\\dfrac{2\\pi}{7} + i\\sin\\dfrac{2\\pi}{7}$ とすると $1 + \\omega + \\cdots + \\omega^6 = 0$。実部をとると $1 + 2(\\text{求める和}) = 0$。")
    assert abs(math.tan(math.radians(20)) * math.tan(math.radians(40)) * math.tan(math.radians(80)) - math.sqrt(3)) < 1e-12
    choice("h_addition", "tan の積", "$\\tan 20^\\circ \\tan 40^\\circ \\tan 80^\\circ$ の値はどれか。", "$\\sqrt{3}$",
           ["$1$", "$\\dfrac{\\sqrt{3}}{3}$", "$\\dfrac{1}{8}$"], "$\\tan\\theta\\tan(60^\\circ - \\theta)\\tan(60^\\circ + \\theta) = \\tan 3\\theta$。$\\theta = 20^\\circ$ で $\\tan 60^\\circ = \\sqrt{3}$。")
    a, b, c = 8, 5, 7      # BC = a, CA = b, AB = c、角 B の二等分線
    bd2 = F(a * c) * (1 - F(b, a + c) ** 2)
    frac("h_geom", "角の二等分線の長さ", "三角形 ABC で AB = 7、BC = 8、CA = 5 とする。角 B の二等分線と辺 CA の交点を D とするとき、BD$^2$ を", bd2,
         "AD : DC = 7 : 8。スチュワートの定理（または余弦定理を 2 回）で、BD$^2 = $ AB・BC $- $ AD・DC $= 56 - \\dfrac{7}{3} \\cdot \\dfrac{8}{3} = \\dfrac{448}{9}$。")
    assert bd2 == F(56) - F(7, 3) * F(8, 3)
    frac("h_space", "正四面体の内接球", "1 辺の長さが 6 の正四面体に内接する球の半径を $r$ とする。$r^2$ を", F(3, 2),
         "高さは $6 \\cdot \\sqrt{\\dfrac{2}{3}} = 2\\sqrt{6}$。内接球の中心は高さを 3 : 1 に分けるので、$r = \\dfrac{2\\sqrt{6}}{4} = \\dfrac{\\sqrt{6}}{2}$。$r^2 = \\dfrac{3}{2}$。")
    frac("h_space", "平面までの距離", "空間に 3 点 A$(1, 0, 0)$、B$(0, 1, 0)$、C$(0, 0, 1)$ がある。原点 O から平面 ABC までの距離を $h$ とするとき、$h^2$ を", F(1, 3),
         "平面 ABC は $x + y + z = 1$。距離は $\\dfrac{1}{\\sqrt{3}}$ で、$h^2 = \\dfrac{1}{3}$。")
    X, Y = sp.symbols("X Y", real=True)
    th = sp.Symbol("th", real=True)
    mx = sp.maximum(sp.cos(th) ** 2 + 4 * sp.cos(th) * sp.sin(th) + sp.sin(th) ** 2, th, sp.Interval(0, 2 * sp.pi))
    assert mx == 3
    num("h_trig2", "円の上での最大値", "実数 $x$、$y$ が $x^2 + y^2 = 1$ を満たすとき、$x^2 + 4xy + y^2$ の最大値を答えよ。", 3,
        "$x = \\cos\\theta$、$y = \\sin\\theta$ とおくと $1 + 2\\sin 2\\theta$。最大値は 3。")
    num("h_quadeq", "対称式と実数条件", "実数 $x$、$y$ が $x^2 + xy + y^2 = 3$ を満たすとき、$x + y$ の最大値を答えよ。", 2,
        "$x + y = s$、$xy = p$ とおくと $s^2 - p = 3$。$x$、$y$ が実数なので $s^2 - 4p \\ge 0$、$s^2 - 4(s^2 - 3) \\ge 0$、$s^2 \\le 4$。最大値は 2。")
    num("h_abs", "コーシー・シュワルツの不等式", "正の数 $a$、$b$、$c$ が $a + b + c = 1$ を満たすとき、$\\dfrac{1}{a} + \\dfrac{4}{b} + \\dfrac{9}{c}$ の最小値を答えよ。", 36,
        "$(a + b + c)\\left(\\dfrac{1}{a} + \\dfrac{4}{b} + \\dfrac{9}{c}\\right) \\ge (1 + 2 + 3)^2 = 36$。等号は $a : b : c = 1 : 2 : 3$。")
    mx = max(abs(complex(math.cos(u), math.sin(u)) ** 2 + complex(math.cos(u), math.sin(u)) + 1) for u in [k * 2 * math.pi / 100000 for k in range(100000)])
    assert abs(mx - 3) < 1e-6
    num("h_complex", "複素数の絶対値の最大", "$|z| = 1$ を満たす複素数 $z$ について、$|z^2 + z + 1|$ の最大値を答えよ。", 3,
        "$|z^2 + z + 1| = |z|\\,|z + 1 + \\overline{z}| = |1 + 2\\cos\\theta|$（$z = \\cos\\theta + i\\sin\\theta$）。最大値は 3。")
    v = sp.prod([2 - sp.exp(2 * sp.pi * sp.I * k / 5) for k in range(1, 5)])
    assert sp.simplify(sp.expand_complex(v)) == 31
    num("h_complex", "1 の 5 乗根と積", "$z^5 = 1$ の解のうち、1 以外の 4 つを $\\alpha$、$\\beta$、$\\gamma$、$\\delta$ とする。$(2 - \\alpha)(2 - \\beta)(2 - \\gamma)(2 - \\delta)$ の値を答えよ。", 31,
        "$z^4 + z^3 + z^2 + z + 1 = (z - \\alpha)(z - \\beta)(z - \\gamma)(z - \\delta)$。$z = 2$ を代入して $16 + 8 + 4 + 2 + 1 = 31$。")
    num("h_complex", "円の上の点と原点", "複素数 $z$ が $|z - 3 - 4i| = 1$ を満たすとき、$|z|$ の最大値を答えよ。", 6,
        "$z$ は中心 $3 + 4i$、半径 1 の円の上。中心と原点の距離は 5 なので、最大値は $5 + 1 = 6$。")

    # ───────── 数列・式 ─────────
    a = F(1)
    for _ in range(99): a = a / (1 + a)
    frac("h_seq2", "逆数をとる漸化式", "$a_1 = 1$、$a_{n+1} = \\dfrac{a_n}{1 + a_n}$ で定まる数列の $a_{100}$ を", a,
         "逆数をとると $\\dfrac{1}{a_{n+1}} = \\dfrac{1}{a_n} + 1$。$\\dfrac{1}{a_n} = n$ なので $a_{100} = \\dfrac{1}{100}$。")
    v = sum(1 / (math.sqrt(k) + math.sqrt(k + 1)) for k in range(1, 50))
    assert abs(v - (math.sqrt(50) - 1)) < 1e-9
    choice("h_seq", "有理化して打ち消す和", "$\\displaystyle\\sum_{k=1}^{49} \\dfrac{1}{\\sqrt{k} + \\sqrt{k + 1}}$ の値はどれか。", "$5\\sqrt{2} - 1$",
           ["$7$", "$5\\sqrt{2}$", "$5\\sqrt{2} + 1$"], "有理化すると $\\sqrt{k + 1} - \\sqrt{k}$。打ち消し合って $\\sqrt{50} - 1 = 5\\sqrt{2} - 1$。")
    a = 1
    for m in range(1, 10): a = 2 * a + 2 ** m
    assert a == 10 * 2 ** 9
    num("h_seq2", "2 のべきを含む漸化式", "$a_1 = 1$、$a_{n+1} = 2a_n + 2^n$ で定まる数列の $a_{10}$ を答えよ。", a,
        "両辺を $2^{n+1}$ で割ると $\\dfrac{a_{n+1}}{2^{n+1}} = \\dfrac{a_n}{2^n} + \\dfrac{1}{2}$。$\\dfrac{a_n}{2^n} = \\dfrac{n}{2}$ より $a_n = n \\cdot 2^{n-1}$。$a_{10} = 5120$。")
    seq = [k for k in range(1, 30) for _ in range(k)]
    num("h_seq", "群数列の項", "数列 1, 2, 2, 3, 3, 3, 4, 4, 4, 4, …（$k$ が $k$ 個並ぶ）の第 100 項を答えよ。", seq[99],
        "$k$ までで $\\dfrac{k(k + 1)}{2}$ 項。$k = 13$ で 91 項、$k = 14$ で 105 項なので、第 100 項は 14。")
    num("h_seq", "群数列の和", "数列 1, 2, 2, 3, 3, 3, 4, 4, 4, 4, …（$k$ が $k$ 個並ぶ）の、第 1 項から第 100 項までの和を答えよ。", sum(seq[:100]),
        "13 までの和は $\\sum k^2 = 819$。残りの 9 項は 14 で 126。合計 945。")
    v = 1
    for m in range(2, 64): v *= sp.log(m + 1) / sp.log(m)
    assert sp.simplify(v) == 6
    num("h_exp", "対数の積", "$\\log_2 3 \\cdot \\log_3 4 \\cdot \\log_4 5 \\cdots \\log_{63} 64$ の値を答えよ。", 6,
        "底の変換で $\\dfrac{\\log 3}{\\log 2} \\cdot \\dfrac{\\log 4}{\\log 3} \\cdots \\dfrac{\\log 64}{\\log 63} = \\dfrac{\\log 64}{\\log 2} = 6$。")
    assert str(3 ** 100)[0] == "5" and int(100 * 0.4771) == 47
    num("h_exp", "最高位の数字", "$3^{100}$ の最高位の数字を答えよ（$\\log_{10} 2 = 0.3010$、$\\log_{10} 3 = 0.4771$ とする）。", 5,
        "$\\log_{10} 3^{100} = 47.71$。$\\log_{10} 5 = 0.6990 < 0.71 < \\log_{10} 6 = 0.7781$ なので、最高位は 5。")
    r = sp.solve((x - 1) ** 4 - 16, x)
    assert sum(v for v in r if v.is_real) == 2
    num("h_cplx", "4 次方程式の実数解", "方程式 $x^4 - 4x^3 + 6x^2 - 4x - 15 = 0$ の実数解の和を答えよ。", 2,
        "左辺は $(x - 1)^4 - 16$。$(x - 1)^2 = 4$ より実数解は $x = 3, -1$（$(x - 1)^2 = -4$ は虚数解）。和は 2。")
    xx = (3 + sp.sqrt(5)) / 2
    assert sp.simplify(xx ** 5 + xx ** -5) == 123
    num("h_cplx", "x + 1/x から求める", "$x + \\dfrac{1}{x} = 3$ のとき、$x^5 + \\dfrac{1}{x^5}$ の値を答えよ。", 123,
        "$x^2 + \\dfrac{1}{x^2} = 7$、$x^3 + \\dfrac{1}{x^3} = 18$。$\\left(x^2 + \\dfrac{1}{x^2}\\right)\\left(x^3 + \\dfrac{1}{x^3}\\right) = x^5 + \\dfrac{1}{x^5} + x + \\dfrac{1}{x}$ より $126 - 3 = 123$。")
    rs = sp.Poly(x ** 3 - 3 * x - 1, x).nroots()
    p5 = round(sum(r ** 5 for r in rs).real) if hasattr(sum(r ** 5 for r in rs), "real") else round(float(sum(r ** 5 for r in rs)))
    assert p5 == 15
    num("h_cplx", "解の 5 乗の和", "$x^3 - 3x - 1 = 0$ の 3 つの解を $\\alpha$、$\\beta$、$\\gamma$ とする。$\\alpha^5 + \\beta^5 + \\gamma^5$ の値を答えよ。", 15,
        "$s_k = \\alpha^k + \\beta^k + \\gamma^k$ とすると $s_{k+3} = 3s_{k+1} + s_k$。$s_0 = 3$、$s_1 = 0$、$s_2 = 6$ から $s_3 = 3$、$s_4 = 18$、$s_5 = 15$。")
    ok = []
    for a in range(-50, 51):
        f = lambda z: z * z - 2 * a * z + a + 2
        if a * a - a - 2 > 0 and 1 < a < 4 and f(1) > 0 and f(4) > 0: ok.append(a)
    # 整数の a は 3 だけ（a=3 で x^2 - 6x + 5：解 1, 5 は範囲外 → f(1)=0 なので除かれる）
    oka = [a for a in range(-50, 51) for _ in [0] if a * a - a - 2 > 0 and 1 < a < 4 and (1 - 2 * a + a + 2) > 0 and (16 - 8 * a + a + 2) > 0]
    c = len(oka)
    lo, hi = 2, F(18, 7)
    frac("h_quadeq", "解の配置（範囲）", "二次方程式 $x^2 - 2ax + a + 2 = 0$ が、$1 < x < 4$ の範囲に異なる 2 つの実数解をもつような $a$ の範囲は $2 < a < c$ となる。$c$ を", hi,
         "$f(x) = x^2 - 2ax + a + 2$ として、判別式 $a^2 - a - 2 > 0$、軸 $1 < a < 4$、$f(1) = 3 - a > 0$、$f(4) = 18 - 7a > 0$。まとめて $2 < a < \\dfrac{18}{7}$。")
    # 数値で確かめる
    for aa in [2.05, 2.3, 2.55]:
        r = [z for z in sp.Poly(x ** 2 - 2 * aa * x + aa + 2, x).nroots() if abs(sp.im(z)) < 1e-12]
        assert len(r) == 2 and all(1 < float(z) < 4 for z in r)
    for aa in [1.95, 2.6]:
        r = [z for z in sp.Poly(x ** 2 - 2 * aa * x + aa + 2, x).nroots() if abs(sp.im(z)) < 1e-12]
        assert not (len(r) == 2 and all(1 < float(sp.re(z)) < 4 for z in r))

    # ───────── ジャンルを広げる（2026年11月 追加）─────────
    # 確率の漸化式
    p = F(1)
    for _ in range(10): p = p * F(1, 3) + (1 - p) * F(2, 3)      # 正三角形の頂点を移動（その場にとどまらない）… 下で別に確かめる
    # 正四面体の頂点 A から、毎回ほかの 3 頂点へ等確率で移動。n 回後に A にいる確率 p_n = 1/4 + (3/4)(-1/3)^n
    pn = F(1, 4) + F(3, 4) * F(-1, 3) ** 6
    q = F(1)
    for _ in range(6): q = (1 - q) * F(1, 3)
    assert q == pn
    frac("h_seq2", "確率の漸化式", "正四面体 ABCD の頂点 A に点 P がある。P は 1 秒ごとに、いまいる頂点以外の 3 つの頂点のどれかへ、等しい確率で移る。6 秒後に P が A にいる確率を", pn,
         "$n$ 秒後に A にいる確率を $p_n$ とすると $p_{n+1} = \\dfrac{1}{3}(1 - p_n)$。$p_n - \\dfrac{1}{4} = -\\dfrac{1}{3}\\left(p_{n-1} - \\dfrac{1}{4}\\right)$ より $p_n = \\dfrac{1}{4} + \\dfrac{3}{4}\\left(-\\dfrac{1}{3}\\right)^n$。")
    # データ：平均と分散の合成
    xs = [3, 5, 7, 9, 11]; ys = [x + 10 for x in xs]
    allv = xs + ys
    m = F(sum(allv), len(allv)); v = sum((F(a) - m) ** 2 for a in allv) / len(allv)
    num("h_stat", "2 つのデータの合併", "あるデータ A（5 個）の平均は 7、分散は 8 である。A のすべての値に 10 を足したデータ B（5 個）をつくる。A と B を合わせた 10 個のデータの分散を答えよ。", int(v),
        "B の平均は 17、分散は 8。合わせると平均は 12。分散は（2 乗の平均）−（平均の 2 乗）で、$\\dfrac{(8 + 49) + (8 + 289)}{2} - 144 = 33$。")
    assert v == 33
    # 空間図形：正八面体の体積
    num("h_space", "正八面体の体積", "1 辺の長さが $3\\sqrt{2}$ の正八面体の体積を答えよ。", 36,
        "正八面体は、底面が 1 辺 $3\\sqrt{2}$ の正方形の正四角錐 2 つ。高さは対角線の半分で 3。$2 \\times \\dfrac{1}{3} \\times 18 \\times 3 = 36$。")
    # 複素数平面：正三角形の頂点
    z = sp.Rational(1) + sp.I
    w = (z) * (sp.Rational(1, 2) + sp.sqrt(3) / 2 * sp.I)
    assert abs(complex(w) - complex((1 - math.sqrt(3)) / 2, (1 + math.sqrt(3)) / 2)) < 1e-12
    choice("h_complex", "回転と正三角形", "複素数平面で、0、$1 + i$、$w$ が正三角形の頂点で、$w$ は $1 + i$ を原点のまわりに $+\\dfrac{\\pi}{3}$ 回転した点とする。$w$ の実部はどれか。",
           "$\\dfrac{1 - \\sqrt{3}}{2}$", ["$\\dfrac{1 + \\sqrt{3}}{2}$", "$\\dfrac{\\sqrt{3} - 1}{2}$", "$1 - \\sqrt{3}$"],
           "$w = (1 + i)\\left(\\dfrac{1}{2} + \\dfrac{\\sqrt{3}}{2}i\\right) = \\dfrac{1 - \\sqrt{3}}{2} + \\dfrac{1 + \\sqrt{3}}{2}i$。")
    # 軌跡
    frac("h_circle", "中点の軌跡", "点 P が円 $x^2 + y^2 = 9$ の上を動くとき、点 A$(6, 0)$ と P を結ぶ線分の中点 M の軌跡は円になる。その半径を", F(3, 2),
         "M$(X, Y)$ とすると P$(2X - 6, 2Y)$。$(2X - 6)^2 + (2Y)^2 = 9$ より $(X - 3)^2 + Y^2 = \\dfrac{9}{4}$。半径 $\\dfrac{3}{2}$。")
    # 図形：三角形の内部の点と最小
    num("h_vec", "距離の 2 乗の和の最小", "平面上の 3 点 A$(0, 0)$、B$(6, 0)$、C$(0, 9)$ がある。点 P を動かすとき、PA$^2$ + PB$^2$ + PC$^2$ の最小値を答えよ。", 78,
        "最小になるのは P が重心 G$(2, 3)$ のとき。$13 + 25 + 40 = 78$。")
    assert min((x - 0) ** 2 + y ** 2 + (x - 6) ** 2 + y ** 2 + x ** 2 + (y - 9) ** 2 for x in [F(i, 2) for i in range(-10, 30)] for y in [F(j, 2) for j in range(-10, 30)]) == 78
    # 整数：桁と余り
    c = sum(1 for k in range(1, 1001) if pow(2, k, 7) == 1)
    num("h_nt", "累乗の余りの周期", "1 以上 1000 以下の整数 $k$ のうち、$2^k$ を 7 で割った余りが 1 になるものは何個あるか。", c,
        "$2^3 = 8 \\equiv 1 \\pmod 7$ なので、余りは周期 3 でくり返し、$k$ が 3 の倍数のときだけ 1。1000 以下の 3 の倍数は 333 個。")
    # 場合の数：円順列と制約
    c = 0
    for perm in itertools.permutations(range(1, 6)):
        seq = (0,) + perm          # 0,1,2 が男子… 男女交互は別
    people = list(range(6))       # 0〜2 男子、3〜5 女子
    cnt = 0
    for perm in itertools.permutations(people[1:]):
        s_ = (0,) + perm
        if all((s_[i] < 3) != (s_[(i + 1) % 6] < 3) for i in range(6)): cnt += 1
    num("h_count", "男女交互の円順列", "男子 3 人、女子 3 人が円形のテーブルにすわる。男女が交互になるすわり方は何通りか。", cnt,
        "男子 3 人の円順列 $(3 - 1)! = 2$ 通り。その間の 3 か所に女子が並ぶ $3! = 6$ 通り。$2 \\times 6 = 12$ 通り。")
    # 不等式：絶対値の和の最小
    v = min(sum(abs(x - k) for k in range(1, 11)) for x in range(-20, 31))
    num("h_abs", "絶対値の和の最小値", "$f(x) = |x - 1| + |x - 2| + \\cdots + |x - 10|$ の最小値を答えよ。", v,
        "中央値（$5 \\le x \\le 6$）で最小。$x = 5$ のとき $4 + 3 + 2 + 1 + 0 + 1 + 2 + 3 + 4 + 5 = 25$。")
    # 数列：周期
    a = [1, 3]
    for _ in range(2023): a.append(a[-1] - a[-2])
    num("h_seq2", "周期をもつ数列", "$a_1 = 1$、$a_2 = 3$、$a_{n+2} = a_{n+1} - a_n$ で定まる数列の $a_{2025}$ を答えよ。", a[2024],
        "順に $1, 3, 2, -1, -3, -2, 1, 3, \\dots$ と、周期 6 でくり返す。$2025 = 6 \\times 337 + 3$ なので $a_{2025} = a_3 = 2$。")
    return list(OUT)


if __name__ == "__main__":
    ps = generate()
    print(len(ps))
    for p in ps: print(p["unit"], p["title"], p["answer"])
