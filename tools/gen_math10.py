"""図形の問題を、問題ごとに図を作って足す（円周角・平行線と角・外角・三平方・面積・おうぎ形・円に内接する四角形・接弦定理）。

- 図は、問題の数字に合わせて1問ずつ描く（だいたいの形。角度はなるべく実際に近く描く）。
- 答えはコードで計算する。
"""
import math
import random
from fractions import Fraction as F
import gen_math9 as G9

R = random.Random(20261112)
OUT = []
_count = {}
INK, ACC = G9.INK, G9.ACC
label, poly_draw, fig_save = G9.label, G9.poly_draw, G9.fig_save


def add(unit, diff, title, body, ans, expl, draw):
    _count[unit] = _count.get(unit, 0) + 1
    pid = f"x10-{unit}-{_count[unit]}"
    name = "fig_" + pid.replace("-", "_")
    fig_save(name, draw)
    OUT.append(dict(id=pid, category=G9.CAT[unit], difficulty=diff, title=title, body=body, answer=int(ans),
                    explanation=expl, plain=G9.tex2plain(body), unit=unit, rate_hint=G9.RATE[diff], figure=name))


def pt(cx, cy, r, deg):
    return (cx + r * math.cos(math.radians(deg)), cy + r * math.sin(math.radians(deg)))


def circle(ax, c=(0, 0), r=1, color=INK, lw=2):
    th = [i * 2 * math.pi / 200 for i in range(201)]
    ax.plot([c[0] + r * math.cos(t) for t in th], [c[1] + r * math.sin(t) for t in th], color=color, lw=lw)


def out(P, c=(0, 0), k=0.16):
    d = math.hypot(P[0] - c[0], P[1] - c[1]) or 1
    return ((P[0] - c[0]) / d * k, (P[1] - c[1]) / d * k)


# ── 円周角 ──
def inscribed(n):
    seen = set()
    while len(seen) < n:
        a1, a2 = R.randint(200, 250), R.randint(290, 340)       # A, B は下側
        p = R.randint(70, 130)                                  # P は上側
        central = a2 - a1
        x = central / 2
        if central % 2 or (a1, a2) in seen: continue
        seen.add((a1, a2))
        ask = R.choice(["P", "O"])

        def draw(ax, a1=a1, a2=a2, p=p, ask=ask, x=x, central=central):
            circle(ax)
            A, B, P = pt(0, 0, 1, a1), pt(0, 0, 1, a2), pt(0, 0, 1, p)
            poly_draw(ax, [A, P, B], close=False)
            poly_draw(ax, [A, (0, 0), B], close=False, color=ACC)
            ax.plot([0], [0], "o", color=INK, ms=3)
            for Q, s in [(A, "A"), (B, "B"), (P, "P")]:
                d = out(Q); label(ax, Q, s, d[0], d[1], 12)
            label(ax, (0, 0), "O", 0.0, 0.14, 11)
            label(ax, P, "x" if ask == "P" else f"{int(x)}°", 0, -0.3, 11, ACC if ask == "P" else INK)
            label(ax, (0, 0), f"{central}°" if ask == "P" else "x", 0, -0.3, 11, INK if ask == "P" else ACC)
            ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.35, 1.35)
        if ask == "P":
            add("m_circle", 1, "円周角の定理", f"図で、O は円の中心で、$\\angle$AOB $= {central}^\\circ$ である。$\\angle$APB $= x$ を求めよ（度）。", x,
                f"円周角は、同じ弧に対する中心角の半分。$x = {central}^\\circ \\div 2 = {int(x)}^\\circ$。", draw)
        else:
            add("m_circle", 1, "中心角と円周角", f"図で、O は円の中心で、$\\angle$APB $= {int(x)}^\\circ$ である。$\\angle$AOB $= x$ を求めよ（度）。", central,
                f"中心角は、同じ弧に対する円周角の 2 倍。$x = {int(x)}^\\circ \\times 2 = {central}^\\circ$。", draw)


