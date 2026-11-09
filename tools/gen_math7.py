"""数学の問題を増やす（約1,000問）。難易度を4段階にする（1 初級・2 中級・3 上級・4 最上級）。

- どの問題も、答えをコード（総当たり・sympy・分数の計算）で求めてから作る。手で書いた答えは使わない。
- 最上級は、難関大以外の大学の入試（教科書の例題には載らない程度）から、東大・京大・東工大の2次試験の
  易しめの問題くらいまでを目安にした、自作の問題。実際の入試問題をそのまま使ったものではない。
- 数字だけを変えて作る問題なので、同じ種類（title）の問題は、アプリが「酷似した問題」としてまとめて扱う。
"""
import math
import itertools
import random
from fractions import Fraction as F
import sympy as sp
from gen_problems import tex2plain

R = random.Random(20261110)
OUT = []
_seen = set()
_count = {}

CAT = {}
for u in "e_calc e_decfrac e_divmult e_ratio e_speed e_geom e_count e_avg".split(): CAT[u] = "elem"
for u in ("m_signed m_expr m_linear m_simul m_ineq m_sqrt m_factor m_quad m_func2 m_pythag m_polygon m_prob m_int m_prop "
          "m_expand m_quad_word m_pythag_use m_simul_word m_linfunc m_algebra m_similar m_circle m_space m_data").split(): CAT[u] = "junior"
for u in "h_quadfunc h_quadeq h_trig h_logic h_abs h_count h_prob h_nt h_geom h_stat".split(): CAT[u] = "math1a"
for u in "h_exp h_circle h_trig2 h_addition h_cplx h_binom h_diff h_diff2 h_integ h_integ_app h_seq h_seq2 h_vec h_space".split(): CAT[u] = "math2b"
for u in "h_limit h_diff3 h_integ3 h_complex h_conic".split(): CAT[u] = "math3c"

RATE = {1: 7.6, 2: 5.6, 3: 3.8, 4: 2.3}     # 10人中、1発で正解できそうな人数の見積もり（作成時）


# 教科書の例題・章末にのる種類は、最上級ではなく上級にする
DEMOTE = {"約数の総和", "けた数と最高位の数", "分散", "ω の性質", "根号を含む極限", "三角方程式の解の個数", "回転体の体積",
          "通れない点がある道順", "区分求積法", "絶対値を含む定積分", "ベクトルの大きさの最小値"}


def add(unit, diff, title, body, ans, expl, choices=None):
    if diff == 4 and title in DEMOTE: diff = 3
    key = (unit, body)
    if key in _seen: return False
    _seen.add(key)
    _count[unit] = _count.get(unit, 0) + 1
    plain = tex2plain(body)
    p = dict(id=f"x7-{unit}-{_count[unit]}", category=CAT[unit], difficulty=diff, title=title, body=body,
             answer=ans, explanation=expl, plain=plain, unit=unit, rate_hint=RATE[diff])
    if choices is not None:
        labels = ["①", "②", "③", "④"]
        p["choices"] = choices
        p["plain"] += "　" + "　".join(f"{labels[i]} {tex2plain(c)}" for i, c in enumerate(choices))
    else:
        assert isinstance(ans, int), (unit, body, ans)
    OUT.append(p)
    return True


def make(n, fn, tries=4000):
    made = 0
    for _ in range(tries):
        if made >= n: break
        if fn(): made += 1
    assert made >= max(1, n * 7 // 10), (fn.__name__, made, n)
    return made


def frac_tex(f):
    f = F(f)
    if f.denominator == 1: return str(f.numerator)
    s = "-" if f < 0 else ""
    return f"{s}\\dfrac{{{abs(f.numerator)}}}{{{f.denominator}}}"


def ab(f):
    """既約分数 a/b（正）の a + b。"""
    f = F(f)
    assert f > 0 and f.denominator > 1
    return f.numerator + f.denominator


def sg(n, first=False):
    if first: return str(n)
    return f"+ {n}" if n >= 0 else f"- {-n}"


def poly(terms):
    """[(係数, 'x^2'), ...] を、きれいな式に。"""
    s = ""
    for c, v in terms:
        if c == 0: continue
        if v == "":
            t = str(abs(c))
        else:
            t = ("" if abs(c) == 1 else str(abs(c))) + v
        if s == "":
            s = ("-" if c < 0 else "") + t
        else:
            s += (" - " if c < 0 else " + ") + t
    return s or "0"


# ═════════════════════════ 初級（1） ═════════════════════════
def e_frac_add():
    a, b = R.randint(1, 5), R.randint(2, 9); c, d = R.randint(1, 5), R.randint(2, 9)
    if a >= b or c >= d or b == d: return False
    s = F(a, b) + F(c, d)
    if s.denominator == 1 or s > 2: return False
    return add("e_decfrac", 1, "分数のたし算", f"$\\dfrac{{{a}}}{{{b}}} + \\dfrac{{{c}}}{{{d}}}$ を計算し、既約分数 $\\dfrac{{p}}{{q}}$ で表す。$p + q$ を答えよ。",
               ab(s), f"通分して $\\dfrac{{{a * d + c * b}}}{{{b * d}}} = {frac_tex(s)}$。$p + q = {ab(s)}$。")


def e_lcm_word():
    a, b = R.choice([(6, 8), (4, 6), (9, 12), (8, 12), (10, 15), (12, 18), (6, 10), (14, 21), (15, 20)])
    h = R.randint(8, 10)
    l = a * b // math.gcd(a, b)
    return add("e_divmult", 1, "同時に出発する問題", f"A 駅からは {a} 分ごと、B 駅からは {b} 分ごとにバスが出る。午前 {h} 時に同時に出たあと、次に同時に出るのは何分後か。",
               l, f"{a} と {b} の最小公倍数を求める。答えは {l} 分後。")


def e_ratio_share():
    a, b = R.randint(1, 7), R.randint(1, 7)
    if math.gcd(a, b) != 1 or a == b: return False
    t = (a + b) * R.randint(3, 40) * 10
    return add("e_ratio", 1, "比で分ける", f"{t} 円を、兄と弟で {a}:{b} に分ける。兄の分は何円か。", t * a // (a + b),
               f"兄の分は全体の $\\dfrac{{{a}}}{{{a + b}}}$。${t} \\times \\dfrac{{{a}}}{{{a + b}}} = {t * a // (a + b)}$ 円。")


def e_speed_meet():
    v1, v2 = R.choice([60, 70, 80, 90]), R.choice([40, 50, 60, 70])
    t = R.randint(5, 20)
    d = (v1 + v2) * t
    return add("e_speed", 1, "出会うまでの時間", f"{d} m はなれた 2 人が、分速 {v1} m と分速 {v2} m で向かい合って同時に歩きはじめた。何分後に出会うか。", t,
               f"1 分間に {v1 + v2} m ずつ近づく。${d} \\div {v1 + v2} = {t}$ 分後。")


def e_avg_missing():
    n = R.randint(4, 6)
    xs = [R.randint(50, 95) for _ in range(n - 1)]
    avg = R.randint(70, 85)
    last = avg * n - sum(xs)
    if not 40 <= last <= 100: return False
    return add("e_avg", 1, "平均から点数を求める", f"{n} 回のテストの平均点を {avg} 点にしたい。{n - 1} 回目までの点数は {'、'.join(map(str, xs))} 点だった。{n} 回目に何点とればよいか。",
               last, f"合計は ${avg} \\times {n} = {avg * n}$ 点必要。${avg * n} - {sum(xs)} = {last}$ 点。")


def m_lin_eq():
    a, c = R.randint(2, 9), R.randint(1, 9)
    if a == c: return False
    x = R.randint(-9, 9)
    b, d = R.randint(-15, 15), None
    d = a * x + b - c * x
    if b == 0 or d == 0: return False
    return add("m_linear", 1, "一次方程式", f"方程式 ${poly([(a, 'x'), (b, '')])} = {poly([(c, 'x'), (d, '')])}$ を解け。", x,
               f"${a - c}x = {d - b}$ より $x = {x}$。")


def m_signed_calc():
    a, b, c = R.randint(-9, 9), R.randint(2, 6), R.randint(-9, 9)
    if a == 0 or c == 0: return False
    v = a * b - c * c
    return add("m_signed", 1, "正負の数の計算", f"$({a}) \\times {b} - ({c})^2$ を計算せよ。", v,
               f"$({a}) \\times {b} = {a * b}$、$({c})^2 = {c * c}$。${a * b} - {c * c} = {v}$。")


def m_pythag_basic():
    a, b, c = R.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (6, 8, 10), (9, 12, 15), (20, 21, 29), (9, 40, 41)])
    return add("m_pythag", 1, "斜辺を求める", f"直角をはさむ 2 辺が {a} cm、{b} cm の直角三角形の斜辺は何 cm か。", c,
               f"$\\sqrt{{{a}^2 + {b}^2}} = \\sqrt{{{c * c}}} = {c}$。")


def m_prob_dice():
    s = R.randint(3, 11)
    w = sum(1 for i in range(1, 7) for j in range(1, 7) if i + j == s)
    p = F(w, 36)
    if p.denominator == 1: return False
    return add("m_prob", 1, "2 つのさいころの和", f"大小 2 つのさいころを投げるとき、目の和が {s} になる確率を既約分数 $\\dfrac{{a}}{{b}}$ で表す。$a + b$ を答えよ。",
               ab(p), f"和が {s} になるのは {w} 通り。$\\dfrac{{{w}}}{{36}} = {frac_tex(p)}$。")


def h_quadfunc_vertex():
    a = R.choice([1, 2, 3, -1, -2]); p, q = R.randint(-5, 5), R.randint(-9, 9)
    b, c = -2 * a * p, a * p * p + q
    return add("h_quadfunc", 1, "頂点の y 座標", f"放物線 $y = {poly([(a, 'x^2'), (b, 'x'), (c, '')])}$ の頂点の $y$ 座標を答えよ。", q,
               f"平方完成すると $y = {'' if a == 1 else ('-' if a == -1 else a)}(x {sg(-p)})^2 {sg(q)}$。頂点は $({p}, {q})$。")


