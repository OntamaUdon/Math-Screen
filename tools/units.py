"""単元（学習指導要領のまとまり）の定義と、問題を単元に振り分ける表。

units.json の中身：id・教科・段階（小学/中学/高校）・名前・前提にする単元。
問題の完成度は、単元ごとの直近の正答率と「1発正解」で測る（アプリ側）。
問題が1つもない単元は、アプリでは表示しない（小学の算数などは、問題を足すと自動で出る）。
"""

# (id, 教科, 段階, 名前, 前提にする単元)
UNITS = [
    # ── 算数・数学：小学 ──
    ("e_calc",     "math", "小学", "四則計算", []),
    ("e_decfrac",  "math", "小学", "小数と分数", ["e_calc"]),
    ("e_divmult",  "math", "小学", "約数と倍数", ["e_calc"]),
    ("e_ratio",    "math", "小学", "割合と比", ["e_decfrac"]),
    ("e_speed",    "math", "小学", "速さ・時間・道のり", ["e_ratio"]),
    ("e_geom",     "math", "小学", "面積と体積", ["e_calc"]),
    ("e_count",    "math", "小学", "場合の数", ["e_calc"]),
    # ── 数学：中学 ──
    ("m_signed",   "math", "中学", "正負の数", ["e_calc"]),
    ("m_expr",     "math", "中学", "式の値", ["m_signed"]),
    ("m_linear",   "math", "中学", "一次方程式", ["m_expr"]),
    ("m_simul",    "math", "中学", "連立方程式", ["m_linear"]),
    ("m_ineq",     "math", "中学", "不等式", ["m_linear"]),
    ("m_sqrt",     "math", "中学", "平方根", ["m_signed"]),
    ("m_factor",   "math", "中学", "因数分解", ["m_expr"]),
    ("m_quad",     "math", "中学", "二次方程式", ["m_sqrt", "m_factor"]),
    ("m_func2",    "math", "中学", "関数 y = ax²", ["m_linear"]),
    ("m_pythag",   "math", "中学", "三平方の定理", ["m_sqrt"]),
    ("m_polygon",  "math", "中学", "図形と角", ["m_linear"]),
    ("m_prob",     "math", "中学", "確率", ["m_signed"]),
    ("m_int",      "math", "中学", "整数の性質", ["m_signed"]),
    # ── 数学：高校 ──
    ("h_quadfunc", "math", "高校", "二次関数", ["m_func2", "m_quad"]),
    ("h_quadeq",   "math", "高校", "二次方程式・判別式", ["m_quad"]),
    ("h_trig",     "math", "高校", "三角比", ["m_pythag"]),
    ("h_logic",    "math", "高校", "命題と条件", []),
    ("h_abs",      "math", "高校", "絶対値と不等式", ["m_ineq"]),
    ("h_count",    "math", "高校", "場合の数", ["m_prob"]),
    ("h_prob",     "math", "高校", "確率（高校）", ["h_count"]),
    ("h_nt",       "math", "高校", "整数の性質（高校）", ["m_int"]),
    ("h_exp",      "math", "高校", "指数・対数", ["m_sqrt"]),
    ("h_seq",      "math", "高校", "数列", ["m_linear"]),
    ("h_binom",    "math", "高校", "二項定理", ["h_count", "m_factor"]),
    ("h_circle",   "math", "高校", "図形と方程式", ["m_quad"]),
    ("h_trig2",    "math", "高校", "三角関数", ["h_trig"]),
    ("h_diff",     "math", "高校", "微分", ["h_quadfunc"]),
    ("h_integ",    "math", "高校", "積分", ["h_diff"]),
    ("h_vec",      "math", "高校", "ベクトル", ["h_trig"]),
    ("h_limit",    "math", "高校", "極限", ["h_seq"]),
    ("h_diff3",    "math", "高校", "いろいろな微分", ["h_diff", "h_trig2"]),
    ("h_integ3",   "math", "高校", "いろいろな積分", ["h_integ", "h_diff3"]),
    ("h_complex",  "math", "高校", "複素数平面", ["h_trig2", "h_quadeq"]),
    ("h_conic",    "math", "高校", "二次曲線", ["h_circle"]),
    ("h_space",    "math", "高校", "空間図形", ["h_vec"]),
    # ── 英語 ──
    ("w_basic",    "english", "中学", "基本の英単語", []),
    ("w_std",      "english", "高校", "標準の英単語", ["w_basic"]),
    ("g_grammar",  "english", "中学", "英語の文法", []),
    ("g_translate", "english", "中学", "英文の和訳", ["g_grammar"]),
    # ── 社会 ──
    ("s_geo",      "social", "中学", "地理", []),
    ("s_hist",     "social", "中学", "歴史", []),
    ("s_civ",      "social", "中学", "公民", []),
    # ── 理科 ──
    ("b_all",      "science", "中学", "生物", []),
    ("c_all",      "science", "中学", "化学", []),
    ("e_all",      "science", "中学", "地学", []),
    ("p_other",    "science", "中学", "物理の基本", []),
    ("p_speed",    "science", "中学", "速さ", []),
    ("p_density",  "science", "中学", "密度", []),
    ("p_press",    "science", "中学", "圧力", []),
    ("p_ohm",      "science", "中学", "オームの法則", ["p_other"]),
]