# ── 平行線と角 ──
def parallel_angle(n):
    for _ in range(n):
        a = R.randint(40, 140)
        kind = R.choice(["錯角", "同位角"])

        def draw(ax, a=a, kind=kind):
            ax.plot([-1.6, 1.6], [0.6, 0.6], color=INK, lw=1.8); ax.plot([-1.6, 1.6], [-0.6, -0.6], color=INK, lw=1.8)
            label(ax, (1.78, 0.6), "ℓ", size=12); label(ax, (1.78, -0.6), "m", size=12)
            t = math.radians(a)
            dx = 0.6 / math.tan(t)
            P, Q = (dx, 0.6), (-dx, -0.6)
            ax.plot([Q[0] - math.cos(t) * .55, P[0] + math.cos(t) * .55], [Q[1] - math.sin(t) * .55, P[1] + math.sin(t) * .55], color=ACC, lw=1.8)
            def at(X, ang, text, color=INK, size=11):
                r = 0.3
                label(ax, X, text, r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang)), size, color)
            at(P, a / 2, f"{a}°")                                  # 上の交点の右上の角 = a
            if kind == "同位角":
                at(Q, a / 2, "x", ACC, 12)                         # 下の交点の右上 = a
            else:
                at(Q, (a + 180) / 2, "x", ACC, 12)                 # 下の交点の左上 = 180 − a（上の右下と錯角）
            ax.set_xlim(-1.9, 2.0); ax.set_ylim(-1.25, 1.25)
        if kind == "同位角":
            ans, expl = a, f"ℓ // m なので、同位角は等しい。$x = {a}^\\circ$。"
        else:
            ans, expl = 180 - a, f"上の交点の右下の角は $180^\\circ - {a}^\\circ = {180 - a}^\\circ$。これと $x$ は錯角なので等しい（ℓ // m）。$x = {180 - a}^\\circ$。"
        add("m_polygon", 1, "平行線と角", "図で ℓ // m のとき、$x$ の大きさを求めよ（度）。", ans, expl, draw)


# ── 三角形の外角 ──
def exterior(n):
    for _ in range(n):
        a, b = R.randint(30, 80), R.randint(30, 80)
        if a + b >= 160: continue

        def draw(ax, a=a, b=b):
            B, C = (0, 0), (2.4, 0)
            ta, tb = math.radians(b), math.radians(180 - a - b)
            # B の角は b、C の角は 180 − a − b、A の角は a
            # A を、B から角 b の方向と、C から角 (180 − a − b) の方向の交点にする
            k = 2.4 * math.sin(tb) / math.sin(math.radians(a))
            A = (k * math.cos(ta), k * math.sin(ta))
            poly_draw(ax, [A, B, C]); ax.plot([2.4, 3.3], [0, 0], color=INK, lw=1.8)
            label(ax, A, "A", 0, .16, 12); label(ax, B, "B", -.14, -.1, 12); label(ax, C, "C", 0, -.18, 12)
            label(ax, A, f"{a}°", 0, -.32, 11); label(ax, B, f"{b}°", .38, .14, 11); label(ax, C, "x", .36, .16, 12, ACC)
            ax.set_xlim(-.4, 3.5); ax.set_ylim(-.4, max(A[1], 1) + .35)
        add("m_polygon", 1, "三角形の外角", "図で $x$ の大きさを求めよ（度）。", a + b,
            f"三角形の外角は、となり合わない 2 つの内角の和に等しい。$x = {a}^\\circ + {b}^\\circ = {a + b}^\\circ$。", draw)


