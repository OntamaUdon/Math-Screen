#!/usr/bin/env python3
"""画面に出ている問題を problems.json から探して、押すボタンの文字を1行ずつ出す。
使い方：python3 answer.py ui.xml problems.json right|wrong
4択なら「②」など、数字の問題なら「1」「2」…（負の数は「±」から）。最後に「こたえる」。"""
import json, sys, xml.etree.ElementTree as ET

ui, data, mode = sys.argv[1], sys.argv[2], sys.argv[3]
texts = set()
for n in ET.parse(ui).getroot().iter("node"):
    for k in ("text", "content-desc"):
        v = n.get(k, "").strip()
        if v: texts.add(v)
problems = json.load(open(data, encoding="utf-8"))
p = next((q for q in problems if q["plain"].strip() in texts), None)
if p is None:
    sys.exit("画面の問題が problems.json に見つかりません")
marks = ["①", "②", "③", "④"]
if p.get("choices"):
    i = p["answer"] if mode == "right" else (p["answer"] + 1) % len(p["choices"])
    print(marks[i])
else:
    v = p["answer"] if mode == "right" else p["answer"] + 1
    if v < 0: print("±")
    for ch in str(abs(v)): print(ch)
print("こたえる")
