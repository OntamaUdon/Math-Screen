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
    ("e_avg",      "math", "小学", "平均", ["e_calc"]),
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
    ("m_prop",     "math", "中学", "比例・反比例", ["m_expr"]),
    ("m_linfunc",  "math", "中学", "一次関数", ["m_prop", "m_linear"]),
    ("m_algebra",  "math", "中学", "文字式の計算", ["m_signed"]),
    ("m_similar",  "math", "中学", "相似", ["m_prop"]),
    ("m_circle",   "math", "中学", "円と角", ["m_polygon"]),
    ("m_space",    "math", "中学", "立体の体積と表面積", ["m_pythag"]),
    ("m_data",     "math", "中学", "データの活用", ["e_calc"]),
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
    ("h_seq2",     "math", "高校", "数列の応用", ["h_seq"]),
    ("h_diff2",    "math", "高校", "微分の応用", ["h_diff"]),
    ("h_geom",     "math", "高校", "図形の性質", ["m_similar"]),
    ("h_stat",     "math", "高校", "データの分析", ["m_data"]),
    ("h_cplx",     "math", "高校", "複素数と方程式", ["h_quadeq"]),
    # ── 英語 ──
    ("w_basic",    "english", "中学", "基本の英単語", []),
    ("w_std",      "english", "高校", "標準の英単語", ["w_basic"]),
    ("w_adv",      "english", "高校", "入試レベルの英単語", ["w_std"]),
    ("g_grammar",  "english", "中学", "英語の文法", []),
    ("g_translate", "english", "中学", "英文の和訳", ["g_grammar"]),
    ("g_order",    "english", "中学", "英文の並べかえ", ["g_grammar"]),
    ("g_irreg",    "english", "中学", "不規則動詞", ["g_grammar"]),
    ("g_prep",     "english", "中学", "前置詞と冠詞", ["g_grammar"]),
    ("g_form",     "english", "中学", "語形変化", ["g_grammar"]),
    ("w_syn",      "english", "高校", "同意語・反意語", ["w_basic"]),
    # ── 国語 ──
    ("j_kanji_read",  "japanese", "中学", "漢字の読み", []),
    ("j_kanji_write", "japanese", "中学", "漢字の書き取り", []),
    ("j_idiom",       "japanese", "中学", "四字熟語", []),
    ("j_proverb",     "japanese", "中学", "ことわざ・慣用句", []),
    ("j_grammar",     "japanese", "中学", "国語の文法", []),
    ("j_classic",     "japanese", "高校", "古文単語", ["j_grammar"]),
    # ── 社会 ──
    ("s_geo_map",   "social", "中学", "地球と地図", []),
    ("s_geo_world", "social", "中学", "世界の国々", ["s_geo_map"]),
    ("s_geo_japan", "social", "中学", "日本の地理", ["s_geo_map"]),
    ("s_hist_ancient",  "social", "中学", "古代の歴史", []),
    ("s_hist_medieval", "social", "中学", "中世の歴史", ["s_hist_ancient"]),
    ("s_hist_early",    "social", "中学", "近世の歴史", ["s_hist_medieval"]),
    ("s_hist_modern",   "social", "中学", "近代の歴史", ["s_hist_early"]),
    ("s_hist_contemp",  "social", "中学", "現代の歴史", ["s_hist_modern"]),
    ("s_geo_asia", "social", "中学", "アジア州", ["s_geo_world"]),
    ("s_geo_europe", "social", "中学", "ヨーロッパ・アフリカ", ["s_geo_world"]),
    ("s_geo_americas", "social", "中学", "南北アメリカ・オセアニア", ["s_geo_world"]),
    ("s_jp_region", "social", "中学", "日本の諸地域", ["s_geo_japan"]),
    ("s_jp_industry", "social", "中学", "日本の産業", ["s_geo_japan"]),
    ("s_civ_const", "social", "中学", "憲法と人権", []),
    ("s_civ_gov",   "social", "中学", "政治のしくみ", ["s_civ_const"]),
    ("s_civ_econ",  "social", "中学", "経済のしくみ", ["s_civ_gov"]),
    ("s_civ_intl",  "social", "中学", "国際社会", ["s_civ_gov"]),
    # ── 理科 ──
    ("b_cell_plant", "science", "中学", "細胞と植物", []),
    ("b_human",      "science", "中学", "人体のつくり", ["b_cell_plant"]),
    ("b_eco",        "science", "中学", "生態系", ["b_cell_plant"]),
    ("b_genetic",    "science", "中学", "遺伝と進化", ["b_cell_plant"]),
    ("b_animal",     "science", "中学", "動物の分類", []),
    ("c_ion",        "science", "中学", "イオンと電池", ["c_atom"]),
    ("p_energy",     "science", "中学", "エネルギー", ["p_elec"]),
    ("c_atom",       "science", "中学", "物質と原子", []),
    ("c_state",      "science", "中学", "物質の性質", []),
    ("c_solution",   "science", "中学", "水溶液と酸・アルカリ", ["c_atom"]),
    ("c_reaction",   "science", "中学", "化学変化", ["c_atom"]),
    ("p_elec",       "science", "中学", "電気", []),
    ("p_force",      "science", "中学", "力と圧力", []),
    ("p_motion",     "science", "中学", "運動と仕事", ["p_force"]),
    ("p_wave",       "science", "中学", "光と音", []),
    ("e_space",      "science", "中学", "天体", []),
    ("e_land",       "science", "中学", "大地の変化", []),
    ("e_weather",    "science", "中学", "天気", []),
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
_m("h_conic", "楕円の焦点"); _m("h_space", "四面体の体積", "直方体の対角線", "角錐の体積", "球の体積と表面積")
_m("h_trig2", "弧度法", "三角関数の値")
_m("h_integ3", "三角関数・指数関数の積分", "合成関数の積分"); _m("h_quadeq", "判別式"); _m("h_exp", "指数の計算"); _m("h_count", "最短経路")
_m("h_prob", "期待値"); _m("h_conic", "放物線の焦点", "双曲線の焦点", "楕円の長軸"); _m("h_nt", "最大公約数と互除法"); _m("h_circle", "図形と方程式"); _m("h_logic", "集合の要素の個数", "命題の対偶")
_m("g_grammar", "英語の文法"); _m("g_translate", "英文の和訳")
_m("p_elec", "オームの法則"); _m("p_motion", "速さ"); _m("c_state", "密度"); _m("p_force", "圧力")