# ── 三平方の定理 ──
def pythag(n):
    trip = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10), (7, 24, 25), (9, 12, 15), (12, 16, 20), (20, 21, 29), (9, 40, 41), (12, 35, 37)]
    R.shuffle(trip)
    for a, b, c in trip[:n]:
        ask = R.choice(["hyp", "leg"])

        def draw(ax, a=a, b=b, c=c, ask=ask):
            s = 2.6 / max(a, b)
            B, C, A = (0, 0), (b * s, 0), (0, a * s)
            poly_draw(ax, [A, B, C])
            q = 0.16; poly_draw(ax, [(q, 0), (q, q), (0, q)], close=False, lw=1.2)
            label(ax, ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2), str(a), -.2, 0, 12)
            if ask == "hyp":
                label(ax, ((B[0] + C[0]) / 2, 0), str(b), 0, -.18, 12)
                label(ax, ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2), "x", .16, .14, 13, ACC)
            else:
                label(ax, ((B[0] + C[0]) / 2, 0), "x", 0, -.18, 13, ACC)
                label(ax, ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2), str(c), .16, .14, 12)
            ax.set_xlim(-.5, C[0] + .4); ax.set_ylim(-.4, A[1] + .3)
        if ask == "hyp":
            add("m_pythag", 1, "三平方の定理（図）", "図の直角三角形で、$x$ の長さを求めよ。", c, f"$x^2 = {a}^2 + {b}^2 = {c * c}$。$x = {c}$。", draw)
        else:
            add("m_pythag", 1, "三平方の定理（図）", "図の直角三角形で、$x$ の長さを求めよ。", b, f"$x^2 = {c}^2 - {a}^2 = {b * b}$。$x = {b}$。", draw)


# ── 面積（小学） ──
def trapezoid(n):
    for _ in range(n):
        a, b, h = R.randint(2, 12), R.randint(4, 16), R.randint(2, 12)
        if a >= b or ((a + b) * h) % 2: continue

        def draw(ax, a=a, b=b, h=h):
            s = 3.0 / b
            off = (b - a) * s / 2
            P = [(0, 0), (b * s, 0), (off + a * s, h * s * .6 + .5), (off, h * s * .6 + .5)]
            poly_draw(ax, P)
            top = P[2][1]
            ax.plot([off, off], [0, top], color=ACC, lw=1.2, ls="--")
            label(ax, ((P[2][0] + P[3][0]) / 2, top), f"{a} cm", 0, .16, 11)
            label(ax, (b * s / 2, 0), f"{b} cm", 0, -.18, 11)
            label(ax, (off, top / 2), f"{h} cm", .34, 0, 11, ACC)
            ax.set_xlim(-.6, b * s + .3); ax.set_ylim(-.4, top + .4)
        add("e_geom", 1, "台形の面積（図）", "図の台形の面積は何 cm² か。", (a + b) * h // 2,
            f"（上底 + 下底）× 高さ ÷ 2 $= ({a} + {b}) \\times {h} \\div 2 = {(a + b) * h // 2}$ cm²。", draw)


def lshape(n):
    for _ in range(n):
        W, H, w, h = R.randint(6, 14), R.randint(6, 14), R.randint(2, 5), R.randint(2, 5)
        if w >= W - 1 or h >= H - 1: continue

        def draw(ax, W=W, H=H, w=w, h=h):
            s = 2.6 / max(W, H)
            P = [(0, 0), (W * s, 0), (W * s, (H - h) * s), ((W - w) * s, (H - h) * s), ((W - w) * s, H * s), (0, H * s)]
            poly_draw(ax, P)
            label(ax, (W * s / 2, 0), f"{W} cm", 0, -.18, 11)
            label(ax, (0, H * s / 2), f"{H} cm", -.4, 0, 11)
            label(ax, ((W - w / 2) * s, (H - h) * s), f"{w} cm", 0, .16, 10)
            label(ax, ((W - w) * s, (H - h / 2) * s), f"{h} cm", .38, 0, 10)
            ax.set_xlim(-.8, W * s + .4); ax.set_ylim(-.4, H * s + .2)
        add("e_geom", 2, "へこんだ形の面積（図）", "図の形の面積は何 cm² か（角はすべて直角）。", W * H - w * h,
            f"大きな長方形 ${W} \\times {H} = {W * H}$ から、欠けた長方形 ${w} \\times {h} = {w * h}$ を引く。${W * H - w * h}$ cm²。", draw)


