"""問題データ (problems.json) を生成し、すべての正解を sympy で検算するスクリプト。

使い方:  python3 tools/build_problems.py
出力先:  mathscreen/Resources/problems.json と preview/problems.js
"""
import json, itertools, math, os
from fractions import Fraction
import sympy as sp

x, y, k, n, t, th = sp.symbols("x y k n t theta", real=True)
P = []

def add(pid, cat, diff, title, body, answer, check, explanation):
    val = check() if callable(check) else check
    val = sp.nsimplify(val)
    assert val == answer, f"{pid}: 検算結果 {val} != 正解 {answer}"
    assert isinstance(answer, int)
    P.append(dict(id=pid, category=cat, difficulty=diff, title=title,
                  body=body, answer=answer, explanation=explanation))

def frac_sum(fr):  # 既約分数 a/b -> a+b
    fr = sp.Rational(fr); return int(fr.p + fr.q)

def dice_prob(n_dice, pred):
    outs = list(itertools.product(range(1, 7), repeat=n_dice))
    return sp.Rational(sum(1 for o in outs if pred(o)), len(outs))

# ───────── 中学数学 ─────────
C = "junior"
add("j01", C, 1, "一次方程式", "方程式 2x + 7 = 3x − 5 を解け。x の値を答えよ。", 12,
    lambda: sp.solve(2*x+7-(3*x-5), x)[0], "x を右辺、数を左辺に集めると 7 + 5 = 3x − 2x より x = 12。")
add("j02", C, 1, "正負の数", "(−3)² − 4 × (−2) を計算せよ。", 17,
    (-3)**2 - 4*(-2), "(−3)² = 9、−4 × (−2) = +8 なので 9 + 8 = 17。")
add("j03", C, 1, "連立方程式", "x + y = 10、x − y = 4 のとき、xy の値を答えよ。", 21,
    lambda: (lambda s: s[x]*s[y])(sp.solve([x+y-10, x-y-4], [x, y])),
    "2式を足して 2x = 14 より x = 7、y = 3。よって xy = 21。")
add("j04", C, 1, "多角形の角", "正八角形の1つの内角は何度か。", 135,
    sp.Rational(180*(8-2), 8), "内角の和は 180° × (8 − 2) = 1080°。1つ分は 1080° ÷ 8 = 135°。")
add("j05", C, 1, "平方根", "√48 ÷ √3 を計算せよ。", 4,
    sp.sqrt(48)/sp.sqrt(3), "√48 ÷ √3 = √(48 ÷ 3) = √16 = 4。")
add("j06", C, 2, "二次方程式", "二次方程式 x² − 5x − 14 = 0 の正の解を答えよ。", 7,
    lambda: max(sp.solve(x**2-5*x-14, x)), "(x − 7)(x + 2) = 0 より x = 7, −2。正の解は 7。")
add("j07", C, 2, "三平方の定理", "直角三角形の斜辺が 13、他の1辺が 5 のとき、残りの辺の長さを答えよ。", 12,
    sp.sqrt(13**2-5**2), "13² − 5² = 169 − 25 = 144 = 12²。")
add("j08", C, 2, "確率", "大小2つのさいころを投げるとき、出た目の和が 5 になる確率を既約分数 a/b で表す。a + b を答えよ。", 10,
    lambda: frac_sum(dice_prob(2, lambda o: sum(o) == 5)),
    "和が5になるのは (1,4)(2,3)(3,2)(4,1) の4通り。4/36 = 1/9 より a + b = 10。")
add("j09", C, 2, "関数 y = ax²", "関数 y = ax² のグラフが点 (2, 12) を通る。x = −3 のときの y の値を答えよ。", 27,
    lambda: (sp.Rational(12, 4))*9, "12 = 4a より a = 3。y = 3 × (−3)² = 27。")
add("j10", C, 2, "整数の文章題", "連続する3つの整数の和が 87 のとき、最も大きい数を答えよ。", 30,
    lambda: sp.solve((n-1)+n+(n+1)-87, n)[0] + 1, "真ん中を n とすると 3n = 87 より n = 29。最大は 30。")