# 最初からあった社会・理科の問題（id が s-分野-番号）は、内容に合わせて単元を決める
BY_ID = {}
def _ids(cat, unit, *nums):
    for n in nums: BY_ID[f"s-{cat}-{n}"] = unit
_ids("soc_geo", "s_geo_japan", 1, 2, 3, 4); _ids("soc_geo", "s_geo_world", 5, 6, 7); _ids("soc_geo", "s_geo_map", 8, 9, 10)
_ids("soc_hist", "s_hist_medieval", 1, 10); _ids("soc_hist", "s_hist_early", 2, 7); _ids("soc_hist", "s_hist_modern", 3, 4, 9, 12)
_ids("soc_hist", "s_hist_ancient", 5, 6); _ids("soc_hist", "s_hist_contemp", 8, 11)
_ids("soc_civ", "s_civ_const", 1); _ids("soc_civ", "s_civ_gov", 2, 3, 4, 5, 6, 7, 12); _ids("soc_civ", "s_civ_econ", 8, 9, 11)
_ids("soc_civ", "s_civ_intl", 10)
_ids("sci_bio", "b_cell_plant", 1, 3, 4); _ids("sci_bio", "b_human", 2, 5, 6); _ids("sci_bio", "b_eco", 7)
_ids("sci_chem", "c_atom", 1, 2, 3); _ids("sci_chem", "c_solution", 4, 5); _ids("sci_chem", "c_reaction", 6); _ids("sci_chem", "c_state", 7)
_ids("sci_phys", "p_force", 1); _ids("sci_phys", "p_elec", 2, 3); _ids("sci_phys", "p_wave", 4); _ids("sci_phys", "p_motion", 5)
_ids("sci_earth", "e_space", 1, 2, 3, 4); _ids("sci_earth", "e_land", 5, 6)


_m("e_calc", "計算の順序", "かっこのある計算", "くふうした計算", "かけ算の筆算", "あまりのあるわり算")
_m("e_decfrac", "小数のかけ算", "分数のたし算", "約分", "小数の位取り", "単位の換算")
_m("e_divmult", "最大公約数", "最小公倍数", "約数を数える", "倍数を数える", "素数")
_m("e_ratio", "割合", "比", "比で分ける", "割引", "食塩水の濃さ")
_m("e_speed", "速さを求める", "時間を求める", "道のりを求める", "出会うまでの時間")
_m("e_geom", "三角形の面積", "台形の面積", "円の面積", "円周の長さ", "直方体の体積", "立方体の表面積", "三角形の角度")
_m("e_count", "並べ方", "組み合わせ", "さいころの目", "選び方の組")


_m("e_avg", "平均")
_m("s_geo_asia", "アジア州"); _m("s_geo_europe", "ヨーロッパ・アフリカ"); _m("s_geo_americas", "南北アメリカ・オセアニア"); _m("s_jp_region", "日本の諸地域"); _m("s_jp_industry", "日本の産業")
_m("b_genetic", "遺伝と進化"); _m("b_animal", "動物の分類"); _m("c_ion", "イオンと電池"); _m("p_energy", "エネルギー")
_m("g_irreg", "不規則動詞"); _m("g_prep", "前置詞と冠詞"); _m("g_form", "語形変化"); _m("w_syn", "同意語・反意語")
_m("m_prop", "比例", "反比例"); _m("m_linfunc", "一次関数"); _m("m_algebra", "文字式の計算"); _m("m_similar", "相似")
_m("m_circle", "円周角"); _m("m_space", "立体の体積と表面積"); _m("m_data", "平均値と中央値")
_m("h_seq2", "階差数列"); _m("h_diff2", "微分の応用"); _m("h_geom", "角の二等分線", "方べきの定理", "三角形の性質")
_m("h_stat", "データの分散"); _m("h_cplx", "複素数の計算")


def unit_of(p):
    if p.get("unit"): return p["unit"]
    if p["id"] in BY_ID: return BY_ID[p["id"]]
    if p["category"] == "eng_word":
        return "w_basic" if p["difficulty"] <= 1 else "w_std"
    return TITLE_UNIT[p["title"]]


def units_json():
    return [dict(id=i, subject=s, stage=st, name=n, order=k, prereqs=pre)
            for k, (i, s, st, n, pre) in enumerate(UNITS)]
