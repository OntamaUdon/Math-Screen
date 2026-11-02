"""連立方程式の利用（文章題）と三角関数の加法定理。数字を変えて作る問題。"""
from fractions import Fraction
from math import gcd
import gen_problems as G
from gen_problems import fmt, add, make

R = G.Rng(20261108)


def fr(f):
    f = Fraction(f)
    return "$%d$" % f.numerator if f.denominator == 1 else "$\\dfrac{%d}{%d}$" % (f.numerator, f.denominator)


def choice_set(correct, wrongs):
    opts = [correct]
    for w in wrongs:
        if w not in opts: opts.append(w)
    if len(opts) < 4: return None
    opts = opts[:4]
    R.shuffle(opts)
    return opts, opts.index(correct)


# ═════════ 連立方程式の利用 ═════════
def t_age():
    x, y = R.randint(30, 50), R.randint(8, 16)       # 親と子の年齢
    s, k = x + y, None
    return add(601, "junior", 2, "連立方程式の文章題", fmt("親と子の年齢の和は $«s»$ 歳で、親の年齢は子の年齢の $«a»$ 倍より $«b»$ 歳多い。子の年齢を答えよ。", s=x + y, a=3, b=x - 3 * y) if x - 3 * y > 0 else "", y,
               fmt("子を $y$、親を $x$ とすると $x + y = «s»$、$x = 3y + «b»$。解いて $y = «y»$。", s=x + y, b=x - 3 * y, y=y)) if x - 3 * y > 0 else False


def t_price():
    a, b = R.randint(60, 150), R.randint(80, 250)
    if a == b: return False
    x, y = R.randint(2, 9), R.randint(2, 9)
    return add(602, "junior", 2, "連立方程式の文章題",
               fmt("りんご $«x»$ 個とみかん $«y»$ 個を買うと $«t1»$ 円、りんご $«y»$ 個とみかん $«x»$ 個を買うと $«t2»$ 円だった。りんご1個の値段を答えよ。", x=x, y=y, t1=a * x + b * y, t2=a * y + b * x) if x != y else "", a,
               fmt("りんごを $a$ 円、みかんを $b$ 円とすると $«x»a + «y»b = «t1»$、$«y»a + «x»b = «t2»$。解いて $a = «a»$。", x=x, y=y, t1=a * x + b * y, t2=a * y + b * x, a=a)) if x != y else False


def t_ticket():
    a, b = R.choice([(500, 300), (600, 400), (800, 500), (1000, 600)]); n = R.randint(8, 20); x = R.randint(2, n - 2)
    return add(603, "junior", 2, "連立方程式の文章題", fmt("大人 $«a»$ 円、子ども $«b»$ 円の入場券を合わせて $«n»$ 枚買ったら、代金は $«t»$ 円だった。子どもの券は何枚か。", a=a, b=b, n=n, t=a * x + b * (n - x)), n - x,
               fmt("大人を $x$ 枚、子どもを $y$ 枚とすると $x + y = «n»$、$«a»x + «b»y = «t»$。解いて $y = «y»$。", n=n, a=a, b=b, t=a * x + b * (n - x), y=n - x))


def t_walk():
    v1, v2 = R.randint(60, 90), R.randint(40, 80)
    if v1 <= v2: return False
    t = R.randint(5, 20)
    return add(604, "junior", 2, "連立方程式の文章題", fmt("A さんは分速 $«v1»$ m、B さんは分速 $«v2»$ m で、同じ地点から同じ向きに同時に歩き出した。$«t»$ 分後、2人の間は何 m はなれているか。", v1=v1, v2=v2, t=t), (v1 - v2) * t,
               fmt("1分で $«d»$ m ずつ差がつくので $«d» \\times «t» = «r»$ m。", d=v1 - v2, t=t, r=(v1 - v2) * t))


def t_coin():
    x, y = R.randint(2, 9), R.randint(2, 9)
    return add(605, "junior", 2, "連立方程式の文章題", fmt("10円玉と50円玉が合わせて $«n»$ 枚あり、合計金額は $«t»$ 円である。10円玉は何枚か。", n=x + y, t=10 * x + 50 * y), x,
               fmt("10円玉を $x$ 枚、50円玉を $y$ 枚とすると $x + y = «n»$、$10x + 50y = «t»$。解いて $x = «x»$。", n=x + y, t=10 * x + 50 * y, x=x))


def t_total():
    a, b = R.randint(11, 40), R.randint(11, 40)
    if a == b: return False
    return add(606, "junior", 2, "連立方程式の文章題", fmt("2つの数があり、和が $«s»$、差が $«d»$ である。大きいほうの数を答えよ。", s=a + b, d=abs(a - b)), max(a, b),
               fmt("大きいほうは $(«s» + «d») \\div 2 = «m»$。", s=a + b, d=abs(a - b), m=max(a, b)))


# ═════════ 加法定理 ═════════
_TRIPLES = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]


def c_sin_add():
    (a, b, c), (p, q, r) = R.choice(_TRIPLES), R.choice(_TRIPLES)
    sa, ca, sb, cb = Fraction(a, c), Fraction(b, c), Fraction(p, r), Fraction(q, r)
    good = sa * cb + ca * sb
    cs = choice_set(fr(good), [fr(sa * cb - ca * sb), fr(ca * cb + sa * sb), fr(ca * cb - sa * sb), fr(sa * sb + ca * cb + 0)])
    if cs is None: return False
    return add(611, "math2b", 3, "加法定理", fmt("$0 < \\alpha, \\beta < \\dfrac{\\pi}{2}$ で $\\sin\\alpha = «sa»$、$\\sin\\beta = «sb»$ のとき、$\\sin(\\alpha + \\beta)$ の値を選べ。", sa=fr(sa).strip("$"), sb=fr(sb).strip("$")), cs[1],
               fmt("$\\cos\\alpha = «ca»$、$\\cos\\beta = «cb»$。$\\sin\\alpha\\cos\\beta + \\cos\\alpha\\sin\\beta = «g»$。", ca=fr(ca).strip("$"), cb=fr(cb).strip("$"), g=fr(good).strip("$")), cs[0])