def h_exp_log():
    b = R.choice([2, 3, 5]); m, n = R.randint(2, 6), R.randint(1, 4)
    v = b ** (m + n)
    return add("h_exp", 1, "対数の計算", f"$\\log_{{{b}}} {b ** m} + \\log_{{{b}}} {b ** n}$ の値を答えよ。", m + n,
               f"$\\log_{{{b}}} ({b ** m} \\times {b ** n}) = \\log_{{{b}}} {v} = {m + n}$。")


def h_diff_slope():
    a, b, c = R.randint(1, 3), R.randint(-6, 6), R.randint(-9, 9); t = R.randint(-3, 3)
    v = 3 * a * t * t + 2 * b * t + c
    return add("h_diff", 1, "接線の傾き", f"曲線 $y = {poly([(a, 'x^3'), (b, 'x^2'), (c, 'x')])}$ の $x = {t}$ における接線の傾きを答えよ。", v,
               f"$y' = {poly([(3 * a, 'x^2'), (2 * b, 'x'), (c, '')])}$。$x = {t}$ を代入して ${v}$。")


def h_seq_arith():
    a, d, n = R.randint(-10, 10), R.randint(2, 7), R.randint(10, 30)
    s = n * (2 * a + (n - 1) * d) // 2
    return add("h_seq", 1, "等差数列の和", f"初項 {a}、公差 {d} の等差数列の、初項から第 {n} 項までの和を答えよ。", s,
               f"$\\dfrac{{{n}\\{{2 \\cdot ({a}) + ({n} - 1) \\cdot {d}\\}}}}{{2}} = {s}$。")


def h_integ_basic():
    a, b = R.randint(1, 3), R.randint(-4, 4); u = R.randint(1, 3)
    v = a * u ** 3 + b * u * u
    return add("h_integ", 1, "定積分の計算", f"$\\displaystyle\\int_0^{{{u}}} ({poly([(3 * a, 'x^2'), (2 * b, 'x')])})\\,dx$ の値を答えよ。", v,
               f"原始関数は ${poly([(a, 'x^3'), (b, 'x^2')])}$。$x = {u}$ を代入して ${v}$。")


def h_count_basic():
    n, r = R.randint(5, 9), R.randint(2, 4)
    return add("h_count", 1, "組合せ", f"{n} 人の中から {r} 人の代表を選ぶ方法は何通りか。", math.comb(n, r),
               f"${{}}_{{{n}}}\\mathrm{{C}}_{{{r}}} = {math.comb(n, r)}$ 通り。")


def h_trig_value():
    deg, v = R.choice([(30, "\\dfrac{1}{2}"), (45, "\\dfrac{\\sqrt{2}}{2}"), (60, "\\dfrac{\\sqrt{3}}{2}"), (120, "\\dfrac{\\sqrt{3}}{2}"),
                       (135, "\\dfrac{\\sqrt{2}}{2}"), (150, "\\dfrac{1}{2}")])
    wrong = ["\\dfrac{1}{2}", "\\dfrac{\\sqrt{2}}{2}", "\\dfrac{\\sqrt{3}}{2}", "1", "\\dfrac{\\sqrt{3}}{3}"]
    ws = [w for w in wrong if w != v][:3]
    opts = [v] + ws; R.shuffle(opts)
    return add("h_trig", 1, "三角比の値", f"$\\sin {deg}^\\circ$ の値はどれか。", opts.index(v),
               f"$\\sin {deg}^\\circ = {v}$。", [f"${o}$" for o in opts])


# ═════════════════════════ 中級（2） ═════════════════════════
def e_work():
    a, b = R.choice([(6, 12), (10, 15), (12, 24), (20, 30), (6, 3), (15, 10), (18, 9), (12, 6), (30, 20)])
    t = a * b // (a + b) if a * b % (a + b) == 0 else None
    if t is None: return False
    return add("e_ratio", 2, "仕事算", f"ある仕事を、A さん 1 人では {a} 日、B さん 1 人では {b} 日で終える。2 人でいっしょにすると何日で終わるか。", t,
               f"1 日にする量は $\\dfrac{{1}}{{{a}}} + \\dfrac{{1}}{{{b}}} = \\dfrac{{1}}{{{t}}}$。{t} 日。")


def e_tsuru():
    n = R.randint(10, 30); c = R.randint(1, n - 1)
    legs = 4 * c + 2 * (n - c)
    return add("e_count", 2, "つるかめ算", f"つるとかめが合わせて {n} 匹いて、足の数は合わせて {legs} 本である。かめは何匹いるか。", c,
               f"全部つるなら足は {2 * n} 本。かめ 1 匹で 2 本ふえる。$({legs} - {2 * n}) \\div 2 = {c}$ 匹。")


def m_simul_word():
    a, b = R.randint(50, 150), R.randint(80, 200)
    if a == b: return False
    x, y = R.randint(2, 12), R.randint(2, 12)
    return add("m_simul_word", 2, "代金の連立方程式", f"1 個 {a} 円のりんごと 1 個 {b} 円のなしを合わせて {x + y} 個買ったら、代金は {a * x + b * y} 円だった。りんごは何個買ったか。", x,
               f"りんごを $x$ 個、なしを $y$ 個とすると $x + y = {x + y}$、${a}x + {b}y = {a * x + b * y}$。解くと $x = {x}$。")


def m_quad_int():
    p, q = R.randint(-9, 9), R.randint(-9, 9)
    if p == q or p == 0 or q == 0: return False
    b, c = -(p + q), p * q
    return add("m_quad", 2, "二次方程式の解の積", f"二次方程式 ${poly([(1, 'x^2'), (b, 'x'), (c, '')])} = 0$ の 2 つの解の積を答えよ。", c,
               f"$(x {sg(-p)})(x {sg(-q)}) = 0$ より解は ${p}$ と ${q}$。積は ${c}$。")


def m_func2_area():
    a = R.choice([1, 2]); p, q = R.randint(-4, -1), R.randint(1, 4)
    # y = a x^2 上の 2 点 A(p, ap^2), B(q, aq^2) と原点 O の三角形の面積
    s = F(abs(p * a * q * q - q * a * p * p), 2)
    if s.denominator != 1: return False
    return add("m_func2", 2, "放物線と三角形の面積", f"放物線 $y = {'' if a == 1 else a}x^2$ 上に、$x$ 座標が ${p}$ の点 A と ${q}$ の点 B がある。三角形 OAB の面積を答えよ（O は原点）。",
               int(s), f"A$({p}, {a * p * p})$、B$({q}, {a * q * q})$。面積は $\\dfrac{{1}}{{2}}|x_A y_B - x_B y_A| = {int(s)}$。")


def m_circle_angle():
    c = R.randint(20, 80)
    return add("m_circle", 2, "円周角と中心角", f"円 O で、弧 AB に対する円周角が ${c}^\\circ$ のとき、中心角 $\\angle$AOB は何度か。", 2 * c,
               f"中心角は円周角の 2 倍。${2 * c}^\\circ$。")