add("j11", C, 3, "式の値", "x + y = 5、xy = 3 のとき、x² + y² の値を答えよ。", 19,
    5**2 - 2*3, "x² + y² = (x + y)² − 2xy = 25 − 6 = 19。")
add("j12", C, 3, "正六角形の面積", "半径 6 の円に内接する正六角形の面積を a√b（b はできるだけ小さい自然数）で表す。a + b を答えよ。", 57,
    lambda: (lambda S: (S/sp.sqrt(3)) + 3)(6*sp.sqrt(3)/4*36),
    "正六角形は1辺6の正三角形6個。面積は 6 × (√3/4) × 36 = 54√3。a + b = 54 + 3 = 57。")
add("j13", C, 3, "根号を含む式の値", "x = √5 + 2 のとき、x² − 4x + 7 の値を答えよ。", 8,
    lambda: sp.expand((sp.sqrt(5)+2)**2 - 4*(sp.sqrt(5)+2) + 7),
    "x² − 4x + 7 = (x − 2)² + 3。x − 2 = √5 なので 5 + 3 = 8。")
add("j14", C, 3, "倍数の個数", "1 から 100 までの整数のうち、3 でも 4 でも割り切れない数はいくつあるか。", 50,
    sum(1 for i in range(1, 101) if i % 3 and i % 4),
    "3の倍数33個、4の倍数25個、12の倍数8個。どちらかで割り切れるのは 33 + 25 − 8 = 50 個。100 − 50 = 50。")
def j15():
    pts = [sp.Point(sp.cos(sp.pi/2 + 2*sp.pi*i/5), sp.sin(sp.pi/2 + 2*sp.pi*i/5)) for i in range(5)]
    A, B, Cc, D, E = pts
    Pp = sp.Line(A, Cc).intersection(sp.Line(B, D))[0]
    ang = sp.acos(sp.Matrix(A-Pp).dot(sp.Matrix(B-Pp)) / (Pp.distance(A)*Pp.distance(B)))
    return sp.nsimplify(sp.N(ang*180/sp.pi, 30))
add("j15", C, 3, "正五角形と角", "正五角形 ABCDE で、対角線 AC と BD の交点を P とする。∠APB は何度か。", 72,
    j15, "∠BAC = 36°、∠ABD = 108° − 36° = 72°。三角形 ABP で ∠APB = 180° − 36° − 72° = 72°。")

# ───────── 数学I・A ─────────
C = "math1a"
add("a01", C, 1, "二次関数の最小値", "二次関数 y = x² − 6x + 11 の最小値を答えよ。", 2,
    lambda: sp.minimum(x**2-6*x+11, x), "y = (x − 3)² + 2 と平方完成でき、最小値は 2。")
add("a02", C, 1, "順列", "異なる5人を1列に並べる方法は何通りか。", 120,
    math.factorial(5), "5! = 5 × 4 × 3 × 2 × 1 = 120 通り。")
add("a03", C, 1, "三角比", "0° < θ < 90° で sin θ = 3/5 のとき、tan θ を既約分数 a/b で表す。a + b を答えよ。", 7,
    lambda: frac_sum(sp.Rational(3, 5)/sp.sqrt(1-sp.Rational(9, 25))),
    "cos θ = √(1 − 9/25) = 4/5。tan θ = (3/5) ÷ (4/5) = 3/4 より a + b = 7。")
add("a04", C, 1, "絶対値と不等式", "|x − 3| < 5 を満たす整数 x はいくつあるか。", 9,
    sum(1 for i in range(-50, 50) if abs(i-3) < 5), "−5 < x − 3 < 5 より −2 < x < 8。整数は −1 から 7 の 9 個。")
add("a05", C, 1, "組合せ", "₇C₃ の値を答えよ。", 35,
    math.comb(7, 3), "₇C₃ = (7 × 6 × 5) ÷ (3 × 2 × 1) = 35。")
