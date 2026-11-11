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
    ("m_expand",   "math", "中学", "展開と因数分解の公式", ["m_factor"]),
    ("m_quad_word", "math", "中学", "二次方程式の利用", ["m_quad"]),
    ("m_pythag_use", "math", "中学", "三平方の定理の利用", ["m_pythag"]),
    ("m_simul_word", "math", "中学", "連立方程式の利用", ["m_simul"]),
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
    ("h_integ_app", "math", "高校", "微積の応用", ["h_integ"]),
    ("h_addition", "math", "高校", "三角関数の加法定理", ["h_trig2"]),
    ("h_diff2",    "math", "高校", "微分の応用", ["h_diff"]),
    ("h_geom",     "math", "高校", "図形の性質", ["m_similar"]),
    ("h_stat",     "math", "高校", "データの分析", ["m_data"]),
    ("h_cplx",     "math", "高校", "複素数と方程式", ["h_quadeq"]),
    # ── 足りなかった単元（2026年11月に追加）──
    ("e_round",    "math", "小学", "概数と見積もり", ["e_calc"]),
    ("e_unit",     "math", "小学", "単位量あたりの大きさ", ["e_decfrac"]),
    ("e_shape",    "math", "小学", "合同・対称・拡大図", ["e_geom"]),
    ("m_parallel", "math", "中学", "平行線と線分の比", ["m_similar"]),
    ("m_boxplot",  "math", "中学", "箱ひげ図と標本調査", ["m_data"]),
    ("h_sine",     "math", "高校", "正弦定理と三角形の面積", ["h_trig"]),
    ("h_center",   "math", "高校", "三角形の五心とチェバ・メネラウス", ["h_geom"]),
    ("h_condprob", "math", "高校", "条件付き確率", ["h_prob"]),
    ("h_nbase",    "math", "高校", "n 進法", ["h_nt"]),
    ("h_remainder","math", "高校", "剰余の定理と解と係数の関係", ["h_cplx"]),
    ("h_line",     "math", "高校", "点と直線・軌跡と領域", ["h_circle"]),
    ("h_compose",  "math", "高校", "三角関数の合成", ["h_addition"]),
    ("h_divpt",    "math", "高校", "内分点・外分点とベクトル", ["h_vec"]),
    ("h_statinf",  "math", "高校", "確率分布と統計的な推測", ["h_prob"]),
    ("h_curve",    "math", "高校", "媒介変数と極座標", ["h_conic"]),
    ("h_func3",    "math", "高校", "いろいろな関数（分数・無理・逆関数）", ["h_quadfunc"]),
    ("h_graph",    "math", "高校", "グラフの凹凸と漸近線", ["h_diff3"]),
    # ── 英語 ──
    ("w_basic",    "english", "中学", "基本の英単語", []),
    ("w_std",      "english", "高校", "標準の英単語", ["w_basic"]),
    ("w_adv",      "english", "高校", "上級の英単語", ["w_std"]),
    ("g_grammar",  "english", "中学", "英語の文法", []),
    ("g_translate", "english", "中学", "英文の和訳", ["g_grammar"]),
    ("g_order",    "english", "中学", "英文の並べかえ", ["g_grammar"]),
    ("g_modal",    "english", "中学", "助動詞", ["g_grammar"]),
    ("g_infinitive", "english", "中学", "不定詞・動名詞", ["g_grammar"]),
    ("g_passive",  "english", "中学", "受け身", ["g_grammar", "g_irreg"]),
    ("g_perfect",  "english", "中学", "現在完了", ["g_irreg"]),
    ("g_relative", "english", "中学", "関係代名詞", ["g_grammar"]),
    ("g_subjunctive", "english", "高校", "仮定法", ["g_modal", "g_perfect"]),
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
    ("j_keigo",       "japanese", "中学", "敬語", ["j_grammar"]),
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
    ("s_hist_meiji", "social", "中学", "明治維新", ["s_hist_edo"]),
    ("s_geo_climate", "social", "中学", "日本の気候区分", ["s_geo_japan"]),
    ("s_civ_trade", "social", "中学", "貿易と為替・金融", ["s_civ_econ"]),
    ("s_hist_edo", "social", "中学", "江戸時代の文化と政治", ["s_hist_early"]),
    ("s_hist_war", "social", "中学", "戦争と民主化", ["s_hist_modern"]),
    ("s_civ_local", "social", "中学", "地方自治", ["s_civ_gov"]),
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
    ("c_mass",       "science", "中学", "化学変化と質量", ["c_reaction"]),
    ("c_redox",      "science", "中学", "酸化と還元", ["c_reaction"]),
    ("p_balance",    "science", "中学", "力のつり合い", ["p_force"]),
    ("p_magnet",     "science", "中学", "電流と磁界", ["p_elec"]),
    ("e_front",      "science", "中学", "前線と気団", ["e_weather"]),
    ("b_photo",      "science", "中学", "光合成と呼吸", ["b_cell_plant"]),
    ("b_digest",     "science", "中学", "消化と吸収", ["b_human"]),
    ("p_record",     "science", "中学", "運動の記録", ["p_motion"]),
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
    # ── 高校：理科・社会 ──
    ("hp_motion",  "science", "高校", "等加速度運動", ["m_func2"]),
    ("hp_force",   "science", "高校", "運動の法則", ["hp_motion"]),
    ("hp_energy",  "science", "高校", "仕事とエネルギー", ["hp_force"]),
    ("hp_wave",    "science", "高校", "波と音", ["hp_motion"]),
    ("hp_circuit", "science", "高校", "電気回路", ["p_elec"]),
    ("hc_mol",     "science", "高校", "物質量と化学反応式", ["c_reaction"]),
    ("hc_acid",    "science", "高校", "酸・塩基と pH", ["hc_mol"]),
    ("hc_struct",  "science", "高校", "原子の構造と化学結合", ["c_atom"]),
    ("hc_org",     "science", "高校", "有機化合物", ["hc_struct"]),
    ("hb_cell",    "science", "高校", "細胞とエネルギー代謝", ["b_cell_plant"]),
    ("hb_dna",     "science", "高校", "遺伝子とDNA", ["b_genetic"]),
    ("hb_body",    "science", "高校", "体内環境の維持", ["b_human"]),
    ("he_earth",   "science", "高校", "地球のしくみ", ["e_land"]),
    ("he_atmo",    "science", "高校", "大気・海洋・宇宙", ["e_weather", "e_space"]),
    ("hs_jp_ancmed", "social", "高校", "日本史：古代〜中世", ["s_hist_ancient"]),
    ("hs_jp_early",  "social", "高校", "日本史：近世", ["hs_jp_ancmed"]),
    ("hs_jp_modern", "social", "高校", "日本史：近代", ["hs_jp_early"]),
    ("hs_jp_contemp", "social", "高校", "日本史：現代", ["hs_jp_modern"]),
    ("hs_w_ancient", "social", "高校", "世界史：古代文明と帝国", []),
    ("hs_w_medieval", "social", "高校", "世界史：中世のヨーロッパ・イスラーム・アジア", ["hs_w_ancient"]),
    ("hs_w_early",   "social", "高校", "世界史：近世・革命の時代", ["hs_w_medieval"]),
    ("hs_w_20c",     "social", "高校", "世界史：帝国主義と二つの世界大戦・現代", ["hs_w_early"]),
    ("hs_geo_nature", "social", "高校", "地理：地形と気候", ["s_geo_climate"]),
    ("hs_geo_industry", "social", "高校", "地理：資源・産業", ["s_jp_industry"]),
    ("hs_geo_pop",   "social", "高校", "地理：人口・都市・環境問題", ["s_geo_world"]),
    ("hs_civ_politics", "social", "高校", "民主政治と日本の政治制度", ["s_civ_gov"]),
    ("hs_civ_econ",  "social", "高校", "市場経済と国際経済", ["s_civ_econ"]),
    ("hs_ethics",    "social", "高校", "倫理（思想家）", []),
    # ── ノンジャンル：発展内容（指導要領の外）──
    ("tm_adv",   "math", "ノンジャンル", "発展内容（指導要領の外）", []),
    ("te_adv",   "english", "ノンジャンル", "発展内容（指導要領の外）", []),
    ("ts_adv",   "social", "ノンジャンル", "発展内容（指導要領の外）", []),
    ("tsc_adv",  "science", "ノンジャンル", "発展内容（指導要領の外）", []),
    ("tj_adv",   "japanese", "ノンジャンル", "発展内容（指導要領の外）", []),
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
_m("m_expand", "展開と因数分解の公式"); _m("m_quad_word", "二次方程式の利用"); _m("m_pythag_use", "三平方の定理の利用"); _m("h_integ_app", "面積と速度")
_m("m_simul_word", "連立方程式の文章題"); _m("h_addition", "加法定理")
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