# (category, title) → 単元。英単語は難しさで分ける。
TITLE_UNIT = {}
def _m(unit, *titles):
    for t in titles: TITLE_UNIT[t] = unit
_m("m_signed", "正負の数"); _m("m_expr", "式の値"); _m("m_sqrt", "平方根", "根号を含む式の値")
_m("m_linear", "一次方程式"); _m("m_simul", "連立方程式"); _m("m_ineq", "不等式")
_m("m_factor", "因数分解"); _m("m_quad", "二次方程式"); _m("m_func2", "関数 y = ax²")
_m("m_pythag", "三平方の定理"); _m("m_polygon", "多角形の角", "正五角形と角", "正六角形の面積")
_m("m_prob", "確率", "確率の値"); _m("m_int", "倍数の個数", "整数の文章題")
_m("h_quadfunc", "二次関数の最小値", "放物線の頂点", "定義域つき最小値")
_m("h_trig", "三角比", "余弦定理", "三角形の面積"); _m("h_logic", "必要条件・十分条件")
_m("h_abs", "絶対値と不等式"); _m("h_count", "順列", "組合せ", "組分け")
_m("h_prob", "確率（組合せ）", "最大値の確率"); _m("h_nt", "約数の個数", "不定方程式", "整数の割り切れ")
_m("h_quadeq", "重解条件", "二次方程式の解")
_m("h_exp", "対数", "指数方程式"); _m("h_seq", "等差数列", "Σの計算", "漸化式", "等比数列の和")
_m("h_binom", "二項定理"); _m("h_circle", "円の方程式"); _m("h_trig2", "三角方程式の解の個数")
_m("h_diff", "導関数", "微分係数", "極大値", "三次方程式の実数解")
_m("h_integ", "不定積分", "定積分", "囲まれた面積"); _m("h_vec", "ベクトルの大きさ", "内積")
_m("h_limit", "数列の極限", "関数の極限", "無限等比級数", "三角関数の極限")
_m("h_diff3", "合成関数の微分", "いろいろな関数の微分")
_m("h_integ3", "部分積分", "対数関数の積分", "sin³x の積分", "回転体の体積", "サイクロイドの長さ")
_m("h_complex", "複素数の累乗", "複素数の絶対値", "複素数の偏角", "ド・モアブルの定理", "1の5乗根")
_m("h_conic", "楕円の焦点"); _m("h_space", "四面体の体積")
_m("g_grammar", "英語の文法"); _m("g_translate", "英文の和訳")
_m("s_geo", "地理"); _m("s_hist", "歴史"); _m("s_civ", "公民")
_m("b_all", "生物"); _m("c_all", "化学"); _m("e_all", "地学")
_m("p_other", "物理"); _m("p_speed", "速さ"); _m("p_density", "密度"); _m("p_press", "圧力")
_m("p_ohm", "オームの法則")


def unit_of(p):
    if p["category"] == "eng_word":
        return "w_basic" if p["difficulty"] <= 1 else "w_std"
    return TITLE_UNIT[p["title"]]


def units_json():
    return [dict(id=i, subject=s, stage=st, name=n, order=k, prereqs=pre)
            for k, (i, s, st, n, pre) in enumerate(UNITS)]
