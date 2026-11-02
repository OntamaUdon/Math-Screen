"""小学算数の問題（整数で答える問題と4択問題）。tools/build_problems.py から呼ばれる。

- 数字を変えて作る。乱数は自前の線形合同法で、同じ問題が同じ順で出る（CI の差分確認のため）。
- 正解は、公式とは別に総当たりでも確かめてから登録する。
- category は "elem"（小学算数）。単元は tools/units.py の TITLE_UNIT で決まる。
"""
from fractions import Fraction
from math import gcd, lcm, comb, perm
import gen_problems as G
from gen_problems import fmt, add, make

R = G.Rng(20261103)
CAT = "elem"


def dec(x):
    """Fraction を小数の文字列にする（分母が10のべき乗のもの）。"""
    x = Fraction(x)
    # 小数点以下の桁数
    for k in range(0, 5):
        if (x * 10 ** k).denominator == 1: break
    else:
        raise ValueError(x)
    v = int(x * 10 ** k)
    sign = "-" if v < 0 else ""
    v = abs(v)
    if k == 0: return sign + str(v)
    t = str(v).rjust(k + 1, "0")
    return sign + t[:-k] + "." + t[-k:]


def choice_set(correct, wrongs):
    opts = [correct]
    for w in wrongs:
        if w not in opts: opts.append(w)
    if len(opts) < 4: return None
    opts = opts[:4]
    R.shuffle(opts)
    return opts, opts.index(correct)


# ═════════ 四則計算 ═════════
def t_order():
    e = R.randint(2, 9); k = R.randint(2, 9); d = e * k
    a, b, c = R.randint(5, 30), R.randint(2, 9), R.randint(2, 9)
    ans = a + b * c - k
    if ans <= 0: return False
    return add(101, CAT, 1, "計算の順序", fmt("$«a» + «b» \\times «c» - «d» \\div «e»$ を計算せよ。", a=a, b=b, c=c, d=d, e=e), ans,
               fmt("かけ算・わり算を先に計算します。$«b» \\times «c» = «bc»$、$«d» \\div «e» = «k»$ なので $«a» + «bc» - «k» = «ans»$。",
                   a=a, b=b, c=c, d=d, e=e, bc=b * c, k=k, ans=ans))


def t_paren():
    a, b, c, d = R.randint(2, 15), R.randint(2, 15), R.randint(2, 9), R.randint(1, 20)
    ans = (a + b) * c - d
    if ans <= 0: return False
    return add(102, CAT, 1, "かっこのある計算", fmt("$(«a» + «b») \\times «c» - «d»$ を計算せよ。", a=a, b=b, c=c, d=d), ans,
               fmt("かっこの中を先に計算します。$«a» + «b» = «s»$、$«s» \\times «c» = «p»$、$«p» - «d» = «ans»$。",
                   a=a, b=b, c=c, d=d, s=a + b, p=(a + b) * c, ans=ans))


def t_clever():
    a, c = R.choice([(25, 4), (125, 8), (5, 20), (50, 2)]); b = R.randint(3, 19)
    if R.randint(0, 1): a, c = c, a
    return add(103, CAT, 2, "くふうした計算", fmt("くふうして計算せよ。 $«a» \\times «b» \\times «c»$", a=a, b=b, c=c), a * b * c,
               fmt("先に $«a» \\times «c» = «ac»$ を計算すると楽です。$«ac» \\times «b» = «ans»$。", a=a, b=b, c=c, ac=a * c, ans=a * b * c))


