#!/usr/bin/env python3
"""画面の部品を、文字（または説明）で探して、その真ん中の座標を出す。uiautomator dump の XML を読む。
使い方：python3 ui.py dump.xml "緊急解除"   → "540 1800"（見つからなければ何も出さず、終了コード 1）"""
import re, sys, xml.etree.ElementTree as ET

path, want = sys.argv[1], sys.argv[2]
exact = len(sys.argv) > 3 and sys.argv[3] == "exact"
root = ET.parse(path).getroot()
for n in root.iter("node"):
    t = n.get("text", ""); d = n.get("content-desc", "")
    hit = (t == want or d == want) if exact else (want in t or want in d)
    if hit:
        x1, y1, x2, y2 = map(int, re.findall(r"\d+", n.get("bounds")))
        print((x1 + x2) // 2, (y1 + y2) // 2)
        sys.exit(0)
sys.exit(1)