def m_data_median():
    n = R.choice([7, 8, 9, 10])
    xs = sorted(R.randint(1, 30) for _ in range(n))
    med = F(xs[n // 2] + xs[(n - 1) // 2], 2)
    if med.denominator != 1: return False
    ys = xs[:]; R.shuffle(ys)
    return add("m_data", 2, "中央値", f"次の {n} 個のデータの中央値を答えよ。　{', '.join(map(str, ys))}", int(med),
               f"小さい順に並べると {', '.join(map(str, xs))}。中央値は {int(med)}。")


def h_quadeq_disc():
    a, m = R.randint(1, 5), R.randint(1, 9)
    c = m * m * R.choice([1, 4]) // 1
    k2 = 4 * a * c
    k = math.isqrt(k2)
    if k * k != k2: return False
    return add("h_quadeq", 2, "重解をもつ条件", f"二次方程式 ${'' if a == 1 else a}x^2 + kx + {c} = 0$ が重解をもつような正の定数 $k$ を答えよ。", k,
               f"判別式 $D = k^2 - 4 \\cdot {a} \\cdot {c} = k^2 - {k2} = 0$ より $k = \\pm {k}$。正なので $k = {k}$。")


def h_trig_cos_rule():
    while True:
        a, b, c = R.randint(3, 15), R.randint(3, 15), R.randint(3, 15)
        if a + b > c and b + c > a and c + a > b: break
    cosA = F(b * b + c * c - a * a, 2 * b * c)
    if cosA.denominator == 1 or cosA <= 0: return False
    return add("h_trig", 2, "余弦定理", f"三角形 ABC で、BC = {a}、CA = {b}、AB = {c} のとき、$\\cos A$ を既約分数 $\\dfrac{{p}}{{q}}$ で表す。$p + q$ を答えよ。",
               ab(cosA), f"$\\cos A = \\dfrac{{{b}^2 + {c}^2 - {a}^2}}{{2 \\cdot {b} \\cdot {c}}} = {frac_tex(cosA)}$。")


def h_prob_draw():
    r, w = R.randint(2, 6), R.randint(2, 6); k = 2
    p = F(math.comb(r, 1) * math.comb(w, 1), math.comb(r + w, 2))
    if p.denominator == 1: return False
    return add("h_prob", 2, "色のちがう 2 個を取り出す確率", f"赤玉 {r} 個、白玉 {w} 個が入った袋から、同時に 2 個取り出す。赤と白が 1 個ずつになる確率を既約分数 $\\dfrac{{a}}{{b}}$ で表す。$a + b$ を答えよ。",
               ab(p), f"$\\dfrac{{{r} \\times {w}}}{{{{}}_{{{r + w}}}\\mathrm{{C}}_{{2}}}} = {frac_tex(p)}$。")


def h_nt_divisors():
    n = R.choice([2 ** a * 3 ** b * 5 ** c for a in range(1, 5) for b in range(0, 3) for c in range(0, 2)])
    d = sum(1 for k in range(1, n + 1) if n % k == 0)
    f = sp.factorint(n)
    fs = " \\times ".join(f"{p}^{{{e}}}" if e > 1 else str(p) for p, e in sorted(f.items()))
    return add("h_nt", 2, "約数の個数", f"{n} の正の約数は何個あるか。", d,
               f"${n} = {fs}$。約数の個数は {' × '.join(str(e + 1) for e in sorted(f.values()))} の積で {d} 個。".replace("の積で", "") if False else
               f"${n} = {fs}$ なので、約数の個数は $" + " \\times ".join(f"({e} + 1)" for p, e in sorted(f.items())) + f" = {d}$ 個。")


def h_exp_eq():
    b = R.choice([2, 3]); t = R.randint(1, 4); s = R.randint(1, 4)
    if t == s: return False
    # (b^x)^2 - (b^t + b^s) b^x + b^(t+s) = 0 の解の和 x = t + s
    return add("h_exp", 2, "指数方程式", f"方程式 ${b}^{{2x}} - {b ** t + b ** s} \\cdot {b}^x + {b ** (t + s)} = 0$ の 2 つの解の和を答えよ。", t + s,
               f"${b}^x = X$ とおくと $(X - {b ** t})(X - {b ** s}) = 0$。$x = {t}, {s}$ で、和は ${t + s}$。")


def h_seq_geo():
    a, r, n = R.randint(1, 5), R.choice([2, 3]), R.randint(4, 8)
    s = a * (r ** n - 1) // (r - 1)
    return add("h_seq", 2, "等比数列の和", f"初項 {a}、公比 {r} の等比数列の、初項から第 {n} 項までの和を答えよ。", s,
               f"$\\dfrac{{{a}({r}^{{{n}}} - 1)}}{{{r} - 1}} = {s}$。")


def h_vec_dot():
    a, b, c, d = [R.randint(-5, 5) for _ in range(4)]
    if (a, b) == (0, 0) or (c, d) == (0, 0): return False
    return add("h_vec", 2, "内積", f"$\\vec{{a}} = ({a}, {b})$、$\\vec{{b}} = ({c}, {d})$ のとき、内積 $\\vec{{a}} \\cdot \\vec{{b}}$ を答えよ。", a * c + b * d,
               f"${a} \\cdot ({c}) + ({b}) \\cdot ({d}) = {a * c + b * d}$。")


def h_circle_center():
    p, q, r = R.randint(-6, 6), R.randint(-6, 6), R.randint(1, 7)
    D, E, Fc = -2 * p, -2 * q, p * p + q * q - r * r
    if Fc == 0: return False
    return add("h_circle", 2, "円の半径", f"円 $x^2 + y^2 {sg(D)}x {sg(E)}y {sg(Fc)} = 0$ の半径を答えよ。".replace("+ 0x ", "").replace("+ 0y ", ""), r,
               f"$(x {sg(-p)})^2 + (y {sg(-q)})^2 = {r * r}$ と変形できる。半径は ${r}$。")


def h_limit_rational():
    a, b, c, d = R.randint(1, 6), R.randint(-5, 5), R.randint(1, 6), R.randint(-5, 5)
    q = F(a, c)
    if q.denominator != 1: return False
    return add("h_limit", 2, "数列の極限", f"$\\displaystyle\\lim_{{n \\to \\infty}} \\dfrac{{{poly([(a, 'n^2'), (b, 'n')])}}}{{{poly([(c, 'n^2'), (d, '')])}}}$ の値を答えよ。", int(q),
               f"分母と分子を $n^2$ で割ると、$\\dfrac{{{a}}}{{{c}}} = {int(q)}$ に近づく。")


def h_cplx_calc():
    a, b, c, d = [R.randint(-5, 5) for _ in range(4)]
    if 0 in (a, b, c, d): return False
    re = a * c - b * d
    return add("h_cplx", 2, "複素数の積", f"$({poly([(a, ''), (b, 'i')])})({poly([(c, ''), (d, 'i')])})$ の実部を答えよ。", re,
               f"$({a})({c}) - ({b})({d}) = {re}$（$i^2 = -1$）。")


def h_diff_extreme():
    p, q = R.randint(-4, 3), R.randint(-3, 4)
    if p >= q: return False
    # f'(x) = 3(x-p)(x-q)、f(x) = x^3 - 3/2 (p+q) x^2 + 3pq x + c
    if (p + q) % 2: return False
    c = R.randint(-5, 5)
    f = lambda t: t ** 3 - F(3, 2) * (p + q) * t * t + 3 * p * q * t + c
    v = f(p) - f(q)
    if v.denominator != 1: return False
    b = -3 * (p + q) // 2
    return add("h_diff2", 2, "極大値と極小値の差", f"関数 $f(x) = {poly([(1, 'x^3'), (b, 'x^2'), (3 * p * q, 'x'), (c, '')])}$ の極大値と極小値の差を答えよ。", int(v),
               f"$f'(x) = 3(x {sg(-p)})(x {sg(-q)})$。$x = {p}$ で極大、$x = {q}$ で極小。$f({p}) - f({q}) = {int(v)}$。")


# ═════════════════════════ 上級（3） ═════════════════════════
def e_clock():
    h = R.randint(1, 11); m = R.choice([0, 10, 20, 30, 40, 50])
    ang = abs(30 * h + F(m, 2) - 6 * m)
    ang = min(ang, 360 - ang)
    if ang.denominator != 1: return False
    return add("e_geom", 3, "時計の針の角度", f"{h} 時 {m} 分のとき、時計の長針と短針がつくる角のうち、小さいほうは何度か。", int(ang),
               f"短針は 1 分で $0.5^\\circ$、長針は $6^\\circ$ 進む。短針は ${float(30 * h + F(m, 2)):g}^\\circ$、長針は ${6 * m}^\\circ$ の位置。差は ${int(ang)}^\\circ$。")


def e_count_paths():
    a, b = R.randint(3, 6), R.randint(2, 5)
    return add("e_count", 3, "道順の数", f"縦の道と横の道が碁盤の目のようになった町で、右へ {a} 区画、上へ {b} 区画進んだ所へ、最短で行く道順は何通りか。", math.comb(a + b, a),
               f"右 {a} 回と上 {b} 回の並べ方なので ${{}}_{{{a + b}}}\\mathrm{{C}}_{{{a}}} = {math.comb(a + b, a)}$ 通り。")


def m_int_digits():
    n = R.randint(2, 5)
    cnt = sum(1 for k in range(10 ** (n - 1), 10 ** n) if k % 3 == 0 and k % 5 != 0) if n <= 4 else None
    if cnt is None: return False
    return add("m_int", 3, "条件を満たす整数の個数", f"{n} けたの正の整数のうち、3 の倍数であって 5 の倍数でないものは何個あるか。", cnt,
               f"3 の倍数の個数から、15 の倍数の個数を引く。答えは {cnt} 個。")


def m_space_cone():
    r, h = R.choice([(3, 4), (5, 12), (6, 8), (8, 15), (9, 12)])
    l = math.isqrt(r * r + h * h)
    s = r * r + r * l   # 表面積 / π
    return add("m_space", 3, "円錐の表面積", f"底面の半径が {r} cm、高さが {h} cm の円錐の表面積は $a\\pi$ cm² である。$a$ を答えよ。", s,
               f"母線は $\\sqrt{{{r}^2 + {h}^2}} = {l}$。底面 ${r * r}\\pi$、側面 $\\pi \\cdot {r} \\cdot {l} = {r * l}\\pi$。合計 ${s}\\pi$。")


def m_quad_word():
    w = R.randint(10, 30); h = R.randint(8, 25); x = R.randint(1, 4)
    area = (w - 2 * x) * (h - 2 * x)
    if area <= 0: return False
    other = F(w + h, 2) - x                      # もう 1 つの解が、条件に合ってしまう問題は作らない
    if 0 < other < F(min(w, h), 2): return False
    return add("m_quad_word", 3, "道はばの問題", f"縦 {h} m、横 {w} m の長方形の土地の周りに、同じはばの道をつくり、残りの土地の面積を {area} m² にしたい。道のはばは何 m か（道は土地の内側につくる）。", x,
               f"$({w} - 2x)({h} - 2x) = {area}$ を解く。$0 < x < {min(w, h) / 2:g}$ を満たすのは $x = {x}$。")


def h_count_circle():
    n = R.randint(5, 8)
    v = math.factorial(n - 2) * 2
    return add("h_count", 3, "円順列（となり合う）", f"{n} 人が円形のテーブルにすわる。特定の 2 人 A、B がとなり合うすわり方は何通りか。", v,
               f"A と B をひとまとめにして ${n - 1}$ 個の円順列 $({n - 2})!$ 通り。A、B の並び 2 通り。${v}$ 通り。")


def h_count_dist():
    n, k = R.randint(6, 12), R.randint(3, 4)
    v = math.comb(n - 1, k - 1)
    return add("h_count", 3, "重複組合せ（1 個以上）", f"同じ種類のりんご {n} 個を、A、B、C{'、D' if k == 4 else ''} の {k} 人に、どの人も 1 個以上もらうように配る方法は何通りか。", v,
               f"仕切りの考え方で ${{}}_{{{n - 1}}}\\mathrm{{C}}_{{{k - 1}}} = {v}$ 通り。")


def h_prob_cond():
    r1, w1, r2, w2 = R.randint(1, 5), R.randint(1, 5), R.randint(1, 5), R.randint(1, 5)
    pa = F(1, 2) * F(r1, r1 + w1); pb = F(1, 2) * F(r2, r2 + w2)
    p = pa / (pa + pb)
    if p.denominator == 1: return False
    return add("h_prob", 3, "条件つき確率", f"袋 A には赤玉 {r1} 個と白玉 {w1} 個、袋 B には赤玉 {r2} 個と白玉 {w2} 個が入っている。どちらかの袋を等しい確率で選び、1 個取り出したら赤玉だった。選んだ袋が A である確率を既約分数 $\\dfrac{{a}}{{b}}$ で表す。$a + b$ を答えよ。",
               ab(p), f"$\\dfrac{{\\frac12 \\cdot {frac_tex(F(r1, r1 + w1))}}}{{\\frac12 \\cdot {frac_tex(F(r1, r1 + w1))} + \\frac12 \\cdot {frac_tex(F(r2, r2 + w2))}}} = {frac_tex(p)}$。")


def h_nt_mod():
    a, n, m = R.randint(2, 9), R.randint(50, 200), R.choice([7, 9, 11, 13])
    if math.gcd(a, m) != 1: return False
    v = pow(a, n, m)
    return add("h_nt", 3, "累乗の余り", f"${a}^{{{n}}}$ を {m} で割った余りを答えよ。", v,
               f"${a}$ の累乗を {m} で割った余りは周期的にくり返す。周期を使うと、余りは ${v}$。")


def h_nt_diophantine():
    a, b = R.randint(3, 13), R.randint(3, 13)
    if math.gcd(a, b) != 1: return False
    c = R.randint(60, 200)
    cnt = sum(1 for x in range(1, c) for y in range(1, c) if a * x + b * y == c)
    if cnt == 0: return False
    return add("h_nt", 3, "不定方程式の解の個数", f"${a}x + {b}y = {c}$ を満たす正の整数の組 $(x, y)$ は何組あるか。", cnt,
               f"1 組の解を見つけ、一般解 $x = x_0 + {b}t$、$y = y_0 - {a}t$ で正の範囲に入るものを数えると {cnt} 組。")


def h_seq_rec():
    p, q, a1, n = R.choice([2, 3]), R.randint(1, 5), R.randint(1, 4), R.randint(5, 8)
    a = a1
    for _ in range(n - 1): a = p * a + q
    return add("h_seq2", 3, "漸化式", f"$a_1 = {a1}$、$a_{{n+1}} = {p}a_n + {q}$ で定まる数列の $a_{{{n}}}$ を答えよ。", a,
               f"$a_{{n+1}} + {frac_tex(F(q, p - 1))} = {p}(a_n + {frac_tex(F(q, p - 1))})$ と変形できる。順に求めても $a_{{{n}}} = {a}$。")


def h_seq_sigma():
    n = R.randint(5, 15); a, b = R.randint(1, 3), R.randint(-3, 3)
    v = sum(k * (a * k + b) for k in range(1, n + 1))
    return add("h_seq", 3, "Σ の計算", f"$\\displaystyle\\sum_{{k=1}}^{{{n}}} k({poly([(a, 'k'), (b, '')])})$ の値を答えよ。", v,
               f"$\\sum k^2 = \\dfrac{{n(n+1)(2n+1)}}{{6}}$、$\\sum k = \\dfrac{{n(n+1)}}{{2}}$ を使う。答えは ${v}$。")


def h_integ_area():
    a, b = R.randint(-4, 0), R.randint(1, 4)
    # y = (x-a)(x-b) と x 軸で囲まれた面積 = (b-a)^3/6
    s = F((b - a) ** 3, 6)
    if s.denominator == 1: return False
    return add("h_integ_app", 3, "放物線と x 軸で囲む面積", f"放物線 $y = {poly([(1, 'x^2'), (-(a + b), 'x'), (a * b, '')])}$ と $x$ 軸で囲まれた部分の面積を既約分数 $\\dfrac{{p}}{{q}}$ で表す。$p + q$ を答えよ。",
               ab(s), f"$x$ 軸との交点は $x = {a}, {b}$。面積は $\\dfrac{{({b} - ({a}))^3}}{{6}} = {frac_tex(s)}$。")


def h_vec_area():
    pts = [(R.randint(-4, 4), R.randint(-4, 4), R.randint(-4, 4)) for _ in range(3)]
    A, B, C = [sp.Matrix(p) for p in pts]
    cr = (B - A).cross(C - A)
    s2 = int(cr.dot(cr))
    if s2 == 0: return False
    v = F(s2, 4)
    if v.denominator != 1: return False
    return add("h_space", 3, "空間の三角形の面積", f"空間の 3 点 A{pts[0]}、B{pts[1]}、C{pts[2]} を頂点とする三角形の面積を $S$ とする。$S^2$ を答えよ。".replace("(", "(").replace(")", ")"),
               int(v), f"$S = \\dfrac{{1}}{{2}}\\sqrt{{|\\vec{{AB}}|^2|\\vec{{AC}}|^2 - (\\vec{{AB}} \\cdot \\vec{{AC}})^2}}$。計算すると $S^2 = {int(v)}$。")


def h_addition_tan():
    a, b = R.randint(1, 5), R.randint(1, 5)
    t = F(a + b, 1)  # tan(α+β) with tanα=1/a… 使わない
    p, q = F(1, a + 1), F(1, b + 2)
    t = (p + q) / (1 - p * q)
    if t.denominator == 1: return False
    return add("h_addition", 3, "tan の加法定理", f"$\\tan\\alpha = {frac_tex(p)}$、$\\tan\\beta = {frac_tex(q)}$ のとき、$\\tan(\\alpha + \\beta)$ を既約分数 $\\dfrac{{a}}{{b}}$ で表す。$a + b$ を答えよ。",
               ab(t), f"$\\dfrac{{{frac_tex(p)} + {frac_tex(q)}}}{{1 - {frac_tex(p)} \\cdot {frac_tex(q)}}} = {frac_tex(t)}$。")


def h_binom_coef():
    a, b, n = R.randint(1, 3), R.randint(1, 3), R.randint(5, 8); k = R.randint(2, n - 2)
    v = math.comb(n, k) * a ** k * b ** (n - k)
    return add("h_binom", 3, "二項展開の係数", f"$({'' if a == 1 else a}x + {b})^{{{n}}}$ を展開したときの $x^{{{k}}}$ の係数を答えよ。", v,
               f"${{}}_{{{n}}}\\mathrm{{C}}_{{{k}}} \\cdot {a}^{{{k}}} \\cdot {b}^{{{n - k}}} = {v}$。")


def h_conic_ellipse():
    a, b = R.randint(3, 9), R.randint(2, 8)
    if a <= b: return False
    c2 = a * a - b * b
    return add("h_conic", 3, "楕円の焦点", f"楕円 $\\dfrac{{x^2}}{{{a * a}}} + \\dfrac{{y^2}}{{{b * b}}} = 1$ の焦点を $(\\pm c, 0)$ とする。$c^2$ を答えよ。", c2,
               f"$c^2 = {a * a} - {b * b} = {c2}$。")


def h_complex_pow():
    a, b, n = R.choice([(1, 1), (1, -1), (-1, 1)]), None, R.randint(4, 12)
    z = sp.expand((a[0] + a[1] * sp.I) ** n)
    re = int(sp.re(z))
    return add("h_complex", 3, "複素数の累乗", f"$({a[0]} {sg(a[1])}i)^{{{n}}}$ の実部を答えよ。".replace("(1 + 1i)", "(1 + i)").replace("(1 - 1i)", "(1 - i)").replace("(-1 + 1i)", "(-1 + i)"),
               re, f"極形式 $\\sqrt{{2}}(\\cos\\theta + i\\sin\\theta)$ にして、ド・モアブルの定理を使う。実部は ${re}$。")


def h_diff3_max():
    k = R.randint(1, 4)
    # y = x^k e^{-x} (x>0) の最大値は x = k で k^k e^{-k}
    choices = [f"$\\dfrac{{{k ** k}}}{{e^{{{k}}}}}$", f"$\\dfrac{{{k}}}{{e}}$", f"$\\dfrac{{1}}{{e^{{{k}}}}}$", f"${k}e^{{{k}}}$"]
    if len(set(choices)) < 4: return False
    opts = choices[:]; R.shuffle(opts)
    return add("h_diff3", 3, "いろいろな関数の最大値", f"$x > 0$ における関数 $y = x^{{{k}}}e^{{-x}}$ の最大値はどれか。".replace("x^{1}", "x"), opts.index(choices[0]),
               f"$y' = x^{{{k - 1}}}e^{{-x}}({k} - x)$。$x = {k}$ で最大になり、値は ${k}^{{{k}}}e^{{-{k}}}$。", opts)


def h_integ3_parts():
    n = R.randint(1, 3)
    v = sp.integrate(sp.Symbol("x") ** n * sp.exp(sp.Symbol("x")), (sp.Symbol("x"), 0, 1))
    v = sp.nsimplify(v)
    # a e + b の形
    e = sp.E
    a_ = sp.simplify(sp.diff(v, e)) if False else None
    poly_ = sp.Poly(sp.expand(v).subs(sp.E, sp.Symbol("E")), sp.Symbol("E"))
    coeffs = poly_.all_coeffs()
    A, B = (int(coeffs[0]), int(coeffs[1])) if len(coeffs) == 2 else (0, int(coeffs[0]))
    return add("h_integ3", 3, "部分積分", f"$\\displaystyle\\int_0^1 x^{{{n}}}e^x\\,dx = ae + b$（$a$、$b$ は整数）のとき、$a + b$ を答えよ。".replace("x^{1}", "x"), A + B,
               f"部分積分をくり返すと、$ {A}e {sg(B)}$。$a + b = {A + B}$。")


# ═════════════════════════ 最上級（4） ═════════════════════════
def x_lattice_disc():
    r2 = R.randint(10, 60)
    cnt = sum(1 for x in range(-8, 9) for y in range(-8, 9) if x * x + y * y <= r2)
    return add("h_circle", 4, "円の内部の格子点", f"不等式 $x^2 + y^2 \\le {r2}$ を満たす整数の組 $(x, y)$ は何組あるか。", cnt,
               f"$x = 0, \\pm1, \\pm2, \\dots$ ごとに、$y^2 \\le {r2} - x^2$ を満たす整数 $y$ を数えて足す。{cnt} 組。")


def x_dice_max_min():
    k = R.randint(2, 4)
    tot = 6 ** 3
    w = sum(1 for t in itertools.product(range(1, 7), repeat=3) if max(t) - min(t) == k)
    p = F(w, tot)
    return add("h_prob", 4, "最大と最小の差の確率", f"さいころを 3 回投げる。出た目の最大値と最小値の差がちょうど {k} になる確率を既約分数 $\\dfrac{{a}}{{b}}$ で表す。$a + b$ を答えよ。",
               ab(p), f"最小値を $m$ とすると、目はすべて $m$ 以上 $m + {k}$ 以下で、$m$ と $m + {k}$ を両方含む。各 $m$ で $({k}+1)^3 - 2{k}^3 + ({k}-1)^3$ 通り。合計 {w} 通りで、${frac_tex(p)}$。")


def x_dice_prod():
    m = R.choice([4, 6, 8, 9, 12])
    n = R.choice([2, 3])
    w = sum(1 for t in itertools.product(range(1, 7), repeat=n) if math.prod(t) % m == 0)
    p = F(w, 6 ** n)
    if p.denominator == 1: return False
    return add("h_prob", 4, "目の積が倍数になる確率", f"さいころを {n} 回投げる。出た目の積が {m} の倍数になる確率を既約分数 $\\dfrac{{a}}{{b}}$ で表す。$a + b$ を答えよ。",
               ab(p), f"{m} を素因数分解し、積に必要な素因数がそろう場合を、余事象も使って数える。{w} 通りで、${frac_tex(p)}$。")


def x_mod_last2():
    a, n = R.choice([3, 7, 13, 17, 19, 23]), R.randint(100, 2030)
    v = pow(a, n, 100)
    return add("h_nt", 4, "累乗の下 2 けた", f"${a}^{{{n}}}$ を 100 で割った余りを答えよ。", v,
               f"${a}$ の累乗を 100 で割った余りの周期を調べる（$\\bmod 4$ と $\\bmod 25$ に分けてもよい）。余りは ${v}$。")


def x_divisor_sum():
    n = R.choice([2 ** a * 3 ** b * 7 ** c for a in range(1, 6) for b in range(0, 4) for c in range(0, 2)])
    if n > 3000: return False
    s = sum(k for k in range(1, n + 1) if n % k == 0)
    f = sp.factorint(n)
    fs = " \\times ".join(f"{p}^{{{e}}}" if e > 1 else str(p) for p, e in sorted(f.items()))
    return add("h_nt", 4, "約数の総和", f"{n} の正の約数すべての和を答えよ。", s,
               f"${n} = {fs}$。約数の和は、素因数ごとの $(1 + p + p^2 + \\cdots)$ の積で ${s}$。")


def x_count_subset_mod():
    n, m = R.randint(6, 10), R.choice([3, 4, 5])
    cnt = sum(1 for k in range(n + 1) for c in itertools.combinations(range(1, n + 1), k) if sum(c) % m == 0 and k > 0)
    return add("h_count", 4, "和が倍数になる部分集合", f"集合 $\\{{1, 2, \\dots, {n}\\}}$ の空でない部分集合のうち、要素の和が {m} の倍数になるものは何個あるか。", cnt,
               f"各要素を {m} で割った余りで分類し、余りの和が 0 になる選び方を数える。{cnt} 個。")


def x_surj():
    n, k = R.randint(5, 7), R.randint(3, 4)
    v = sum((-1) ** j * math.comb(k, j) * (k - j) ** n for j in range(k + 1))
    return add("h_count", 4, "どの部屋も空にしない分け方", f"区別のある {n} 人を、区別のある {k} つの部屋に入れる。どの部屋も 1 人以上になる入れ方は何通りか。", v,
               f"包除原理：$" + " ".join(f"{'+' if j % 2 == 0 and j > 0 else ('-' if j % 2 else '')} {{}}_{{{k}}}\\mathrm{{C}}_{{{j}}} \\cdot {k - j}^{{{n}}}" for j in range(k)) + f" = {v}$ 通り。")


def x_grid_avoid():
    a, b = R.randint(4, 6), R.randint(3, 5)
    p, q = R.randint(1, a - 1), R.randint(1, b - 1)
    v = math.comb(a + b, a) - math.comb(p + q, p) * math.comb(a - p + b - q, a - p)
    return add("h_count", 4, "通れない点がある道順", f"碁盤の目の道を、点 $(0, 0)$ から点 $({a}, {b})$ まで、右か上に 1 区画ずつ進んで最短で行く。点 $({p}, {q})$ は工事中で通れない。道順は何通りか。", v,
               f"全体 ${{}}_{{{a + b}}}\\mathrm{{C}}_{{{a}}}$ から、$({p}, {q})$ を通る ${{}}_{{{p + q}}}\\mathrm{{C}}_{{{p}}} \\times {{}}_{{{a + b - p - q}}}\\mathrm{{C}}_{{{a - p}}}$ を引いて {v} 通り。")


def x_rec_n():
    p, q, r, a1, N = R.choice([2, 3]), R.randint(1, 3), R.randint(-2, 3), R.randint(1, 3), R.randint(6, 9)
    a = a1
    for n in range(1, N): a = p * a + q * n + r
    return add("h_seq2", 4, "n を含む漸化式", f"$a_1 = {a1}$、$a_{{n+1}} = {p}a_n + {poly([(q, 'n'), (r, '')])}$ で定まる数列の $a_{{{N}}}$ を答えよ。", a,
               f"$a_n + \\alpha n + \\beta$ が等比数列になるように $\\alpha$、$\\beta$ を決めるか、順に計算する。$a_{{{N}}} = {a}$。")


def x_floor_sum():
    n, m = R.randint(10, 30), R.randint(3, 7)
    v = sum(k * k // m for k in range(1, n + 1))
    return add("h_seq", 4, "ガウス記号の和", f"$\\displaystyle\\sum_{{k=1}}^{{{n}}} \\left[ \\dfrac{{k^2}}{{{m}}} \\right]$ の値を答えよ（$[x]$ は $x$ を超えない最大の整数）。", v,
               f"$k^2$ を {m} で割った余りは周期 {m} でくり返すので、$\\dfrac{{1}}{{{m}}}(\\sum k^2 - \\sum (\\text{{余り}}))$ で求まる。答えは ${v}$。")


def x_tangent_area():
    # y = x^3 - a x と、x = t での接線で囲む面積 = 27 t^4 / 4
    t = R.choice([1, 2, F(1, 2), F(2, 3), F(3, 2)])
    a = R.randint(0, 4)
    s = F(27, 4) * F(t) ** 4
    if s.denominator == 1: return False
    return add("h_integ_app", 4, "曲線と接線で囲む面積", f"曲線 $y = {poly([(1, 'x^3'), (-a, 'x')])}$ 上の点 $x = {frac_tex(t)}$ における接線と、この曲線で囲まれた部分の面積を既約分数 $\\dfrac{{p}}{{q}}$ で表す。$p + q$ を答えよ。",
               ab(s), f"接線ともう一度交わる点は $x = -2 \\cdot {frac_tex(t)}$。面積は $\\displaystyle\\int (x - t)^2(x + 2t)\\,dx = \\dfrac{{27}}{{4}}t^4 = {frac_tex(s)}$。")


def x_abs_integral():
    a, b = R.randint(1, 4), R.randint(2, 6)
    X = sp.Symbol("x")
    g = X * X - a * X
    m = min(a, b)
    v = -sp.integrate(g, (X, 0, m)) + (sp.integrate(g, (X, a, b)) if b > a else 0)
    v = F(str(sp.nsimplify(v)))
    if v.denominator == 1: return False
    return add("h_integ", 4, "絶対値を含む定積分", f"$\\displaystyle\\int_0^{{{b}}} |x^2 - {a}x|\\,dx$ の値を既約分数 $\\dfrac{{p}}{{q}}$ で表す。$p + q$ を答えよ。".replace(" 1x", " x"),
               ab(v), f"$0 \\le x \\le {min(a, b)}$ では $-(x^2 - {a}x)$、${a} \\le x$ では $x^2 - {a}x$ に分けて積分する。答えは ${frac_tex(v)}$。".replace(" 1x", " x"))


def x_cubic_roots_k():
    a = R.randint(1, 4) * 3
    # x^3 - a x + k = 0 が異なる3つの実数解 ⇔ |k| < 2 (a/3)^{3/2}
    m = sp.Rational(a, 3)
    bound = 2 * m * sp.sqrt(m)
    cnt = sum(1 for k in range(-200, 201) if abs(k) < bound)
    return add("h_diff2", 4, "異なる 3 つの実数解をもつ整数", f"方程式 $x^3 - {a}x + k = 0$ が異なる 3 つの実数解をもつような整数 $k$ は何個あるか。", cnt,
               f"$f(x) = x^3 - {a}x$ の極大値と極小値は $\\pm 2\\left(\\dfrac{{{a}}}{{3}}\\right)^{{3/2}}$。$-k$ がその間にある整数を数えて {cnt} 個。")


def x_quad_two_pos():
    c = R.randint(2, 12)
    # x^2 - 2kx + k + c = 0 が異なる 2 つの正の解 ⇔ k^2 - k - c > 0, k > 0, k + c > 0
    ks = [k for k in range(-50, 51) if k * k - k - c > 0 and k > 0 and k + c > 0 and k <= 20]
    if not ks: return False
    return add("h_quadeq", 4, "解の配置", f"二次方程式 $x^2 - 2kx + k + {c} = 0$ が異なる 2 つの正の解をもつような整数 $k$ のうち、最小のものを答えよ。", min(ks),
               f"判別式 $k^2 - k - {c} > 0$、解の和 $2k > 0$、積 $k + {c} > 0$ をすべて満たす最小の整数は ${min(ks)}$。")


def x_abs_ineq():
    a, b, c = R.randint(-6, 0), R.randint(1, 7), R.randint(9, 20)
    cnt = sum(1 for x in range(-100, 101) if abs(x - a) + abs(x - b) <= c)
    return add("h_abs", 4, "絶対値の和の不等式", f"不等式 $|x {sg(-a)}| + |x {sg(-b)}| \\le {c}$ を満たす整数 $x$ は何個あるか。", cnt,
               f"$x$ の範囲で場合分けすると、解は ${frac_tex(F(a + b - c, 2))} \\le x \\le {frac_tex(F(a + b + c, 2))}$。整数は {cnt} 個。".replace("/", "/"))


def x_vec_min():
    a, b, c, d = R.randint(-4, 4), R.randint(-4, 4), R.randint(-4, 4), R.randint(-4, 4)
    if (c, d) == (0, 0): return False
    # |a + t b|^2 の最小値
    A, B = sp.Matrix([a, b]), sp.Matrix([c, d])
    t = sp.Symbol("t")
    f = (A + t * B).dot(A + t * B)
    v = sp.simplify(f.subs(t, sp.solve(sp.diff(f, t), t)[0]))
    v = F(str(v))
    if v.denominator == 1 or v == 0: return False
    return add("h_vec", 4, "ベクトルの大きさの最小値", f"$\\vec{{a}} = ({a}, {b})$、$\\vec{{b}} = ({c}, {d})$ とする。実数 $t$ を動かすとき、$|\\vec{{a}} + t\\vec{{b}}|^2$ の最小値を既約分数 $\\dfrac{{p}}{{q}}$ で表す。$p + q$ を答えよ。",
               ab(v), f"$|\\vec{{a}} + t\\vec{{b}}|^2$ は $t$ の二次式。平方完成すると最小値は ${frac_tex(v)}$。")


def x_tetra_volume():
    pts = [(0, 0, 0)] + [(R.randint(-3, 4), R.randint(-3, 4), R.randint(-3, 4)) for _ in range(3)]
    M = sp.Matrix([list(p) for p in pts[1:]])
    v = F(abs(int(M.det())), 6)
    if v == 0 or v.denominator == 1: return False
    return add("h_space", 4, "四面体の体積", f"空間の 4 点 O(0, 0, 0)、A{pts[1]}、B{pts[2]}、C{pts[3]} を頂点とする四面体の体積を既約分数 $\\dfrac{{p}}{{q}}$ で表す。$p + q$ を答えよ。",
               ab(v), f"体積は $\\dfrac{{1}}{{6}}|\\det(\\vec{{OA}}, \\vec{{OB}}, \\vec{{OC}})|$ で、${frac_tex(v)}$。")


def x_riemann():
    a, b = R.randint(1, 3), R.randint(1, 3)
    # lim (1/n) Σ (k/n)^a (1 + k/n)^... 単純に ∫0^1 x^a (b + x) dx
    X = sp.Symbol("x")
    v = F(str(sp.integrate(X ** a * (b + X), (X, 0, 1))))
    if v.denominator == 1: return False
    return add("h_limit", 4, "区分求積法", f"$\\displaystyle\\lim_{{n \\to \\infty}} \\dfrac{{1}}{{n}}\\sum_{{k=1}}^{{n}} \\left(\\dfrac{{k}}{{n}}\\right)^{{{a}}}\\left({b} + \\dfrac{{k}}{{n}}\\right)$ を既約分数 $\\dfrac{{p}}{{q}}$ で表す。$p + q$ を答えよ。".replace("^{1}", ""),
               ab(v), f"区分求積法で $\\displaystyle\\int_0^1 x^{{{a}}}({b} + x)\\,dx = {frac_tex(v)}$。".replace("^{1}", ""))


def x_rotation_volume():
    a = R.randint(1, 4)
    # y = x(a - x) と x 軸で囲む部分を x 軸のまわりに回転: π a^5 / 30
    v = F(a ** 5, 30)
    if v.denominator == 1: return False
    return add("h_integ3", 4, "回転体の体積", f"放物線 $y = x({a} - x)$ と $x$ 軸で囲まれた部分を、$x$ 軸のまわりに 1 回転させてできる立体の体積は $V\\pi$ である。$V$ を既約分数 $\\dfrac{{p}}{{q}}$ で表したとき、$p + q$ を答えよ。".replace("x(1 - x)", "x(1 - x)"),
               ab(v), f"$V = \\displaystyle\\int_0^{{{a}}} x^2({a} - x)^2\\,dx = \\dfrac{{{a}^5}}{{30}} = {frac_tex(v)}$。")


def x_complex_sum():
    n = R.choice([5, 6, 7, 8, 9, 10, 12]); form = R.randint(0, 2)
    w = f"$\\omega = \\cos\\dfrac{{2\\pi}}{{{n}}} + i\\sin\\dfrac{{2\\pi}}{{{n}}}$ とする。"
    if form == 0:
        return add("h_complex", 4, "1 の n 乗根の和", w + f"$\\displaystyle\\sum_{{j=0}}^{{{n - 1}}} |1 - \\omega^j|^2$ の値を答えよ。", 2 * n,
                   f"$|1 - \\omega^j|^2 = 2 - (\\omega^j + \\overline{{\\omega^j}})$。$\\sum \\omega^j = 0$ なので、和は $2 \\times {n} = {2 * n}$。")
    if form == 1:
        return add("h_complex", 4, "1 の n 乗根の積", w + f"$\\displaystyle\\prod_{{j=1}}^{{{n - 1}}} (1 - \\omega^j)$ の値を答えよ。", n,
                   f"$x^{{{n}}} - 1 = (x - 1)\\prod (x - \\omega^j)$ より $\\prod (x - \\omega^j) = 1 + x + \\cdots + x^{{{n - 1}}}$。$x = 1$ を代入して ${n}$。")
    vals = [sp.exp(2 * sp.pi * sp.I * j / n) for j in range(n)]
    v = sp.nsimplify(sp.simplify(sum((2 - v_ - 1 / v_) ** 2 for v_ in vals)))
    v = int(v); assert v == 6 * n
    return add("h_complex", 4, "1 の n 乗根の和（2 乗）", w + f"$\\displaystyle\\sum_{{j=0}}^{{{n - 1}}} |1 - \\omega^j|^4$ の値を答えよ。", v,
               f"$|1 - \\omega^j|^2 = 2 - \\omega^j - \\omega^{{-j}}$。2 乗して展開し、$\\sum \\omega^{{j}} = \\sum \\omega^{{2j}} = 0$ を使うと $6 \\times {n} = {v}$。")


def x_complex_poly():
    n = R.randint(5, 30)
    w = sp.exp(2 * sp.pi * sp.I / 3)
    v = sp.nsimplify(sp.simplify(sp.expand_complex(w ** n + w ** (2 * n) + 1)))
    v = int(v)
    return add("h_cplx", 4, "ω の性質", f"$\\omega$ を $x^2 + x + 1 = 0$ の解の 1 つとする。$\\omega^{{{2 * n}}} + \\omega^{{{n}}} + 1$ の値を答えよ。", v,
               f"$\\omega^3 = 1$ より、{n} を 3 で割った余りで決まる。{n} が 3 の倍数なら 3、そうでなければ 0。答えは ${v}$。")


def x_log_digits():
    b, n = R.choice([2, 3, 7]), R.randint(30, 120)
    d = len(str(b ** n))
    logs = {2: "0.3010", 3: "0.4771", 7: "0.8451"}
    if int(n * float(logs[b])) + 1 != d: return False      # 近似値で、けた数が変わってしまうものは作らない
    return add("h_exp", 4, "けた数と最高位の数", f"${b}^{{{n}}}$ は何けたの数か（$\\log_{{10}} {b} = {logs[b]}$ とする）。", d,
               f"$\\log_{{10}} {b}^{{{n}}} = {n} \\times {logs[b]}$。この整数部分に 1 を足して {d} けた。")


def x_stat_var():
    n = R.choice([5, 6, 8])
    xs = [R.randint(1, 15) for _ in range(n)]
    m = F(sum(xs), n)
    v = sum((F(x) - m) ** 2 for x in xs) / n
    if v.denominator != 1 or m.denominator != 1: return False
    return add("h_stat", 4, "分散", f"次の {n} 個のデータの分散を答えよ。　{', '.join(map(str, xs))}", int(v),
               f"平均は ${int(m)}$。偏差の 2 乗の平均を計算して、分散は ${int(v)}$。")


def x_geom_inscribed():
    while True:
        a, b, c = R.randint(5, 20), R.randint(5, 20), R.randint(5, 20)
        if a + b > c and b + c > a and a + c > b: break
    s = F(a + b + c, 2)
    S2 = s * (s - a) * (s - b) * (s - c)
    S = math.isqrt(int(S2)) if S2.denominator == 1 else None
    if S is None or S * S != S2: return False
    r = F(S) / s
    if r.denominator != 1: return False
    return add("h_geom", 4, "内接円の半径", f"3 辺の長さが {a}、{b}、{c} の三角形の内接円の半径を答えよ。", int(r),
               f"ヘロンの公式で面積は ${S}$。$S = rs$（$s$ は 3 辺の和の半分 ${s}$）より $r = {int(r)}$。")


def x_circum_r():
    while True:
        a, b, c = R.randint(5, 20), R.randint(5, 20), R.randint(5, 20)
        if a + b > c and b + c > a and a + c > b: break
    s = F(a + b + c, 2)
    S2 = s * (s - a) * (s - b) * (s - c)
    R2 = F(a * a * b * b * c * c) / (16 * S2)
    if R2.denominator != 1: return False
    return add("h_trig", 4, "外接円の半径", f"3 辺の長さが {a}、{b}、{c} の三角形の外接円の半径を $R$ とする。$R^2$ を答えよ。", int(R2),
               f"$R = \\dfrac{{abc}}{{4S}}$。ヘロンの公式で $S^2 = {frac_tex(S2)}$。これを使って $R^2 = \\dfrac{{a^2b^2c^2}}{{16S^2}} = {int(R2)}$。")


def x_trig_count():
    a = R.randint(2, 6); c = R.choice([F(1, 2), F(-1, 2), F(0), F(1), F(-1)])
    cnt = 2 * a if abs(c) < 1 else a
    k = R.randint(1, 3)
    # 0 ≤ x < 2π で sin(a x) = c、ただし k π ≤ … にはしない（シンプルに）
    return add("h_trig2", 4, "三角方程式の解の個数", f"$0 \\le x < 2\\pi$ で、方程式 $\\sin {a}x = {frac_tex(c)}$ の解は何個あるか。", cnt,
               f"${a}x = \\theta$ とおくと $0 \\le \\theta < {2 * a}\\pi$。$\\sin\\theta = {frac_tex(c)}$ の解は 1 周期に {2 if abs(c) < 1 else 1} 個あるので、全部で {cnt} 個。")


def x_lim_sqrt():
    a = R.randint(1, 9) * 2; b = R.randint(1, 9)
    v = F(a, 2)
    return add("h_limit", 4, "根号を含む極限", f"$\\displaystyle\\lim_{{n \\to \\infty}} \\left(\\sqrt{{n^2 + {a}n + {b}}} - n\\right)$ の値を答えよ。", int(v),
               f"分子を有理化すると $\\dfrac{{{a}n + {b}}}{{\\sqrt{{n^2 + {a}n + {b}}} + n}} \\to \\dfrac{{{a}}}{{2}} = {int(v)}$。")


def x_max_on_interval():
    a = R.randint(1, 6)
    X = sp.Symbol("x")
    f = X ** 3 - 3 * a * X
    lo, hi = R.randint(-4, 0), R.randint(1, 5)
    vals = [f.subs(X, t) for t in [lo, hi] + [s for s in sp.solve(sp.diff(f, X), X) if s.is_real and lo <= s <= hi]]
    m = max(vals)
    if not m.is_integer: return False
    return add("h_diff2", 4, "区間での最大値", f"${lo} \\le x \\le {hi}$ における関数 $f(x) = x^3 - {3 * a}x$ の最大値を答えよ。", int(m),
               f"$f'(x) = 3(x^2 - {a})$。極値と区間の端の値をくらべる。最大値は ${int(m)}$。")


def x_coef_trinom():
    n, k = R.randint(4, 8), R.randint(3, 8)
    X = sp.Symbol("x")
    c = sp.Poly(sp.expand((1 + X + X ** 2) ** n), X).coeff_monomial(X ** k)
    return add("h_binom", 4, "3 項の展開の係数", f"$(1 + x + x^2)^{{{n}}}$ を展開したときの $x^{{{k}}}$ の係数を答えよ。", int(c),
               f"$x^2$ を $a$ 個、$x$ を $b$ 個選び $2a + b = {k}$ となる組ごとに $\\dfrac{{{n}!}}{{a!\\,b!\\,({n}-a-b)!}}$ を足す。答えは ${int(c)}$。")


def x_parabola_dist():
    # 点 (0, a) と放物線 y = x^2 の距離の最小値の 2 乗
    a = F(R.randint(1, 8), R.choice([1, 2]))
    X = sp.Symbol("x", real=True)
    f = X ** 2 + (X ** 2 - sp.Rational(a.numerator, a.denominator)) ** 2
    cands = [0] + [s for s in sp.solve(sp.diff(f, X), X) if s.is_real]
    v = min(sp.nsimplify(f.subs(X, s)) for s in cands)
    v = F(str(v))
    if v.denominator == 1: return False
    return add("h_quadfunc", 4, "放物線との距離の最小値", f"点 $\\left(0, {frac_tex(a)}\\right)$ と放物線 $y = x^2$ 上の点の距離の最小値を $d$ とする。$d^2$ を既約分数 $\\dfrac{{p}}{{q}}$ で表したとき、$p + q$ を答えよ。",
               ab(v), f"放物線上の点 $(t, t^2)$ との距離の 2 乗は $t^2 + (t^2 - {frac_tex(a)})^2$。$t^2 = u$ とおいて $u \\ge 0$ で最小にすると ${frac_tex(v)}$。")


# ── 最上級（追加）──
def y_fib_mod():
    m, n = R.choice([3, 4, 5, 6, 7, 8, 9, 10]), R.randint(100, 2030)
    a, b = 1, 1
    seq = [1, 1]
    for _ in range(n): a, b = b, (a + b) % m; seq.append(b)
    v = seq[n - 1] % m
    # 周期を求める
    a, b, per = 1, 1, 0
    while True:
        a, b = b, (a + b) % m; per += 1
        if (a, b) == (1, 1): break
    return add("h_seq2", 4, "フィボナッチ数列の余り", f"$a_1 = a_2 = 1$、$a_{{n+2}} = a_{{n+1}} + a_n$ で定まる数列について、$a_{{{n}}}$ を {m} で割った余りを答えよ。", v,
               f"余りの列は周期 {per} でくり返す。${n}$ を {per} で割った余りの番号の項を見ると、余りは ${v}$。")


def y_tri_perimeter():
    n = R.randint(12, 40)
    cnt = sum(1 for a in range(1, n) for b in range(a, n) for c in [n - a - b] if c >= b and a + b > c)
    return add("h_count", 4, "周の長さが決まった三角形", f"3 辺の長さがすべて整数で、周の長さが {n} の三角形は何種類あるか（合同なものは同じとみなす）。", cnt,
               f"$a \\le b \\le c$、$a + b + c = {n}$、$a + b > c$ を満たす組を、$c$ の値ごとに数える。{cnt} 種類。")


def y_kummer():
    n = R.randint(10, 60)
    c = math.comb(2 * n, n)
    e = 0
    while c % 2 == 0: c //= 2; e += 1
    return add("h_nt", 4, "二項係数に含まれる 2 の個数", f"${{}}_{{{2 * n}}}\\mathrm{{C}}_{{{n}}}$ は 2 で最大何回割り切れるか。", e,
               f"$\\dfrac{{({2 * n})!}}{{({n}!)^2}}$ の 2 の指数を、$[\\tfrac{{m}}{{2}}] + [\\tfrac{{m}}{{4}}] + \\cdots$ で数えて引く。{n} を 2 進法で書いたときの 1 の個数と等しく、${e}$。")


def y_walk():
    n = R.randint(4, 8); k = R.randint(0, n)
    if (n - k) % 2: return False
    p_num, p_den = R.choice([(1, 2), (1, 3), (2, 3), (1, 4), (3, 4)])
    pr = F(p_num, p_den)
    r = (n + k) // 2
    v = math.comb(n, r) * pr ** r * (1 - pr) ** (n - r)
    if v.denominator == 1: return False
    return add("h_prob", 4, "数直線上を動く点", f"数直線上の原点にある点 P が、1 回ごとに確率 ${frac_tex(pr)}$ で $+1$、確率 ${frac_tex(1 - pr)}$ で $-1$ だけ動く。{n} 回動いたあと、P が座標 ${k}$ にある確率を既約分数 $\\dfrac{{a}}{{b}}$ で表す。$a + b$ を答えよ。",
               ab(v), f"$+1$ が {r} 回、$-1$ が {n - r} 回。${{}}_{{{n}}}\\mathrm{{C}}_{{{r}}}\\left({frac_tex(pr)}\\right)^{{{r}}}\\left({frac_tex(1 - pr)}\\right)^{{{n - r}}} = {frac_tex(v)}$。")


def y_exp_max():
    n, m = R.choice([2, 3]), R.choice([4, 6])
    e = F(sum(max(t) for t in itertools.product(range(1, m + 1), repeat=n)), m ** n)
    if e.denominator == 1: return False
    return add("h_prob", 4, "最大の目の期待値", f"1 から {m} までの目が等しい確率で出る{'さいころ' if m == 6 else '正四面体のさいころ'}を {n} 回投げる。出た目の最大値の期待値を既約分数 $\\dfrac{{a}}{{b}}$ で表す。$a + b$ を答えよ。",
               ab(e), f"最大値が $k$ 以下になる確率は $\\left(\\dfrac{{k}}{{{m}}}\\right)^{{{n}}}$。最大値がちょうど $k$ の確率を求めて期待値を計算すると ${frac_tex(e)}$。")


def y_tangent_count():
    a = R.randint(-3, 3); b = R.randint(-6, 6)
    T = sp.Symbol("t")
    f = T ** 3 - 3 * T
    eq = sp.expand(f + sp.diff(f, T) * (a - T) - b)
    roots = set(r for r in sp.real_roots(sp.Poly(eq, T)))
    cnt = len(roots)
    return add("h_diff2", 4, "引ける接線の本数", f"点 $({a}, {b})$ から、曲線 $y = x^3 - 3x$ に引ける接線は何本あるか。", cnt,
               f"接点を $(t, t^3 - 3t)$ とすると、接線が $({a}, {b})$ を通る条件は $t$ の 3 次方程式になる。その異なる実数解の個数が接線の本数で、{cnt} 本。")


def y_region_lattice():
    a, b = R.randint(2, 6), R.randint(1, 4)
    cnt = sum(1 for x in range(-20, 21) for y in range(-30, 60) if y >= x * x - a and y <= b * x + a)
    return add("h_quadfunc", 4, "放物線と直線で囲まれた格子点", f"連立不等式 $y \\ge x^2 - {a}$、$y \\le {'' if b == 1 else b}x + {a}$ を満たす整数の組 $(x, y)$ は何組あるか。", cnt,
               f"$x^2 - {a} \\le {b}x + {a}$ を満たす整数 $x$ ごとに、$y$ の個数 $({b}x + {a}) - (x^2 - {a}) + 1$ を足す。{cnt} 組。".replace(" 1x", " x"))


def y_exactly_one():
    p, q, r = R.choice([(2, 3, 5), (2, 3, 7), (3, 5, 7), (2, 5, 7)]); N = R.choice([100, 200, 300, 500, 1000])
    cnt = sum(1 for k in range(1, N + 1) if [k % p == 0, k % q == 0, k % r == 0].count(True) == 1)
    return add("h_count", 4, "ちょうど 1 つで割り切れる数", f"1 から {N} までの整数のうち、{p}、{q}、{r} のうちちょうど 1 つだけで割り切れるものは何個あるか。", cnt,
               f"包除原理で、1 つだけで割り切れる個数 $= \\sum |A_i| - 2\\sum |A_i \\cap A_j| + 3|A_1 \\cap A_2 \\cap A_3|$。{cnt} 個。")


def y_telescope():
    n = R.randint(5, 30)
    v = sum(F(1, k * (k + 1) * (k + 2)) for k in range(1, n + 1))
    return add("h_seq", 4, "部分分数分解と和", f"$\\displaystyle\\sum_{{k=1}}^{{{n}}} \\dfrac{{1}}{{k(k+1)(k+2)}}$ を既約分数 $\\dfrac{{a}}{{b}}$ で表す。$a + b$ を答えよ。",
               ab(v), f"$\\dfrac{{1}}{{k(k+1)(k+2)}} = \\dfrac{{1}}{{2}}\\left\\{{\\dfrac{{1}}{{k(k+1)}} - \\dfrac{{1}}{{(k+1)(k+2)}}\\right\\}}$ で打ち消し合う。和は ${frac_tex(v)}$。")


def y_gcd_seq():
    a = R.randint(1, 60)
    g = max(math.gcd(n * n + a, (n + 1) ** 2 + a) for n in range(1, 20000))
    return add("h_nt", 4, "隣り合う項の最大公約数", f"正の整数 $n$ に対して $d_n$ を、$n^2 + {a}$ と $(n+1)^2 + {a}$ の最大公約数とする。$d_n$ の最大値を答えよ。", g,
               f"$d_n$ は $2n + 1$ を割り切り、さらに $4(n^2 + {a}) - (2n+1)(2n-1) = {4 * a + 1}$ を割り切る。$d_n = {g}$ となる $n$ がある。")


def y_digit_sum():
    k, sm = R.choice([3, 4]), R.randint(5, 20)
    cnt = sum(1 for x in range(1, 10 ** k) if sum(map(int, str(x))) == sm)
    return add("h_count", 4, "各位の和が決まった数", f"1 以上 ${10 ** k}$ 未満の整数のうち、各位の数の和が {sm} になるものは何個あるか。", cnt,
               f"{k} けたの数字の列（先頭の 0 を許す）として、和が {sm} になる重複組合せから、10 以上の位を含むものを包除原理で除く。{cnt} 個。")


def y_obtuse_ngon():
    n = R.randint(6, 14)
    import cmath
    pts = [cmath.exp(2j * math.pi * k / n) for k in range(n)]
    def kind(a, b, c):
        res = []
        for P, Q, S in ((a, b, c), (b, c, a), (c, a, b)):
            d = ((Q - P).conjugate() * (S - P)).real
            res.append(d)
        if any(abs(d) < 1e-9 for d in res): return "right"
        if any(d < 0 for d in res): return "obtuse"
        return "acute"
    want = R.choice(["obtuse", "acute"])
    cnt = sum(1 for t in itertools.combinations(pts, 3) if kind(*t) == want)
    word = "鈍角三角形" if want == "obtuse" else "鋭角三角形"
    return add("h_count", 4, "正多角形の頂点でつくる三角形", f"正{n}角形の {n} 個の頂点から 3 個を選んで三角形をつくる。{word}は何個できるか。", cnt,
               f"外接円で考える。3 点が半円の内側にあれば鈍角、直径を含めば直角、そうでなければ鋭角。数えると {cnt} 個。")


def y_xy_eq():
    a, b = R.randint(1, 12), R.randint(1, 12)
    cnt = sum(1 for x in range(1, 2000) for y in [None] if (x - b) != 0 and (a * x) % (x - b) == 0 and a * x // (x - b) > 0)
    # xy = a x + b y ⇔ (x - b)(y - a) = ab
    cnt = sum(1 for d in range(1, a * b + 1) if (a * b) % d == 0)
    return add("h_nt", 4, "積の形にする不定方程式", f"$xy = {'' if a == 1 else a}x + {'' if b == 1 else b}y$ を満たす正の整数の組 $(x, y)$ は何組あるか。", cnt,
               f"$(x - {b})(y - {a}) = {a * b}$ と変形できる。$x - {b}$、$y - {a}$ がともに負になる場合はないので、{a * b} の正の約数の個数と同じ {cnt} 組。")


def y_cubic_area():
    a, b = R.randint(1, 4), R.randint(1, 4)
    X = sp.Symbol("x")
    f = X * (X + a) * (X - b)
    v = sp.integrate(f, (X, -a, 0)) - sp.integrate(f, (X, 0, b))
    v = F(str(sp.nsimplify(v)))
    if v.denominator == 1: return False
    return add("h_integ_app", 4, "3 次関数と x 軸で囲む面積", f"曲線 $y = x(x + {a})(x - {b})$ と $x$ 軸で囲まれた 2 つの部分の面積の和を既約分数 $\\dfrac{{p}}{{q}}$ で表す。$p + q$ を答えよ。",
               ab(v), f"$-{a} \\le x \\le 0$ では $y \\ge 0$、$0 \\le x \\le {b}$ では $y \\le 0$。分けて積分して足すと ${frac_tex(v)}$。")


def y_prob_streak():
    n, k = R.randint(5, 8), R.randint(2, 3)
    w = sum(1 for t in itertools.product([0, 1], repeat=n) if any(all(t[i + j] for j in range(k)) for i in range(n - k + 1)))
    p = F(w, 2 ** n)
    return add("h_prob", 4, "連続して表が出る確率", f"硬貨を {n} 回投げる。表が {k} 回以上続けて出ることがある確率を既約分数 $\\dfrac{{a}}{{b}}$ で表す。$a + b$ を答えよ。",
               ab(p), f"表が {k} 回続かない並び方を、最後に出た表の連続回数で分けた漸化式で数える。余事象から ${frac_tex(p)}$。")


PLAN = [
    # (関数, 個数)  初級 150
    (e_frac_add, 10), (e_lcm_word, 8), (e_ratio_share, 10), (e_speed_meet, 10), (e_avg_missing, 10),
    (m_lin_eq, 12), (m_signed_calc, 10), (m_pythag_basic, 8), (m_prob_dice, 8),
    (h_quadfunc_vertex, 12), (h_exp_log, 10), (h_diff_slope, 12), (h_seq_arith, 10), (h_integ_basic, 10), (h_count_basic, 6), (h_trig_value, 6),
    # 中級 200
    (e_work, 9), (e_tsuru, 12), (m_simul_word, 14), (m_quad_int, 14), (m_func2_area, 12), (m_circle_angle, 8), (m_data_median, 12),
    (h_quadeq_disc, 7), (h_trig_cos_rule, 14), (h_prob_draw, 14), (h_nt_divisors, 14), (h_exp_eq, 12), (h_seq_geo, 12),
    (h_vec_dot, 12), (h_circle_center, 12), (h_limit_rational, 10), (h_cplx_calc, 12), (h_diff_extreme, 12),
    # 上級 350
    (e_clock, 16), (e_count_paths, 14), (m_int_digits, 3), (m_space_cone, 5), (m_quad_word, 18),
    (h_count_circle, 4), (h_count_dist, 18), (h_prob_cond, 15), (h_nt_mod, 15), (h_nt_diophantine, 15), (h_seq_rec, 15),
    (h_seq_sigma, 14), (h_integ_area, 18), (h_vec_area, 14), (h_addition_tan, 14), (h_binom_coef, 15), (h_conic_ellipse, 12),
    (h_complex_pow, 18), (h_diff3_max, 4), (h_integ3_parts, 3),
    # 最上級 300
    (x_lattice_disc, 16), (x_dice_max_min, 3), (x_dice_prod, 9), (x_mod_last2, 18), (x_divisor_sum, 12), (x_count_subset_mod, 14),
    (x_surj, 9), (x_grid_avoid, 12), (x_rec_n, 18), (x_floor_sum, 16), (x_tangent_area, 6), (x_abs_integral, 10),
    (x_cubic_roots_k, 4), (x_quad_two_pos, 10), (x_abs_ineq, 16), (x_vec_min, 12), (x_tetra_volume, 16), (x_riemann, 8),
    (x_rotation_volume, 3), (x_complex_sum, 10), (x_complex_poly, 8), (x_log_digits, 10), (x_stat_var, 10),
    (x_geom_inscribed, 6), (x_circum_r, 6), (x_trig_count, 8), (x_lim_sqrt, 8), (x_max_on_interval, 10), (x_coef_trinom, 14),
    (x_parabola_dist, 8),
    (y_fib_mod, 12), (y_tri_perimeter, 10), (y_kummer, 10), (y_walk, 10), (y_exp_max, 3), (y_tangent_count, 12),
    (y_region_lattice, 10), (y_exactly_one, 10), (y_telescope, 8), (y_gcd_seq, 8), (y_digit_sum, 10), (y_obtuse_ngon, 10),
    (y_xy_eq, 10), (y_cubic_area, 8), (y_prob_streak, 5),
]


def generate():
    OUT.clear(); _seen.clear(); _count.clear()
    for fn, n in PLAN:
        make(n, fn)
    return list(OUT)


if __name__ == "__main__":
    import collections
    ps = generate()
    print(len(ps), collections.Counter(p["difficulty"] for p in ps))