def t_mul():
    a, b = R.randint(12, 48), R.randint(11, 29)
    return add(104, CAT, 2, "かけ算の筆算", fmt("$«a» \\times «b»$ を計算せよ。", a=a, b=b), a * b,
               fmt("$«a» \\times «b» = «a» \\times «b1» + «a» \\times «b2» = «x» + «y» = «ans»$。",
                   a=a, b=b, b1=b // 10 * 10, b2=b % 10, x=a * (b // 10 * 10), y=a * (b % 10), ans=a * b))


def t_rem():
    d = R.randint(3, 9); q = R.randint(5, 30); r = R.randint(1, d - 1); N = d * q + r
    assert N % d == r
    return add(105, CAT, 1, "あまりのあるわり算", fmt("$«N» \\div «d»$ のあまりを答えよ。", N=N, d=d), r,
               fmt("$«N» = «d» \\times «q» + «r»$ なので、あまりは $«r»$。", N=N, d=d, q=q, r=r))


# ═════════ 小数と分数 ═════════
def c_decmul():
    A = Fraction(R.randint(12, 49), 10); B = Fraction(R.randint(2, 9), 10)
    P = A * B
    cs = choice_set(dec(P), [dec(P * 10), dec(P / 10), dec(P + Fraction(1, 10))])
    if cs is None: return False
    return add(106, CAT, 1, "小数のかけ算", fmt("$«a» \\times «b»$ の答えを選べ。", a=dec(A), b=dec(B)), cs[1],
               fmt("小数点を無視して $«x» \\times «y» = «z»$。小数点以下の桁数の合計だけ戻して $«p»$。",
                   x=int(A * 10), y=int(B * 10), z=int(A * 10) * int(B * 10), p=dec(P)), cs[0])


def t_fracsum():
    n = R.randint(3, 9); a = R.randint(1, n - 1); k = R.randint(1, 3); b = n * k - a
    if b <= 0: return False
    return add(107, CAT, 1, "分数のたし算", fmt("$\\dfrac{«a»}{«n»} + \\dfrac{«b»}{«n»}$ を計算せよ。", a=a, b=b, n=n), k,
               fmt("分母が同じなので分子を足します。$\\dfrac{«s»}{«n»} = «k»$。", s=a + b, n=n, k=k))


def t_reduce():
    g = R.randint(2, 9); q = R.randint(3, 12); p = R.randint(1, q - 1)
    if gcd(p, q) != 1: return False
    return add(108, CAT, 1, "約分", fmt("$\\dfrac{«P»}{«Q»}$ を約分して、これ以上約分できない形にしたときの分母を答えよ。", P=p * g, Q=q * g), q,
               fmt("分子と分母を最大公約数 $«g»$ でわると $\\dfrac{«p»}{«q»}$。分母は $«q»$。", g=g, p=p, q=q))


def t_place():
    n = R.randint(101, 999) if R.randint(0, 1) else R.randint(1001, 4999)
    if n % 10 == 0: return False
    f = 100 if n < 1000 else 1000
    x = Fraction(n, f)
    return add(109, CAT, 1, "小数の位取り", fmt("$«x» \\times «f»$ を計算せよ。", x=dec(x), f=f), n,
               fmt("$«f»$ をかけると、小数点が右に «z» けた動きます。答えは $«n»$。", f=f, z=2 if f == 100 else 3, n=n))


def t_unit():
    kind = R.choice(["km", "kg", "L", "hr"])
    if kind == "km":
        x = Fraction(R.randint(11, 99), 10); return add(135, CAT, 1, "単位の換算", fmt("$«x»$ km は何 m か。", x=dec(x)), int(x * 1000),
                                                         fmt("$1$ km $= 1000$ m なので $«x» \\times 1000 = «a»$。", x=dec(x), a=int(x * 1000)))
    if kind == "kg":
        x = Fraction(R.randint(11, 99), 10); return add(135, CAT, 1, "単位の換算", fmt("$«x»$ kg は何 g か。", x=dec(x)), int(x * 1000),
                                                         fmt("$1$ kg $= 1000$ g なので $«x» \\times 1000 = «a»$。", x=dec(x), a=int(x * 1000)))
    if kind == "L":
        x = Fraction(R.randint(11, 99), 10); return add(135, CAT, 1, "単位の換算", fmt("$«x»$ L は何 mL か。", x=dec(x)), int(x * 1000),
                                                         fmt("$1$ L $= 1000$ mL なので $«x» \\times 1000 = «a»$。", x=dec(x), a=int(x * 1000)))
    h, m = R.randint(1, 5), R.randint(5, 55)
    return add(135, CAT, 1, "単位の換算", fmt("$«h»$ 時間 $«m»$ 分は何分か。", h=h, m=m), h * 60 + m,
               fmt("$1$ 時間 $= 60$ 分なので $«h» \\times 60 + «m» = «a»$。", h=h, m=m, a=h * 60 + m))


# ═════════ 約数と倍数 ═════════
def t_gcd():
    g = R.randint(2, 12); p, q = R.randint(2, 9), R.randint(2, 9)
    if p == q or gcd(p, q) != 1: return False
    a, b = g * p, g * q
    assert gcd(a, b) == g
    return add(110, CAT, 1, "最大公約数", fmt("$«a»$ と $«b»$ の最大公約数を答えよ。", a=a, b=b), g,
               fmt("$«a» = «g»\\times«p»$、$«b» = «g»\\times«q»$ と書けるので、最大公約数は $«g»$。", a=a, b=b, g=g, p=p, q=q))


def t_lcm():
    a, b = R.randint(4, 24), R.randint(4, 24)
    if a == b or lcm(a, b) > 120 or lcm(a, b) in (a, b): return False
    return add(111, CAT, 2, "最小公倍数", fmt("$«a»$ と $«b»$ の最小公倍数を答えよ。", a=a, b=b), lcm(a, b),
               fmt("最大公約数は $«g»$ なので、最小公倍数は $«a» \\times «b» \\div «g» = «l»$。", a=a, b=b, g=gcd(a, b), l=lcm(a, b)))


def t_ndiv():
    n = R.choice([12, 18, 20, 24, 28, 30, 36, 40, 42, 45, 48, 50, 54, 56, 60])
    cnt = sum(1 for d in range(1, n + 1) if n % d == 0)
    return add(112, CAT, 1, "約数を数える", fmt("$«n»$ の約数は全部で何個あるか。", n=n), cnt,
               fmt("$«n»$ をわりきれる数は «ds» の $«c»$ 個。", n=n, ds="、".join(str(d) for d in range(1, n + 1) if n % d == 0), c=cnt))


def t_nmult():
    a = R.randint(3, 9); N = R.randint(5, 20) * 10
    return add(113, CAT, 1, "倍数を数える", fmt("$1$ から $«N»$ までの整数のうち、$«a»$ の倍数は何個あるか。", N=N, a=a), N // a,
               fmt("$«N» \\div «a»$ の商が個数です。$«N» \\div «a» = «q»$ あまり $«r»$ なので $«q»$ 個。", N=N, a=a, q=N // a, r=N % a))


def t_nmult2():
    a, b = R.choice([(2, 3), (3, 4), (2, 5), (3, 5), (4, 5), (2, 7), (3, 7)]); N = R.randint(6, 20) * 10
    cnt = sum(1 for i in range(1, N + 1) if i % a == 0 and i % b == 0)
    assert cnt == N // lcm(a, b)
    return add(114, CAT, 2, "倍数を数える", fmt("$1$ から $«N»$ までの整数のうち、$«a»$ でも $«b»$ でもわりきれる数は何個あるか。", N=N, a=a, b=b), cnt,
               fmt("$«a»$ と $«b»$ の最小公倍数は $«l»$。$«N» \\div «l»$ の商は $«c»$。", a=a, b=b, l=lcm(a, b), N=N, c=cnt))


def c_prime():
    primes = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    comps = [21, 27, 33, 39, 49, 51, 57, 63, 69, 77, 87, 91]
    p = R.choice(primes); R.shuffle(comps)
    cs = choice_set(str(p), [str(c) for c in comps[:3]])
    if cs is None: return False
    return add(134, CAT, 1, "素数", "次のうち、素数はどれか。", cs[1],
               fmt("素数は、$1$ と自分自身でしかわりきれない数です。ほかの数は $3$ や $7$ などでわりきれます。正解は $«p»$。", p=p), cs[0])


# ═════════ 割合と比 ═════════
def t_percent():
    N = R.choice([20, 40, 50, 60, 80, 100, 120, 150, 200, 250]); p = R.choice([10, 20, 25, 30, 40, 50, 60, 75, 80])
    if (N * p) % 100: return False
    return add(115, CAT, 1, "割合", fmt("定員 $«N»$ 人の $«p»\\%$ は何人か。", N=N, p=p), N * p // 100,
               fmt("$«N» \\times \\dfrac{«p»}{100} = «a»$。", N=N, p=p, a=N * p // 100))


def t_prop():
    a, b = R.randint(2, 9), R.randint(2, 9)
    if a == b or gcd(a, b) != 1: return False
    k = R.randint(2, 9)
    return add(116, CAT, 1, "比", fmt("$«a» : «b» = «c» : \\square$ のとき、$\\square$ にあてはまる数を答えよ。", a=a, b=b, c=a * k), b * k,
               fmt("前の数が $«k»$ 倍になっているので、後ろの数も $«k»$ 倍。$«b» \\times «k» = «x»$。", k=k, b=b, x=b * k))


def t_split():
    a, b = R.randint(1, 6), R.randint(2, 7)
    if a >= b or gcd(a, b) != 1: return False
    k = R.randint(3, 12); N = (a + b) * k
    big = R.randint(0, 1)
    return add(117, CAT, 2, "比で分ける", fmt("$«N»$ 個のあめを $«a» : «b»$ に分ける。«w»ほうは何個か。", N=N, a=a, b=b, w="多い" if big else "少ない"),
               b * k if big else a * k,
               fmt("全体は $«a» + «b» = «t»$ 等分。$1$ 等分は $«N» \\div «t» = «k»$ 個。«w»ほうは $«ans»$ 個。",
                   a=a, b=b, t=a + b, N=N, k=k, w="多い" if big else "少ない", ans=b * k if big else a * k))


def t_discount():
    P = R.randint(5, 30) * 100; q = R.randint(1, 5)
    ans = P * (10 - q) // 10
    return add(118, CAT, 1, "割引", fmt("定価 $«P»$ 円の品物を $«q»$ 割引で買う。代金は何円か。", P=P, q=q), ans,
               fmt("$«q»$ 割引は $«q»0\\%$ 引きなので、代金は定価の $«r»$ 割。$«P» \\times \\dfrac{«r»}{10} = «ans»$。", q=q, r=10 - q, P=P, ans=ans))


def t_salt():
    N = R.choice([100, 200, 300, 400, 500, 250, 150]); p = R.choice([2, 4, 5, 8, 10, 12, 15, 20])
    if (N * p) % 100: return False
    return add(119, CAT, 2, "食塩水の濃さ", fmt("濃さ $«p»\\%$ の食塩水 $«N»$ g には、食塩が何 g ふくまれるか。", p=p, N=N), N * p // 100,
               fmt("$«N» \\times \\dfrac{«p»}{100} = «a»$ g。", N=N, p=p, a=N * p // 100))


# ═════════ 速さ ═════════
def t_speed():
    v = R.choice([20, 25, 30, 40, 45, 50, 60, 75, 80]); t = R.randint(2, 5); d = v * t
    return add(120, CAT, 1, "速さを求める", fmt("$«d»$ km の道のりを $«t»$ 時間で走った。時速は何 km か。", d=d, t=t), v,
               fmt("速さ $=$ 道のり $\\div$ 時間 なので $«d» \\div «t» = «v»$。", d=d, t=t, v=v))


def t_time():
    v = R.choice([30, 40, 48, 60, 72, 90]); d = R.randint(5, 120)
    if (d * 60) % v: return False
    m = d * 60 // v
    if not 10 <= m <= 180: return False
    return add(121, CAT, 2, "時間を求める", fmt("時速 $«v»$ km で $«d»$ km 進むには、何分かかるか。", v=v, d=d), m,
               fmt("時間 $=$ 道のり $\\div$ 速さ なので $«d» \\div «v» = \\dfrac{«d»}{«v»}$ 時間。分になおして $«m»$ 分。", v=v, d=d, m=m))


def t_dist():
    v = R.choice([50, 60, 70, 80, 90, 100, 120]); t = R.randint(5, 30)
    return add(122, CAT, 1, "道のりを求める", fmt("分速 $«v»$ m で $«t»$ 分歩くと、何 m 進むか。", v=v, t=t), v * t,
               fmt("道のり $=$ 速さ $\\times$ 時間 なので $«v» \\times «t» = «d»$。", v=v, t=t, d=v * t))


def t_meet():
    a, b = R.randint(40, 90), R.randint(40, 90)
    if a == b: return False
    k = R.randint(3, 15); D = (a + b) * k
    return add(123, CAT, 2, "出会うまでの時間", fmt("$«D»$ m はなれた2地点から、2人が向かい合って同時に歩き出す。分速はそれぞれ $«a»$ m と $«b»$ m。何分後に出会うか。", D=D, a=a, b=b), k,
               fmt("1分間に近づく道のりは $«a» + «b» = «s»$ m。$«D» \\div «s» = «k»$ 分後。", a=a, b=b, s=a + b, D=D, k=k))


# ═════════ 面積と体積 ═════════
def t_area():
    b, h = R.randint(4, 20), R.randint(4, 20)
    if (b * h) % 2: return False
    return add(124, CAT, 1, "三角形の面積", fmt("底辺 $«b»$ cm、高さ $«h»$ cm の三角形の面積は何 cm² か。", b=b, h=h), b * h // 2,
               fmt("三角形の面積 $=$ 底辺 $\\times$ 高さ $\\div 2$ なので $«b» \\times «h» \\div 2 = «a»$。", b=b, h=h, a=b * h // 2))


def t_trapezoid():
    a, b, h = R.randint(3, 12), R.randint(5, 18), R.randint(3, 12)
    if a >= b or ((a + b) * h) % 2: return False
    return add(125, CAT, 2, "台形の面積", fmt("上底 $«a»$ cm、下底 $«b»$ cm、高さ $«h»$ cm の台形の面積は何 cm² か。", a=a, b=b, h=h), (a + b) * h // 2,
               fmt("台形の面積 $=$ （上底 $+$ 下底）$\\times$ 高さ $\\div 2$ なので $(«a» + «b») \\times «h» \\div 2 = «s»$。", a=a, b=b, h=h, s=(a + b) * h // 2))


def t_circle():
    r = R.choice([10, 20, 30, 40]); ans = 314 * r * r // 100
    assert 314 * r * r % 100 == 0
    return add(126, CAT, 2, "円の面積", fmt("半径 $«r»$ cm の円の面積は何 cm² か。円周率は $3.14$ とする。", r=r), ans,
               fmt("円の面積 $=$ 半径 $\\times$ 半径 $\\times 3.14$ なので $«r» \\times «r» \\times 3.14 = «a»$。", r=r, a=ans))


def t_circumference():
    d = R.choice([50, 100, 150, 200, 300]); ans = 314 * d // 100
    assert 314 * d % 100 == 0
    return add(127, CAT, 1, "円周の長さ", fmt("直径 $«d»$ cm の円の円周は何 cm か。円周率は $3.14$ とする。", d=d), ans,
               fmt("円周 $=$ 直径 $\\times 3.14$ なので $«d» \\times 3.14 = «a»$。", d=d, a=ans))


def t_volume():
    a, b, c = R.randint(2, 12), R.randint(2, 12), R.randint(2, 12)
    return add(128, CAT, 1, "直方体の体積", fmt("たて $«a»$ cm、よこ $«b»$ cm、高さ $«c»$ cm の直方体の体積は何 cm³ か。", a=a, b=b, c=c), a * b * c,
               fmt("体積 $=$ たて $\\times$ よこ $\\times$ 高さ なので $«a» \\times «b» \\times «c» = «v»$。", a=a, b=b, c=c, v=a * b * c))


def t_surface():
    a = R.randint(2, 15)
    return add(129, CAT, 2, "立方体の表面積", fmt("1辺が $«a»$ cm の立方体の表面積は何 cm² か。", a=a), 6 * a * a,
               fmt("1つの面は $«a» \\times «a» = «s»$ cm²。面は6つなので $«s» \\times 6 = «t»$。", a=a, s=a * a, t=6 * a * a))


def t_angle():
    a, b = R.randint(25, 80), R.randint(25, 80)
    if a == b or a + b >= 170: return False
    return add(130, CAT, 1, "三角形の角度", fmt("三角形の2つの角が $«a»^\\circ$ と $«b»^\\circ$ のとき、残りの角は何度か。", a=a, b=b), 180 - a - b,
               fmt("三角形の内角の和は $180^\\circ$。$180 - «a» - «b» = «c»$。", a=a, b=b, c=180 - a - b))


# ═════════ 場合の数 ═════════
def t_perm():
    n, r = R.choice([(4, 2), (5, 2), (4, 3), (5, 3), (6, 2), (6, 3)])
    ans = perm(n, r)
    import itertools
    assert ans == sum(1 for _ in itertools.permutations(range(n), r))
    return add(131, CAT, 2, "並べ方", fmt("$«n»$ 人の中から $«r»$ 人を選んで、1列に並べる。並べ方は全部で何通りか。", n=n, r=r), ans,
               fmt("1番目は $«n»$ 通り、2番目は $«m»$ 通り…と考えて、かけ算します。答えは $«a»$ 通り。", n=n, m=n - 1, a=ans))


def t_comb():
    n = R.randint(4, 10)
    import itertools
    ans = sum(1 for _ in itertools.combinations(range(n), 2))
    assert ans == comb(n, 2)
    return add(132, CAT, 2, "組み合わせ", fmt("$«n»$ 人の中から、そうじ当番を $2$ 人選ぶ。選び方は全部で何通りか。", n=n), ans,
               fmt("並べ方は $«n» \\times «m»$ 通りですが、$2$ 人の順番は関係ないので $2$ でわります。$«n» \\times «m» \\div 2 = «a»$。", n=n, m=n - 1, a=ans))


def t_dice():
    s = R.randint(3, 11)
    ways = sum(1 for i in range(1, 7) for j in range(1, 7) if i + j == s)
    return add(133, CAT, 2, "さいころの目", fmt("大小2つのさいころを同時に投げる。目の和が $«s»$ になる場合は何通りか。", s=s), ways,
               fmt("（大の目, 小の目）の組を書き出して数えると、全部で $«w»$ 通り。", w=ways))


def t_pick():
    a, b, c = R.randint(2, 5), R.randint(2, 5), R.randint(2, 4)
    return add(136, CAT, 1, "選び方の組", fmt("シャツが $«a»$ 種類、ズボンが $«b»$ 種類、くつが $«c»$ 種類ある。1つずつ選ぶ組み合わせは何通りか。", a=a, b=b, c=c), a * b * c,
               fmt("かけ算で数えます。$«a» \\times «b» \\times «c» = «t»$ 通り。", a=a, b=b, c=c, t=a * b * c))


INTEGER_TEMPLATES = [t_order, t_paren, t_clever, t_mul, t_rem, t_fracsum, t_reduce, t_place, t_unit,
                     t_gcd, t_lcm, t_ndiv, t_nmult, t_nmult2, t_percent, t_prop, t_split, t_discount, t_salt,
                     t_speed, t_time, t_dist, t_meet, t_area, t_trapezoid, t_circle, t_circumference, t_volume, t_surface, t_angle,
                     t_perm, t_comb, t_dice, t_pick]
CHOICE_TEMPLATES = [c_decmul, c_prime]
TEMPLATE_NO = {fn: 101 + i for i, fn in enumerate(INTEGER_TEMPLATES)}   # （参考）


def generate(per_template=6):
    G.OUT.clear(); G._seen.clear()
    for fn in INTEGER_TEMPLATES + CHOICE_TEMPLATES: make(0, per_template, fn)
    return list(G.OUT)


if __name__ == "__main__":
    ps = generate()
    print(len(ps), "問")
    for p in ps[::9]:
        print(p["id"], p["difficulty"], "|", p["plain"][:80], "->", p["answer"])