# マップで、段階の下にひとまとめにする名前（枝が10個を超える所で、アプリが使う）
_GROUPS = {
    "数と計算": "e_calc e_decfrac e_divmult e_round",
    "量と図形": "e_geom e_speed e_unit e_shape",
    "変化と関係・データ": "e_ratio e_count e_avg",
    "数と式": "m_signed m_expr m_algebra m_expand m_factor m_sqrt m_int",
    "方程式・不等式": "m_linear m_simul m_simul_word m_ineq m_quad m_quad_word",
    "関数": "m_prop m_linfunc m_func2",
    "図形": "m_polygon m_pythag m_pythag_use m_similar m_parallel m_circle m_space",
    "データと確率": "m_prob m_data m_boxplot",
    "数学I・A": "h_quadfunc h_quadeq h_trig h_sine h_logic h_abs h_count h_prob h_condprob h_nt h_nbase h_geom h_center h_stat",
    "数学II": "h_exp h_circle h_line h_trig2 h_addition h_compose h_cplx h_remainder h_binom h_diff h_diff2 h_integ h_integ_app",
    "数学B・C": "h_seq h_seq2 h_statinf h_vec h_divpt h_complex h_conic h_curve h_space",
    "数学III": "h_func3 h_limit h_diff3 h_graph h_integ3",
    "単語・語形": "w_basic g_irreg g_form",
    "文法": "g_grammar g_modal g_infinitive g_passive g_perfect g_relative g_prep",
    "和訳・並べかえ": "g_translate g_order",
}
GROUP = {u: g for g, ids in _GROUPS.items() for u in ids.split()}
_PREFIX_GROUP = {("science", "p"): "物理", ("science", "c"): "化学", ("science", "b"): "生物", ("science", "e"): "地学",
                 ("social", "geo"): "地理", ("social", "jp"): "地理", ("social", "hist"): "歴史", ("social", "civ"): "公民"}