add("a06", C, 2, "余弦定理", "三角形 ABC で AB = 5、AC = 8、∠A = 60° のとき、BC の長さを答えよ。", 7,
    lambda: sp.sqrt(5**2+8**2-2*5*8*sp.cos(sp.pi/3)), "BC² = 25 + 64 − 2·5·8·cos60° = 89 − 40 = 49 より BC = 7。")
add("a07", C, 2, "重解条件", "x の二次方程式 x² + 2kx + k + 6 = 0 が重解をもつような正の定数 k の値を答えよ。", 3,
    lambda: max(sp.solve(k**2-(k+6), k)), "判別式 D/4 = k² − (k + 6) = 0 より (k − 3)(k + 2) = 0。正なので k = 3。")
add("a08", C, 2, "確率（組合せ）", "赤玉4個、白玉3個が入った袋から同時に3個取り出す。赤玉2個・白玉1個となる確率を既約分数 a/b で表す。a + b を答えよ。", 53,
    lambda: frac_sum(sp.Rational(math.comb(4, 2)*3, math.comb(7, 3))),
    "₄C₂ × ₃C₁ = 18 通り、全体は ₇C₃ = 35 通り。18/35 より a + b = 53。")
add("a09", C, 2, "約数の個数", "360 の正の約数はいくつあるか。", 24,
    sp.divisor_count(360), "360 = 2³ × 3² × 5 なので (3 + 1)(2 + 1)(1 + 1) = 24 個。")
