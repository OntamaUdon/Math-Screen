"""フラットなアプリアイコン (1024x1024) を生成する。 python3 tools/make_icon.py"""
import os
from PIL import Image, ImageDraw, ImageFont

S = 1024
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, "mathscreen/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png")
img = Image.new("RGB", (S, S), (205, 235, 221))           # ミント
d = ImageDraw.Draw(img)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 560)
text = "√"
b = d.textbbox((0, 0), text, font=font)
d.text((S / 2 - (b[2] - b[0]) / 2 - b[0], S / 2 - (b[3] - b[1]) / 2 - b[1]), text, font=font, fill=(38, 38, 42))
img.save(out)
print("saved", out)