_HS_SCIENCE = {"hp": "物理", "hc": "化学", "hb": "生物", "he": "地学"}
_HS_SOCIAL = {"jp": "日本史", "w": "世界史", "geo": "地理", "civ": "公民", "ethics": "公民"}


def group_of(uid, subject):
    if uid in GROUP: return GROUP[uid]
    head = uid.split("_")
    if subject == "science":
        return _HS_SCIENCE.get(head[0]) or _PREFIX_GROUP.get((subject, head[0]))
    if subject == "social":
        if head[0] == "hs": return _HS_SOCIAL.get(head[1])
        return _PREFIX_GROUP.get((subject, head[1]))
    return None


def units_json():
    out = []
    for k, (i, s, st, n, pre) in enumerate(UNITS):
        d = dict(id=i, subject=s, stage=st, name=n, order=k, prereqs=pre)
        g = group_of(i, s)
        if g: d["group"] = g
        out.append(d)
    return out


# 「入試の難問」の単元はなくした（本物の入試問題ではなく自作のため）。その問題は、内容に合う単元へ移す。
def _r(prefix, units):
    return {f"u-{prefix}-{i+1}": u for i, u in enumerate(units.split())}
HARD_REMAP = {}
HARD_REMAP.update(_r("tm_hard", """
h_exp h_exp h_nt h_count h_count h_count h_nt h_seq2 h_seq2 h_cplx
h_nt h_count h_seq2 h_space h_nt h_prob h_diff2 h_integ3 h_integ3 h_limit
h_diff3 h_integ3 h_integ3 h_diff2 h_seq2 h_nt h_prob h_prob h_circle h_trig
h_trig h_trig h_integ_app h_diff2 h_cplx h_cplx h_nt h_nt h_nt h_complex"""))
HARD_REMAP.update(_r("te_hard", """
g_subjunctive g_subjunctive g_grammar g_grammar g_grammar g_subjunctive g_infinitive g_infinitive g_grammar g_perfect
g_grammar g_grammar g_irreg g_grammar g_relative g_infinitive g_modal g_infinitive g_grammar g_relative
g_infinitive g_grammar g_grammar g_translate g_translate g_translate g_translate w_syn w_adv g_translate
g_translate g_translate g_infinitive g_translate g_modal g_subjunctive g_translate"""))
HARD_REMAP.update(_r("ts_hard", """
hs_jp_ancmed hs_jp_ancmed hs_jp_ancmed hs_jp_ancmed hs_jp_ancmed hs_w_early hs_w_early hs_w_early hs_w_20c hs_w_20c
hs_w_20c hs_jp_ancmed hs_jp_early hs_jp_early hs_jp_modern hs_jp_modern hs_jp_modern hs_jp_modern hs_geo_nature hs_geo_industry
hs_geo_industry s_hist_ancient s_hist_early s_hist_edo s_hist_edo s_hist_meiji s_hist_meiji hs_jp_modern s_hist_war s_hist_war
hs_w_early hs_w_early hs_w_early hs_w_20c hs_w_20c hs_w_20c hs_w_20c hs_w_20c s_civ_intl hs_geo_nature"""))
HARD_REMAP.update(_r("tsc_hard", """
hp_energy hp_energy hc_mol hc_acid hc_acid hc_mol hb_dna hb_dna he_atmo he_atmo
he_earth p_force p_energy hc_mol hb_cell hb_dna hp_circuit hp_circuit hp_motion p_force
hc_mol hp_force hp_motion hp_wave hp_wave hp_circuit p_elec hc_mol hc_mol c_solution
hc_mol hc_acid hp_energy hb_dna hb_dna e_land he_atmo hp_energy p_energy p_motion"""))
HARD_REMAP.update(_r("tj_hard", """
j_kanji_read j_kanji_read j_kanji_read j_kanji_read j_kanji_read j_kanji_read j_kanji_read j_kanji_read j_kanji_read j_idiom
j_idiom j_idiom j_proverb j_proverb j_proverb j_proverb j_proverb j_proverb j_proverb j_proverb
j_proverb j_proverb j_proverb j_kanji_write j_kanji_write j_proverb j_proverb j_classic j_grammar j_proverb
j_proverb j_idiom j_idiom j_kanji_read j_kanji_read j_kanji_read"""))