add("a10", C, 2, "不定方程式", "7x + 5y = 1 を満たす整数 x, y のうち、x が正で最小となるものについて x − y の値を答えよ。", 7,
    lambda: next(xx - (1-7*xx)//5 for xx in range(1, 100) if (1-7*xx) % 5 == 0),
    "7x ≡ 1 (mod 5) より 2x ≡ 1、x ≡ 3。x = 3 のとき y = −4。x − y = 7。")
add("a11", C, 3, "三角形の面積", "三角形 ABC で BC = 7、CA = 5、AB = 3 のとき、面積を a√b / c（a と c は互いに素、b は平方因子をもたない）で表す。a + b + c を答えよ。", 22,
    lambda: (lambda S: 15 + 3 + 4 if sp.simplify(S - 15*sp.sqrt(3)/4) == 0 else -1)(
        sp.Rational(1, 2)*5*3*sp.sin(sp.acos(sp.Rational(5**2+3**2-7**2, 2*5*3)))),
    "cos A = (25 + 9 − 49)/(2·5·3) = −1/2 より A = 120°。面積 = ½·5·3·sin120° = 15√3/4。a + b + c = 15 + 3 + 4 = 22。")
def a12():
    a = sp.symbols("a", positive=True)
    sols = []
    for cand in sp.solve(3 - a**2 + 1, a):      # 0 < a <= 2 のとき最小値 f(a) = 3 − a²
        if 0 < cand <= 2: sols.append(cand)
    for cand in sp.solve(7 - 4*a + 1, a):       # a > 2 のとき最小値 f(2) = 7 − 4a
        if cand > 2: sols.append(cand)
    assert len(sols) == 1; return sols[0]
add("a12", C, 3, "定義域つき最小値", "f(x) = x² − 2ax + 3（0 ≦ x ≦ 2）の最小値が −1 となるような正の定数 a の値を答えよ。", 2,
    a12, "軸 x = a。0 < a ≦ 2 なら最小値 3 − a² = −1 より a = 2（適する）。a > 2 なら f(2) = 7 − 4a = −1 より a = 2 で不適。よって a = 2。")
add("a13", C, 3, "組分け", "区別のつく6人を、2人ずつの3組に分ける方法は何通りか（組には区別がない）。", 15,
    math.comb(6, 2)*math.comb(4, 2)//math.factorial(3), "₆C₂ × ₄C₂ × ₂C₂ ÷ 3! = 15 × 6 × 1 ÷ 6 = 15 通り。")
add("a14", C, 3, "最大値の確率", "さいころを3回投げるとき、出た目の最大値が 5 である確率を既約分数 a/b で表す。a + b を答えよ。", 277,
    lambda: frac_sum(dice_prob(3, lambda o: max(o) == 5)),
    "最大値 ≦ 5 の確率 (5/6)³ から 最大値 ≦ 4 の確率 (4/6)³ を引いて (125 − 64)/216 = 61/216。a + b = 277。")
add("a15", C, 3, "整数の割り切れ", "n² + 2n + 12 が n + 3 で割り切れるような正の整数 n のうち、最大のものを答えよ。", 12,
    max(i for i in range(1, 1000) if (i*i+2*i+12) % (i+3) == 0),
    "n² + 2n + 12 = (n + 3)(n − 1) + 15。n + 3 が 15 の約数であればよく、最大は n + 3 = 15 の n = 12。")

# ───────── 数学II・B ─────────
C = "math2b"
add("b01", C, 1, "対数", "log₂32 + log₃27 の値を答えよ。", 8,
    lambda: sp.log(32, 2) + sp.log(27, 3), "log₂32 = 5、log₃27 = 3 なので 8。")
add("b02", C, 1, "等差数列", "初項 3、公差 4 の等差数列の第 20 項を答えよ。", 79,
    3 + 19*4, "aₙ = 3 + (n − 1) × 4。a₂₀ = 3 + 76 = 79。")
add("b03", C, 1, "二項定理", "(x + 2)⁵ を展開したときの x³ の係数を答えよ。", 40,
    lambda: sp.Poly(sp.expand((x+2)**5), x).coeff_monomial(x**3), "₅C₃ × 2² = 10 × 4 = 40。")
add("b04", C, 1, "円の方程式", "円 x² + y² − 4x + 6y − 12 = 0 の半径を答えよ。", 5,
    sp.sqrt(4+9+12), "(x − 2)² + (y + 3)² = 25 と変形でき、半径は 5。")
add("b05", C, 1, "微分係数", "f(x) = x³ − 3x の x = 2 における微分係数 f′(2) を答えよ。", 9,
    lambda: sp.diff(x**3-3*x, x).subs(x, 2), "f′(x) = 3x² − 3 より f′(2) = 12 − 3 = 9。")
add("b06", C, 2, "指数方程式", "方程式 2ˣ = 8ˣ⁻² を解け。x の値を答えよ。", 3,
    lambda: sp.solve(x - 3*(x-2), x)[0], "8ˣ⁻² = 2³⁽ˣ⁻²⁾ より x = 3x − 6、x = 3。")
add("b07", C, 2, "定積分", "定積分 ∫₀³ (x² + 2x) dx の値を答えよ。", 18,
    lambda: sp.integrate(x**2+2*x, (x, 0, 3)), "[x³/3 + x²]₀³ = 9 + 9 = 18。")
add("b08", C, 2, "極大値", "f(x) = x³ − 6x² + 9x + 1 の極大値を答えよ。", 5,
    lambda: (x**3-6*x**2+9*x+1).subs(x, 1), "f′(x) = 3(x − 1)(x − 3)。x = 1 で極大となり f(1) = 5。")
add("b09", C, 2, "Σの計算", "1² + 2² + 3² + … + 10² の値を答えよ。", 385,
    sum(i*i for i in range(1, 11)), "Σk² = n(n + 1)(2n + 1)/6 = 10·11·21/6 = 385。")
add("b10", C, 2, "三角方程式の解の個数", "0 ≦ θ < 2π のとき、方程式 2sin²θ − 3sinθ + 1 = 0 の解はいくつあるか。", 3,
    lambda: len(sp.solveset(2*sp.sin(th)**2 - 3*sp.sin(th) + 1, th, sp.Interval.Ropen(0, 2*sp.pi))),
    "(2sinθ − 1)(sinθ − 1) = 0。sinθ = 1/2 で2個、sinθ = 1 で1個、計3個。")
add("b11", C, 3, "囲まれた面積", "放物線 y = x² − 2x と x 軸で囲まれた部分の面積を既約分数 a/b で表す。a + b を答えよ。", 7,
    lambda: frac_sum(sp.integrate(-(x**2-2*x), (x, 0, 2))), "∫₀² (2x − x²) dx = 4 − 8/3 = 4/3。a + b = 7。")
add("b12", C, 3, "等比数列の和", "初項 2、公比 3 の等比数列の初項から第 n 項までの和が、初めて 1000 を超える n を答えよ。", 7,
    next(i for i in range(1, 50) if 3**i - 1 > 1000), "Sₙ = 3ⁿ − 1。3⁶ − 1 = 728、3⁷ − 1 = 2186 より n = 7。")
def b13():
    a = 1
    for _ in range(9): a = 2*a + 1
    return a
add("b13", C, 3, "漸化式", "a₁ = 1、aₙ₊₁ = 2aₙ + 1 で定まる数列の a₁₀ を答えよ。", 1023,
    b13, "aₙ₊₁ + 1 = 2(aₙ + 1) より aₙ + 1 = 2ⁿ。a₁₀ = 2¹⁰ − 1 = 1023。")
add("b14", C, 3, "ベクトルの大きさ", "|a⃗| = 3、|b⃗| = 4、a⃗·b⃗ = 6 のとき、|2a⃗ − b⃗| を p√q（q は平方因子をもたない自然数）で表す。p + q を答えよ。", 9,
    lambda: (lambda v: 2 + 7 if sp.simplify(v - 2*sp.sqrt(7)) == 0 else -1)(sp.sqrt(4*9 - 4*6 + 16)),
    "|2a⃗ − b⃗|² = 4·9 − 4·6 + 16 = 28 より |2a⃗ − b⃗| = 2√7。p + q = 9。")
add("b15", C, 3, "三次方程式の実数解", "x の方程式 x³ − 3x² − 9x = k が異なる3つの実数解をもつような整数 k はいくつあるか。", 31,
    lambda: sum(1 for kk in range(-100, 100)
                if len([r for r in sp.Poly(x**3-3*x**2-9*x-kk, x).real_roots()]) == 3
                and len(set(sp.Poly(x**3-3*x**2-9*x-kk, x).real_roots())) == 3),
    "f(x) = x³ − 3x² − 9x は x = −1 で極大値 5、x = 3 で極小値 −27。−27 < k < 5 の整数で 31 個。")

# ───────── 数学III・C ─────────
C = "math3c"
add("c01", C, 1, "数列の極限", "n → ∞ のとき、(3n² + 1)/(n² + 2n) の極限値を答えよ。", 3,
    lambda: sp.limit((3*n**2+1)/(n**2+2*n), n, sp.oo), "分母分子を n² で割ると (3 + 1/n²)/(1 + 2/n) → 3。")
add("c02", C, 1, "複素数の累乗", "i を虚数単位とする。(1 + i)⁸ の値を答えよ。", 16,
    lambda: sp.expand((1+sp.I)**8), "(1 + i)² = 2i なので (1 + i)⁸ = (2i)⁴ = 16。")
add("c03", C, 1, "三角関数の極限", "x → 0 のとき、(sin 5x)/x の極限値を答えよ。", 5,
    lambda: sp.limit(sp.sin(5*x)/x, x, 0), "(sin 5x)/(5x) × 5 → 1 × 5 = 5。")
add("c04", C, 1, "対数関数の積分", "定積分 ∫₁ᵉ (2/x) dx の値を答えよ。", 2,
    lambda: sp.integrate(2/x, (x, 1, sp.E)), "[2 log x]₁ᵉ = 2 − 0 = 2。")
add("c05", C, 1, "合成関数の微分", "y = (2x + 1)⁵ の x = 0 における微分係数を答えよ。", 10,
    lambda: sp.diff((2*x+1)**5, x).subs(x, 0), "y′ = 5(2x + 1)⁴ × 2。x = 0 で 10。")
add("c06", C, 2, "無限等比級数", "無限級数 2/3 + (2/3)² + (2/3)³ + … の和を答えよ。", 2,
    lambda: sp.summation(sp.Rational(2, 3)**n, (n, 1, sp.oo)), "初項 2/3、公比 2/3 なので (2/3) ÷ (1 − 2/3) = 2。")
add("c07", C, 2, "楕円の焦点", "楕円 x²/25 + y²/9 = 1 の2つの焦点の間の距離を答えよ。", 8,
    2*sp.sqrt(25-9), "c = √(25 − 9) = 4。焦点は (±4, 0) で距離は 8。")
add("c08", C, 2, "部分積分", "定積分 ∫₀¹ x eˣ dx の値を答えよ。", 1,
    lambda: sp.integrate(x*sp.exp(x), (x, 0, 1)), "[x eˣ − eˣ]₀¹ = (e − e) − (0 − 1) = 1。")
add("c09", C, 2, "ド・モアブルの定理", "複素数 z が |z| = 2、arg z = π/3 を満たすとき、z⁶ の値を答えよ。", 64,
    lambda: sp.simplify((2*sp.exp(sp.I*sp.pi/3))**6), "z⁶ = 2⁶ (cos 2π + i sin 2π) = 64。")
add("c10", C, 2, "関数の極限", "x → 0 のとき、(1 − cos x)/x² の極限値を既約分数 a/b で表す。a + b を答えよ。", 3,
    lambda: frac_sum(sp.limit((1-sp.cos(x))/x**2, x, 0)), "(1 − cos x)/x² = sin²x / {x²(1 + cos x)} → 1/2。a + b = 3。")
add("c11", C, 3, "回転体の体積", "曲線 y = √x（0 ≦ x ≦ 4）と x 軸、直線 x = 4 で囲まれた部分を x 軸のまわりに1回転させた立体の体積を aπ と表す。a を答えよ。", 8,
    lambda: sp.integrate(x, (x, 0, 4)), "V = π∫₀⁴ (√x)² dx = π[x²/2]₀⁴ = 8π。")
add("c12", C, 3, "sin³x の積分", "sin³x を 0 から π/2 まで積分した値（定積分）を既約分数 a/b で表す。a + b を答えよ。", 5,
    lambda: frac_sum(sp.integrate(sp.sin(x)**3, (x, 0, sp.pi/2))),
    "sin³x = sin x (1 − cos²x)。cos x = u と置くと ∫₀¹ (1 − u²) du = 2/3。a + b = 5。")
def c13():
    w = sp.exp(2*sp.pi*sp.I/5)
    return sp.nsimplify(sp.N(sp.prod([1 - w**j for j in range(1, 5)]), 30))
add("c13", C, 3, "1の5乗根", "z⁵ = 1 の解のうち 1 でないものの1つを ω とする。(1 − ω)(1 − ω²)(1 − ω³)(1 − ω⁴) の値を答えよ。", 5,
    c13, "z⁵ − 1 = (z − 1)(z⁴ + z³ + z² + z + 1) で、ω, ω², ω³, ω⁴ は後者の根。z = 1 を代入して 1 + 1 + 1 + 1 + 1 = 5。")
def c14():
    O = sp.Matrix([0, 0, 0]); A = sp.Matrix([1, 0, 0])
    B = sp.Matrix([sp.Rational(1, 2), sp.sqrt(3)/2, 0])
    Cc = sp.Matrix([sp.Rational(1, 2), sp.sqrt(3)/6, sp.sqrt(sp.Rational(2, 3))])
    for u, v in [(A, B), (A, Cc), (B, Cc)]: assert sp.simplify(u.dot(v) - sp.Rational(1, 2)) == 0
    V = sp.simplify(abs(sp.Matrix.hstack(A, B, Cc).det())/6)
    assert sp.simplify(V - sp.sqrt(2)/12) == 0
    return 1 + 2 + 12
add("c14", C, 3, "四面体の体積", "四面体 OABC で |OA⃗| = |OB⃗| = |OC⃗| = 1、OA⃗·OB⃗ = OB⃗·OC⃗ = OC⃗·OA⃗ = 1/2 のとき、体積を a√b / c（a と c は互いに素、b は平方因子をもたない）で表す。a + b + c を答えよ。", 15,
    c14, "条件より各辺の長さが 1 の正四面体。体積は √2/12 なので a + b + c = 1 + 2 + 12 = 15。")
add("c15", C, 3, "サイクロイドの長さ", "曲線 x = t − sin t、y = 1 − cos t（0 ≦ t ≦ 2π）の長さを答えよ。", 8,
    lambda: sp.integrate(2*sp.sin(t/2), (t, 0, 2*sp.pi)),
    "(dx/dt)² + (dy/dt)² = 2 − 2cos t = 4sin²(t/2)。長さは 2sin(t/2) を t = 0 から 2π まで積分して [−4cos(t/2)] = 4 − (−4) = 8。")

# ── LaTeX 版を body / explanation に、従来の文字だけの文を plain に ──
import re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from problems_tex import TEX
assert set(TEX) == {p["id"] for p in P}, "problems_tex.py と問題の id が一致しません"
for p in P:
    tex_body, tex_expl = TEX[p["id"]]
    plain = re.sub(r"([A-Za-z]{1,2})\u20d7", r"ベクトル\1", p["body"])   # 結合文字の矢印は表示が崩れるため
    p["plain"] = plain
    p["body"], p["explanation"] = tex_body, tex_expl

assert len(P) == 60 and len({p["id"] for p in P}) == 60
for c in ["junior", "math1a", "math2b", "math3c"]:
    for d in (1, 2, 3):
        assert sum(1 for p in P if p["category"] == c and p["difficulty"] == d) == 5

# ── 数字を変えて作った問題・4択問題を足す（tools/gen_problems.py）──
import gen_problems
P.extend(gen_problems.generate())
import gen_subjects
P.extend(gen_subjects.generate())
import gen_units
P.extend(gen_units.generate())
import gen_math2
P.extend(gen_math2.generate())
import gen_content
P.extend(gen_content.generate())

# ── ヒントを付ける（問題の種類ごと）。ヒントの無い種類があれば、気づけるようにここで止める ──
from hints import HINTS, GENERIC
_missing = sorted({p["title"] for p in P if p["title"] not in HINTS})
assert not _missing, f"tools/hints.py にヒントがない種類: {_missing}"
for p in P:
    p["hint"] = HINTS[p["title"]]
assert len({p["id"] for p in P}) == len(P), "問題の id が重複しています"
for p in P:
    if "choices" in p:
        assert len(p["choices"]) == 4 and len(set(p["choices"])) == 4 and 0 <= p["answer"] < 4, p["id"]
    else:
        assert isinstance(p["answer"], int), p["id"]

# ── 単元（tools/units.py）に振り分ける ──
import units as _units
_known = {u[0] for u in _units.UNITS}
for p in P:
    p["unit"] = _units.unit_of(p)
    assert p["unit"] in _known, p["id"]
for u in _units.UNITS:
    assert all(q in _known for q in u[4]), u

import rates as _rates
_rates.assign(P)                 # 各問題に、10人中の正解見込み（rate）を付ける

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(root, "mathscreen", "Resources", "units.json"), "w", encoding="utf-8") as f:
    json.dump(_units.units_json(), f, ensure_ascii=False, indent=2)
out = os.path.join(root, "mathscreen", "Resources", "problems.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(P, f, ensure_ascii=False, indent=2)
prev = os.path.join(root, "preview", "problems.js")
os.makedirs(os.path.dirname(prev), exist_ok=True)
with open(prev, "w", encoding="utf-8") as f:
    f.write("window.PROBLEMS = " + json.dumps(P, ensure_ascii=False) + ";\n")
print(f"OK: {len(P)} 問すべて検算済み -> {out}")
