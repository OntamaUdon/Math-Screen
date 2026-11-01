"""アイソメトリックのアプリアイコン (1024x1024) を生成する。 python3 tools/make_icon.py"""
import math, os
from PIL import Image, ImageDraw, ImageFont

S = 1024
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, "mathscreen/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png")
img = Image.new("RGB", (S, S), (238, 241, 247))
d = ImageDraw.Draw(img)
c = math.cos(math.pi / 6)

def proj(ox, oy, s):
    return lambda x, y, z: (ox + (x - y) * c * s, oy + (x + y) * 0.5 * s - z * s)

def cube(P, x, y, z, w, dd, h, top, left, right):
    d.polygon([P(x, y + dd, z), P(x + w, y + dd, z), P(x + w, y + dd, z + h), P(x, y + dd, z + h)], fill=left)
    d.polygon([P(x + w, y, z), P(x + w, y + dd, z), P(x + w, y + dd, z + h), P(x + w, y, z + h)], fill=right)
    d.polygon([P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + dd, z + h), P(x, y + dd, z + h)], fill=top)

s = 300
P = proj(512, 550, s)
teal = ((127, 224, 211), (60, 197, 181), (38, 150, 138))
coral = ((255, 178, 157), (255, 122, 89), (210, 85, 58))
cube(P, -0.5, -0.5, -0.55, 1.0, 1.0, 0.9, *teal)

# 天面に √ を貼る：文字画像を天面の向きにアフィン変換
tile = Image.new("L", (400, 400), 0)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 300)
td = ImageDraw.Draw(tile)
b = td.textbbox((0, 0), "√", font=f)
td.text((200 - (b[2] - b[0]) / 2 - b[0], 200 - (b[3] - b[1]) / 2 - b[1]), "√", font=f, fill=255)
# 文字画像の四角を、天面の手前寄りの領域 (x, y ∈ [-0.2, 0.55], z = 0.35) に対応させる
o = P(-0.2, -0.2, 0.35); ex = P(0.55, -0.2, 0.35); ey = P(-0.2, 0.55, 0.35)
a, bb = (ex[0] - o[0]) / 400, (ey[0] - o[0]) / 400
cc, dd = (ex[1] - o[1]) / 400, (ey[1] - o[1]) / 400
det = a * dd - bb * cc
inv = (dd / det, -bb / det, -cc / det, a / det)
coeffs = (inv[0], inv[1], -(inv[0] * o[0] + inv[1] * o[1]), inv[2], inv[3], -(inv[2] * o[0] + inv[3] * o[1]))
mask = tile.transform((S, S), Image.AFFINE, coeffs, resample=Image.BICUBIC)
img.paste((35, 38, 58), (0, 0), mask.point(lambda v: int(v * 0.95)))
cube(P, -0.5, -0.5, 0.35, 0.32, 0.32, 0.32, *coral)
img.save(out)
print("saved", out)
