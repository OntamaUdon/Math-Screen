"""クレイ風アプリアイコン (1024x1024) を生成する。 python3 tools/make_icon.py"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

S = 1024
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, "mathscreen/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png")

img = Image.new("RGB", (S, S), (233, 231, 227))
# 背景のパステルのにじみ
glow = Image.new("RGB", (S, S), (233, 231, 227))
g = ImageDraw.Draw(glow)
g.ellipse((-200, -200, 560, 560), fill=(207, 200, 236))
g.ellipse((520, 560, 1240, 1240), fill=(195, 230, 214))
img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(160)), 0.75)

def blob(box, r, color, depth=40):
    x0, y0, x1, y1 = box
    global img
    # 外側の影
    sh = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sh).rounded_rectangle((x0 + depth*.5, y0 + depth*.8, x1 + depth*.5, y1 + depth*.8), r, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(depth))
    img = Image.composite(Image.new("RGB", (S, S), (170, 164, 156)), img, sh)
    hl = Image.new("L", (S, S), 0)
    ImageDraw.Draw(hl).rounded_rectangle((x0 - depth*.4, y0 - depth*.4, x1 - depth*.4, y1 - depth*.4), r, fill=200)
    hl = hl.filter(ImageFilter.GaussianBlur(depth))
    img = Image.composite(Image.new("RGB", (S, S), (255, 255, 255)), img, hl)
    # 本体
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, r, fill=255)
    body = Image.new("RGB", (S, S), color)
    # 内側ハイライト（左上）と陰（右下）
    inner_hl = Image.new("L", (S, S), 0)
    ImageDraw.Draw(inner_hl).rounded_rectangle((x0 + 30, y0 + 30, x1 + 60, y1 + 60), r, fill=255)
    inner_hl = ImageChops.subtract(mask, inner_hl).filter(ImageFilter.GaussianBlur(28))
    body = Image.composite(Image.new("RGB", (S, S), (255, 255, 255)), body, inner_hl.point(lambda v: int(v * .8)))
    inner_sh = Image.new("L", (S, S), 0)
    ImageDraw.Draw(inner_sh).rounded_rectangle((x0 - 60, y0 - 60, x1 - 36, y1 - 36), r, fill=255)
    inner_sh = ImageChops.subtract(mask, inner_sh).filter(ImageFilter.GaussianBlur(34))
    shade = tuple(int(c * .78) for c in color)
    body = Image.composite(Image.new("RGB", (S, S), shade), body, inner_sh.point(lambda v: int(v * .7)))
    img = Image.composite(body, img, mask)

blob((212, 212, 812, 812), 190, (207, 200, 236), depth=46)
blob((560, 140, 860, 440), 150, (244, 210, 195), depth=30)

d = ImageDraw.Draw(img)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 380)
text = "√"
bbox = d.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
pos = (512 - tw / 2 - bbox[0], 520 - th / 2 - bbox[1])
d.text((pos[0] + 8, pos[1] + 12), text, font=font, fill=(160, 152, 196))
d.text(pos, text, font=font, fill=(46, 45, 51))
f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
d.text((668, 218), "?", font=f2, fill=(46, 45, 51))
img.save(out)
print("saved", out)
