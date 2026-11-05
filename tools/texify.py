"""文字だけで書いた式（A¹⁰、H₂O、[[3, 2], [1, 4]]、C(10,5) など）を、LaTeX（$...$）に直す。

build_problems.py の最後で、body・explanation・choices に使う。すでに $...$ の中にあるものには触らない。
plain（ブロック画面用の文字だけの問題文）は、直す前の文のまま。
"""
import re

SUB = {c: str(i) for i, c in enumerate("₀₁₂₃₄₅₆₇₈₉")}
SUB.update({"ₐ": "a", "ₑ": "e", "ₙ": "n", "₊": "+", "₋": "-"})
SUP = {c: str(i) for i, c in enumerate("⁰¹²³⁴⁵⁶⁷⁸⁹")}
SUP.update({"⁺": "+", "⁻": "-", "ⁿ": "n"})
SCRIPT = "".join(SUB) + "".join(SUP)

SUPCH = "".join(SUP)
SUBCH = "".join(SUB)
# 1) Ca(OH)₂ のような、かっこ付きの化学式  2) (…)² のようなかっこ付きの式  3) ふつうの語
WORD = re.compile(
    rf"[A-Z][a-z]?\([A-Za-z0-9{SUBCH}]+\)[{SUBCH}]+[A-Za-z0-9{SCRIPT}]*"
    rf"|\([^()]*\)[{SCRIPT}]+"
    rf"|[0-9A-Za-zα-ωΑ-Ω{SCRIPT}]*[{SCRIPT}][0-9A-Za-zα-ωΑ-Ω{SCRIPT}]*")
CHEM = re.compile(rf"^(?:\(|\)|\d|[{SCRIPT}]|[A-Z][a-z]?)+$")


def _runs(word):
    """文字列を (種類, 中身) の並びに分ける。種類は 'sub' 'sup' 'txt'。"""
    out = []
    for ch in word:
        kind = "sub" if ch in SUB else "sup" if ch in SUP else "txt"
        val = SUB.get(ch) or SUP.get(ch) or ch
        if out and out[-1][0] == kind:
            out[-1][1] += val
        else:
            out.append([kind, val])
    return out


def _word_to_tex(word):
    m = re.match(rf"^\(([^()]*)\)([{SCRIPT}]+)$", word)
    if m:                                  # (…)ⁿ
        inner = m.group(1)
        inner = _word_to_tex(inner).strip("$") if re.search(rf"[{SCRIPT}]", inner) else inner
        sup = "".join(SUP.get(c) or SUB.get(c) for c in m.group(2))
        op = "_" if m.group(2)[0] in SUB else "^"
        if op == "_" and re.search(r"[A-Z]", inner):
            inner = f"\\mathrm{{{inner}}}"
        return f"$({inner}){op}{{{sup}}}$"
    chem = bool(CHEM.match(word)) and bool(re.search(r"[A-Z]", word))
    runs = _runs(word)
    parts = []
    for i, (kind, val) in enumerate(runs):
        if kind == "sub":
            parts.append(f"_{{{val}}}")
        elif kind == "sup":
            if i == 0:
                parts.append(f"{{}}^{{{val}}}")        # 質量数など、左上に付くもの
            else:
                parts.append(f"^{{{val}}}")
        else:
            t = val
            if not chem:
                t = re.sub(r"\blog", r"\\log", t) if t.startswith("log") else t
            parts.append(t)
    body = "".join(parts)
    if chem:
        # 先頭の左上の数字は \mathrm の外に出す
        m = re.match(r"^(\{\}\^\{[^}]*\})(.*)$", body)
        pre, rest = (m.group(1), m.group(2)) if m else ("", body)
        return f"${pre}\\mathrm{{{rest}}}$"
    return f"${body}$"


def _outside(text):
    # 行列 [[a, b], [c, d]]
    def mat(m):
        rows = re.findall(r"\[([^\[\]]+)\]", m.group(0))
        cells = [[c.strip() for c in r.split(",")] for r in rows]
        return "$\\begin{pmatrix}" + "\\\\".join("&".join(r) for r in cells) + "\\end{pmatrix}$"
    text = re.sub(r"\[\[[^\[\]]+\](?:\s*,\s*\[[^\[\]]+\])+\]", mat, text)
    # 組合せ C(n,r)
    text = re.sub(r"\bC\((\d+),\s*(\d+)\)", r"${}_{\1}C_{\2}$", text)
    # a×10ⁿ
    def sci(m):
        e = "".join(SUP.get(c, c) for c in m.group(2))
        return f"${m.group(1)}\\times10^{{{e}}}$"
    # √(…)
    def root(m):
        inner = m.group(1)
        inner = re.sub(rf"(\d+(?:\.\d+)?)×10([{SUPCH}]+)", lambda k: sci(k).strip("$"), inner)
        inner = WORD.sub(lambda k: _word_to_tex(k.group(0)).strip("$"), inner)
        inner = inner.replace("×", "\\times ").replace("÷", "\\div ")
        return "$\\sqrt{" + inner + "}$"
    text = re.sub(r"√\(([^()]*)\)", root, text)
    text = re.sub(rf"(\d+(?:\.\d+)?)×10([{SUPCH}]+)", sci, text)
    # 残りの、上付き・下付き文字を含む語
    text = WORD.sub(lambda m: _word_to_tex(m.group(0)), text)
    return text


def texify(text):
    """$...$ の外だけを直す。組合せの書き方（{}_{n}C_{r}）だけは、$...$ の中も直す。"""
    text = re.sub(r"\{\}_\{?(\w+)\}?\\mathrm\{C\}_\{?(\w+)\}?", r"{}_{\1}C_{\2}", text)
    out, pos = [], 0
    for m in re.finditer(r"\$[^$]*\$", text):
        out.append(_outside(text[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(_outside(text[pos:]))
    return "".join(out)