def c_cos_add():
    (a, b, c), (p, q, r) = R.choice(_TRIPLES), R.choice(_TRIPLES)
    sa, ca, sb, cb = Fraction(a, c), Fraction(b, c), Fraction(p, r), Fraction(q, r)
    good = ca * cb - sa * sb
    cs = choice_set(fr(good), [fr(ca * cb + sa * sb), fr(sa * cb + ca * sb), fr(sa * cb - ca * sb), fr(-good) if good != 0 else fr(Fraction(1, 2))])
    if cs is None: return False
    return add(612, "math2b", 3, "加法定理", fmt("$0 < \\alpha, \\beta < \\dfrac{\\pi}{2}$ で $\\sin\\alpha = «sa»$、$\\sin\\beta = «sb»$ のとき、$\\cos(\\alpha + \\beta)$ の値を選べ。", sa=fr(sa).strip("$"), sb=fr(sb).strip("$")), cs[1],
               fmt("$\\cos(\\alpha + \\beta) = \\cos\\alpha\\cos\\beta - \\sin\\alpha\\sin\\beta = «g»$。", g=fr(good).strip("$")), cs[0])


def t_tan_add():
    p, q = R.randint(2, 7), R.randint(2, 7)
    if p == q: return False
    # tan α = 1/p, tan β = 1/q → tan(α+β) = (p+q)/(pq-1)
    num, den = p + q, p * q - 1
    return add(613, "math2b", 3, "加法定理", fmt("$\\tan\\alpha = \\dfrac{1}{«p»}$、$\\tan\\beta = \\dfrac{1}{«q»}$ のとき、$\\tan(\\alpha + \\beta) = \\dfrac{m}{n}$（既約分数）と表せる。$m + n$ の値を答えよ。", p=p, q=q),
               (lambda f: f.numerator + f.denominator)(Fraction(num, den)),
               fmt("$\\tan(\\alpha + \\beta) = \\dfrac{\\frac{1}{«p»} + \\frac{1}{«q»}}{1 - \\frac{1}{«pq»}} = \\dfrac{«n»}{«d»}$。", p=p, q=q, pq=p * q, n=num, d=den))


def t_double():
    a, b, c = R.choice(_TRIPLES)
    sa, ca = Fraction(a, c), Fraction(b, c)
    return add(614, "math2b", 3, "加法定理", fmt("$0 < \\alpha < \\dfrac{\\pi}{2}$ で $\\sin\\alpha = «sa»$ のとき、$\\sin 2\\alpha = \\dfrac{m}{n}$（既約分数）と表せる。$m + n$ の値を答えよ。", sa=fr(sa).strip("$")),
               (lambda f: f.numerator + f.denominator)(2 * sa * ca),
               fmt("$\\cos\\alpha = «ca»$。$\\sin 2\\alpha = 2\\sin\\alpha\\cos\\alpha = «v»$。", ca=fr(ca).strip("$"), v=fr(2 * sa * ca).strip("$")))


def c_special():
    items = [("\\sin 75^\\circ", "\\dfrac{\\sqrt{6} + \\sqrt{2}}{4}"), ("\\cos 75^\\circ", "\\dfrac{\\sqrt{6} - \\sqrt{2}}{4}"), ("\\sin 15^\\circ", "\\dfrac{\\sqrt{6} - \\sqrt{2}}{4}"),
             ("\\cos 15^\\circ", "\\dfrac{\\sqrt{6} + \\sqrt{2}}{4}"), ("\\tan 75^\\circ", "2 + \\sqrt{3}"), ("\\tan 15^\\circ", "2 - \\sqrt{3}"),
             ("\\sin 105^\\circ", "\\dfrac{\\sqrt{6} + \\sqrt{2}}{4}"), ("\\cos 105^\\circ", "\\dfrac{\\sqrt{2} - \\sqrt{6}}{4}")]
    name, good = R.choice(items)
    pool = ["\\dfrac{\\sqrt{6} + \\sqrt{2}}{4}", "\\dfrac{\\sqrt{6} - \\sqrt{2}}{4}", "\\dfrac{\\sqrt{2} - \\sqrt{6}}{4}", "2 + \\sqrt{3}", "2 - \\sqrt{3}", "\\dfrac{\\sqrt{3}}{2}"]
    wr = [p for p in pool if p != good]; R.shuffle(wr)
    cs = choice_set("$%s$" % good, ["$%s$" % w for w in wr[:3]])
    return add(615, "math2b", 3, "加法定理", fmt("加法定理を使って、$«n»$ の値を選べ。", n=name), cs[1],
               "$75^\\circ = 45^\\circ + 30^\\circ$、$15^\\circ = 45^\\circ - 30^\\circ$ などと分けて加法定理を使う。", cs[0])


INTEGER_TEMPLATES = [t_age, t_price, t_ticket, t_walk, t_coin, t_total, t_tan_add, t_double]
CHOICE_TEMPLATES = [c_sin_add, c_cos_add, c_special]


def generate(per_template=8):
    G.OUT.clear(); G._seen.clear()
    for fn in INTEGER_TEMPLATES + CHOICE_TEMPLATES: make(0, per_template, fn)
    return list(G.OUT)


if __name__ == "__main__":
    ps = generate()
    print(len(ps))
    for p in ps[::6]: print(p["id"], p["plain"][:90], "->", p["answer"])