# ── おうぎ形 ──
def sector(n):
    for _ in range(n):
        r, deg = R.randint(2, 12), R.choice([30, 45, 60, 72, 90, 120, 135, 150, 180, 240, 270])
        area = F(r * r * deg, 360)
        if area.denominator != 1: continue

        def draw(ax, r=r, deg=deg):
            th = [math.radians(-deg / 2 + 90) + i * math.radians(deg) / 80 for i in range(81)]
            xs = [math.cos(t) for t in th]; ys = [math.sin(t) for t in th]
            ax.plot([0] + xs + [0], [0] + ys + [0], color=INK, lw=2)
            label(ax, (0, 0), f"{deg}°", 0, .22 if deg < 200 else -.22, 11)
            label(ax, (xs[0] / 2, ys[0] / 2), f"{r} cm", .18, -.1, 11)
            ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3)
        add("m_circle", 2, "おうぎ形の面積（図）", "図のおうぎ形の面積は $a\\pi$ cm² である。$a$ を求めよ。", area,
            f"$\\pi \\times {r}^2 \\times \\dfrac{{{deg}}}{{360}} = {area}\\pi$。", draw)


# ── 円に内接する四角形 ──
def cyclic(n):
    for _ in range(n):
        a = R.randint(55, 125)

        def draw(ax, a=a):
            circle(ax)
            angs = [200, 330, 40, 115]
            P = [pt(0, 0, 1, t) for t in angs]
            poly_draw(ax, P)
            for Q, s in zip(P, "ABCD"):
                d = out(Q); label(ax, Q, s, d[0], d[1], 12)
            label(ax, P[0], f"{a}°", .24, .16, 11)
            label(ax, P[2], "x", -.2, -.14, 12, ACC)
            ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.35, 1.35)
        add("m_circle", 2, "円に内接する四角形（図）", "図の四角形 ABCD は円に内接している。$\\angle$A $= " + f"{a}" + "^\\circ$ のとき、$\\angle$C $= x$ を求めよ（度）。", 180 - a,
            f"円に内接する四角形の向かい合う角の和は $180^\\circ$。$x = 180^\\circ - {a}^\\circ = {180 - a}^\\circ$。", draw)


# ── 接弦定理 ──
def tangent_chord(n):
    for _ in range(n):
        a = R.randint(30, 80)

        def draw(ax, a=a):
            circle(ax)
            T = (0, -1)
            ax.plot([-1.6, 1.6], [-1, -1], color=INK, lw=1.8)
            B = pt(0, 0, 1, -90 + 2 * a)      # 接線と弦 TB のなす角が a
            C = pt(0, 0, 1, 150)
            poly_draw(ax, [T, B], close=False, color=ACC); poly_draw(ax, [T, C, B], close=False)
            label(ax, T, "T", 0, -.18, 12)
            d = out(B); label(ax, B, "B", d[0], d[1], 12)
            d = out(C); label(ax, C, "C", d[0], d[1], 12)
            label(ax, T, f"{a}°", .72, .1, 11)
            label(ax, C, "x", .22, -.2, 12, ACC)
            ax.set_xlim(-1.7, 1.7); ax.set_ylim(-1.4, 1.35)
        add("h_geom", 2, "接弦定理（図）", "図で、直線は T で円に接している。接線と弦 TB のなす角が " + f"${a}^\\circ$" + " のとき、$\\angle$TCB $= x$ を求めよ（度）。", a,
            "接線と弦のつくる角は、その角の内側にある弧に対する円周角に等しい（接弦定理）。$x = " + f"{a}" + "^\\circ$。", draw)


def generate():
    OUT.clear(); _count.clear()
    inscribed(10); parallel_angle(8); exterior(10); pythag(10); trapezoid(10); lshape(8); sector(10); cyclic(8); tangent_chord(8)
    return list(OUT)


if __name__ == "__main__":
    ps = generate()
    print(len(ps))
