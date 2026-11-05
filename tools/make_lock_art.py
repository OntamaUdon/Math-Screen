"""アイソメトリックの南京錠のイラストから、アプリアイコンと、プラン画面のアイコンをつくる。
   python3 tools/make_lock_art.py
"""
import math, os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "mathscreen/Resources/Assets.xcassets")
SS = 4  # 縮小して滑らかにする

def hexc(h): return ((h >> 16) & 255, (h >> 8) & 255, h & 255)

CORAL = dict(top=0xFFB29D, left=0xD2553A, right=0xFF7A59)
TEAL = dict(top=0x7FE0D3, left=0x26968A, right=0x3CC5B5)
SLAB = dict(top=0xFFFFFF, left=0xC7CCDA, right=0xDDE1EC)

def render(size, body, block, bg=None, scale=1.0):
    S = size * SS
    img = Image.new("RGBA", (S, S), hexc(bg) + (255,) if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    k = S / 300 * scale

    def P(x, y, z):
        return (S / 2 + (x - y) * 0.866 * k, S * 0.62 + (x + y) * 0.5 * k - z * k + (S * (1 - scale) * 0.0))

    def poly(pts, c): d.polygon([P(*p) for p in pts], fill=hexc(c))

    def box(x0, y0, z0, w, dp, h, c):
        x1, y1, z1 = x0 + w, y0 + dp, z0 + h
        poly([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], c["left"])
        poly([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], c["right"])
        poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], c["top"])

    # 土台
    box(-84, -62, 0, 168, 124, 14, SLAB)
    # 奥の小さなブロック（差し色）
    box(34, -54, 14, 30, 30, 28, block)
    # 錠の本体（横長。大きい面を手前に）
    bx, by, bz, bw, bd, bh = -42, -22, 14, 84, 44, 62
    box(bx, by, bz, bw, bd, bh, body)
    # 本体の上面の縁取り（立体感）
    top = bz + bh
    # つる：x-z 平面の U 字を、厚みのある管として描く
    ym = by + bd / 2
    r = 25
    path = [(-r, top)]
    path += [(-r, top + 22)]
    for i in range(0, 37):
        a = math.pi - math.pi * i / 36
        path.append((r * math.cos(a), top + 22 + r * math.sin(a)))
    path += [(r, top + 22), (r, top)]
    def stroke(offset_y, color, width):
        pts = [P(x, ym + offset_y, z) for x, z in path]
        d.line(pts, fill=hexc(color), width=int(width * k), joint="curve")
        for (px, py) in (pts[0], pts[-1]):
            pass
        # 先端を丸める
        for (px, py) in (pts[0], pts[-1]):
            rr = width * k / 2
            d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=hexc(color))
    # 奥行き（暗い側面）→ 手前（明るい面）の順に重ねる
    for off in (6, 4.5, 3, 1.5):
        stroke(off, 0x4E5370, 13)
    stroke(0, 0x8E94AD, 13)
    stroke(-1.5, 0xB8BED3, 7)
    # 鍵穴（大きい面＝左の面に、傾きに合わせて描く）
    cx, cy = P(0, by + bd, bz + bh * 0.52)
    def sheared(px, py):  # 面の中の (横, 縦) を画面へ
        return (cx + px * 0.866 * k, cy + px * 0.5 * k - py * k)
    ring = [sheared(8 * math.cos(t), 8 * math.sin(t) + 5) for t in [i * math.pi / 18 for i in range(37)]]
    d.polygon(ring, fill=hexc(0x23263A))
    d.polygon([sheared(-3.6, 6), sheared(3.6, 6), sheared(5, -14), sheared(-5, -14)], fill=hexc(0x23263A))
    return img.resize((size, size), Image.LANCZOS)

if __name__ == "__main__":
    icon = render(1024, CORAL, TEAL, bg=0xEEF1F8, scale=1.08).convert("RGB")
    icon.save(os.path.join(ASSETS, "AppIcon.appiconset/icon-1024.png"))
    plan = render(600, TEAL, CORAL, bg=None, scale=1.0)
    out = os.path.join(ASSETS, "PlanLock.imageset")
    os.makedirs(out, exist_ok=True)
    plan.save(os.path.join(out, "plan-lock.png"))
    open(os.path.join(out, "Contents.json"), "w").write(
        '{\n  "images" : [ { "filename" : "plan-lock.png", "idiom" : "universal" } ],\n  "info" : { "author" : "xcode", "version" : 1 }\n}\n')
    print("ok")
