"""英語の新しい単元（不規則動詞、前置詞、語形変化、同意語・反意語）。表から4択問題を作る。"""
import gen_content as C

R = C.R
qa = C.qa

# 不規則動詞：(原形, 過去形, 過去分詞, 意味)
IRREG = [
    ("be", "was/were", "been", "～である"), ("begin", "began", "begun", "始める"), ("break", "broke", "broken", "こわす"), ("bring", "brought", "brought", "持ってくる"),
    ("build", "built", "built", "建てる"), ("buy", "bought", "bought", "買う"), ("catch", "caught", "caught", "つかまえる"), ("choose", "chose", "chosen", "選ぶ"),
    ("come", "came", "come", "来る"), ("cut", "cut", "cut", "切る"), ("do", "did", "done", "する"), ("draw", "drew", "drawn", "描く"),
    ("drink", "drank", "drunk", "飲む"), ("drive", "drove", "driven", "運転する"), ("eat", "ate", "eaten", "食べる"), ("fall", "fell", "fallen", "落ちる"),
    ("feel", "felt", "felt", "感じる"), ("fight", "fought", "fought", "戦う"), ("find", "found", "found", "見つける"), ("fly", "flew", "flown", "飛ぶ"),
    ("forget", "forgot", "forgotten", "忘れる"), ("get", "got", "got/gotten", "手に入れる"), ("give", "gave", "given", "与える"), ("go", "went", "gone", "行く"),
    ("grow", "grew", "grown", "成長する"), ("have", "had", "had", "持っている"), ("hear", "heard", "heard", "聞こえる"), ("hide", "hid", "hidden", "隠す"),
    ("hit", "hit", "hit", "打つ"), ("hold", "held", "held", "持つ"), ("keep", "kept", "kept", "保つ"), ("know", "knew", "known", "知っている"),
    ("lead", "led", "led", "導く"), ("leave", "left", "left", "去る"), ("lend", "lent", "lent", "貸す"), ("let", "let", "let", "させる"),
    ("lose", "lost", "lost", "失う"), ("make", "made", "made", "作る"), ("mean", "meant", "meant", "意味する"), ("meet", "met", "met", "会う"),
    ("pay", "paid", "paid", "払う"), ("put", "put", "put", "置く"), ("read", "read", "read", "読む"), ("ride", "rode", "ridden", "乗る"),
    ("ring", "rang", "rung", "鳴る"), ("rise", "rose", "risen", "のぼる"), ("run", "ran", "run", "走る"), ("say", "said", "said", "言う"),
    ("see", "saw", "seen", "見える"), ("sell", "sold", "sold", "売る"), ("send", "sent", "sent", "送る"), ("set", "set", "set", "置く・設定する"),
    ("shake", "shook", "shaken", "振る"), ("shine", "shone", "shone", "輝く"), ("show", "showed", "shown", "見せる"), ("shut", "shut", "shut", "閉める"),
    ("sing", "sang", "sung", "歌う"), ("sit", "sat", "sat", "すわる"), ("sleep", "slept", "slept", "眠る"), ("speak", "spoke", "spoken", "話す"),
    ("spend", "spent", "spent", "費やす"), ("stand", "stood", "stood", "立つ"), ("steal", "stole", "stolen", "ぬすむ"), ("swim", "swam", "swum", "泳ぐ"),
    ("take", "took", "taken", "取る"), ("teach", "taught", "taught", "教える"), ("tell", "told", "told", "伝える"), ("think", "thought", "thought", "考える"),
    ("throw", "threw", "thrown", "投げる"), ("understand", "understood", "understood", "理解する"), ("wake", "woke", "woken", "目を覚ます"),
    ("wear", "wore", "worn", "着ている"), ("win", "won", "won", "勝つ"), ("write", "wrote", "written", "書く"),
]


def _wrongs(correct, first, pool):
    """正解と重ならない、3つのまちがい。first を優先し、足りなければ pool（混ぜ済み）から。"""
    out = []
    for w in list(first) + list(pool):
        if w != correct and w not in out: out.append(w)
        if len(out) == 3: break
    return out


def irregular():
    pasts = sorted({v[1] for v in IRREG})
    pps = sorted({v[2] for v in IRREG})
    for base, past, pp, ja in IRREG:
        regular = base + ("d" if base.endswith("e") else "ed")
        pool = list(pasts); R.shuffle(pool)
        qa("eng_sentence", "g_irreg", "不規則動詞", 1, f"「{base}」（{ja}）の過去形はどれか。", past, _wrongs(past, [regular, base, pp], pool), f"{base} - {past} - {pp}")
        if pp != past:
            pool = list(pps); R.shuffle(pool)
            qa("eng_sentence", "g_irreg", "不規則動詞", 2, f"「{base}」（{ja}）の過去分詞はどれか。", pp, _wrongs(pp, [regular, past, base], pool), f"{base} - {past} - {pp}")


# 前置詞・冠詞など：(難しさ, 文, 正解, まちがい3つ, 解説)
PREP = [
    (1, "I get up （ ） six every morning.", "at", ["in", "on", "to"], "時刻の前は at。"),
    (1, "My birthday is （ ） May.", "in", ["at", "on", "to"], "月の前は in。"),
    (1, "We have a party （ ） Sunday.", "on", ["in", "at", "by"], "曜日の前は on。"),
    (1, "She came to Japan （ ） 2019.", "in", ["on", "at", "for"], "年の前は in。"),
    (1, "I go to school （ ） bus.", "by", ["with", "in", "on"], "乗り物を使う手段は by。"),
    (1, "Write your name （ ） a pen.", "with", ["by", "in", "on"], "道具を使うときは with。"),
    (1, "He is good （ ） English.", "at", ["in", "on", "for"], "be good at ～ は「～が得意」。"),
    (1, "I'm interested （ ） music.", "in", ["at", "on", "of"], "be interested in ～ は「～に興味がある」。"),
    (1, "She is afraid （ ） dogs.", "of", ["at", "in", "to"], "be afraid of ～ は「～がこわい」。"),
    (1, "Thank you （ ） your help.", "for", ["of", "to", "at"], "thank you for ～ は「～をありがとう」。"),
    (1, "I live （ ） Tokyo.", "in", ["at", "on", "by"], "広い場所（都市）の前は in。"),
    (1, "The book is （ ） the table.", "on", ["in", "at", "to"], "接している上は on。"),
    (1, "There is a cat （ ） the chair.", "under", ["over", "on", "at"], "「～の下に」は under。"),
    (1, "The bank is （ ） the station and the school.", "between", ["among", "under", "beside"], "2つの間は between。"),
    (1, "He walked （ ） the park.", "through", ["across", "on", "at"], "「～を通り抜けて」は through。"),
    (2, "I have lived here （ ） ten years.", "for", ["since", "during", "from"], "期間の長さは for。"),
    (2, "I have lived here （ ） 2015.", "since", ["for", "from", "in"], "「～以来」は since。"),
    (2, "I'll wait here （ ） you come back.", "until", ["by", "for", "since"], "「～まで（ずっと）」は until。"),
    (2, "Please come back （ ） five o'clock.", "by", ["until", "for", "in"], "「～までに」は by。"),
    (2, "It rained a lot （ ） the night.", "during", ["for", "while", "since"], "特定の期間中は during。"),
    (2, "I was reading a book （ ） he was cooking.", "while", ["during", "for", "until"], "while は接続詞で、あとに文が続く。"),
    (2, "He is looking （ ） his key.", "for", ["at", "after", "to"], "look for ～ は「～をさがす」。"),
    (2, "She takes care （ ） her little sister.", "of", ["to", "for", "at"], "take care of ～ は「～の世話をする」。"),
    (2, "I'm looking forward （ ） the trip.", "to", ["for", "at", "on"], "look forward to ～ は「～を楽しみに待つ」。"),
    (2, "He was born （ ） Osaka （ ） 2005.", "in / in", ["at / in", "in / on", "on / at"], "場所（都市）にも年にも in。"),
    (1, "I have （ ） apple.", "an", ["a", "the", "some"], "母音で始まる語の前は an。"),
    (1, "She plays （ ） piano.", "the", ["a", "an", "（なし）"], "楽器の前には the をつける。"),
    (1, "I play （ ） tennis after school.", "（なし）", ["the", "a", "an"], "スポーツ名の前には冠詞をつけない。"),
    (2, "The sun rises in （ ） east.", "the", ["a", "an", "（なし）"], "方位には the をつける。"),
    (2, "He is （ ） tallest boy in our class.", "the", ["a", "an", "（なし）"], "最上級の前には the をつける。"),
    (1, "I want to go （ ） the library.", "to", ["at", "in", "on"], "「～へ行く」は go to ～。"),
    (1, "She is waiting （ ） the bus stop.", "at", ["in", "on", "to"], "地点を表すときは at。"),
    (2, "The meeting starts （ ） nine.", "at", ["on", "in", "by"], "時刻は at。"),
    (2, "He arrived （ ） Kyoto yesterday.", "in", ["at", "to", "on"], "到着する都市は arrive in。"),
    (2, "We arrived （ ） the station at noon.", "at", ["in", "to", "on"], "到着する小さな地点は arrive at。"),
    (2, "This is a letter （ ） my friend.", "from", ["to", "of", "at"], "「～から（の）」は from。"),
    (1, "I'm going to send it （ ） email.", "by", ["on", "with", "in"], "手段は by。"),
    (2, "He spoke （ ） a loud voice.", "in", ["with", "by", "on"], "in a loud voice は「大声で」。"),
    (2, "The singer is famous （ ） her songs.", "for", ["of", "at", "to"], "be famous for ～ は「～で有名」。"),
    (2, "This sweater is made （ ） wool.", "of", ["from", "by", "in"], "材料が見てわかるときは be made of ～。"),
    (2, "Wine is made （ ） grapes.", "from", ["of", "by", "in"], "原料が見てわからないときは be made from ～。"),
    (2, "I'm proud （ ） my school.", "of", ["at", "in", "for"], "be proud of ～ は「～を誇りに思う」。"),
]

PLURAL = [("child", "children"), ("man", "men"), ("woman", "women"), ("foot", "feet"), ("tooth", "teeth"), ("mouse", "mice"), ("person", "people"),
          ("knife", "knives"), ("leaf", "leaves"), ("wife", "wives"), ("life", "lives"), ("wolf", "wolves"), ("city", "cities"), ("baby", "babies"),
          ("box", "boxes"), ("bus", "buses"), ("watch", "watches"), ("dish", "dishes"), ("potato", "potatoes"), ("tomato", "tomatoes"), ("piano", "pianos"), ("photo", "photos"),
          ("sheep", "sheep"), ("fish", "fish"), ("country", "countries"), ("day", "days"), ("boy", "boys"), ("class", "classes")]
COMPARE = [("good", "better", "best"), ("well", "better", "best"), ("bad", "worse", "worst"), ("many", "more", "most"), ("much", "more", "most"),
           ("little", "less", "least"), ("big", "bigger", "biggest"), ("hot", "hotter", "hottest"), ("large", "larger", "largest"), ("happy", "happier", "happiest"),
           ("easy", "easier", "easiest"), ("early", "earlier", "earliest"), ("busy", "busier", "busiest"), ("famous", "more famous", "most famous"),
           ("beautiful", "more beautiful", "most beautiful"), ("difficult", "more difficult", "most difficult"), ("tall", "taller", "tallest"),
           ("long", "longer", "longest"), ("thin", "thinner", "thinnest"), ("far", "farther", "farthest"), ("old", "older", "oldest"), ("pretty", "prettier", "prettiest"),
           ("important", "more important", "most important"), ("interesting", "more interesting", "most interesting")]


def forms():
    plurals = [p for _, p in PLURAL]
    for sg, pl in PLURAL:
        wr = [sg + "s", sg + "es", sg + "ies"]
        if sg.endswith("y"): wr = [sg + "s", sg + "es", sg[:-1] + "s"]
        if sg.endswith("f") or sg.endswith("fe"): wr = [sg + "s", sg + "es", (sg[:-1] if sg.endswith("f") else sg[:-2]) + "ves" if False else sg + "ies"]
        wr = [w for w in dict.fromkeys(wr) if w != pl]
        extra = [p for p in plurals if p != pl]; R.shuffle(extra)
        while len(wr) < 3: wr.append(extra.pop())
        qa("eng_sentence", "g_form", "語形変化", 1, f"「{sg}」の複数形はどれか。", pl, wr[:3], f"{sg} の複数形は {pl}。")
    for base, comp, sup in COMPARE:
        er = base + "r" if base.endswith("e") else base + "er"
        est = base + "st" if base.endswith("e") else base + "est"
        pool_c = ["more " + base, "most " + base, sup, base + "ier", base + "est", er + "r", "gooder", "more good"]
        qa("eng_sentence", "g_form", "語形変化", 2, f"「{base}」の比較級はどれか。", comp, _wrongs(comp, [er, "more " + base, sup], pool_c), f"{base} の比較級は {comp}、最上級は {sup}。")
        pool_s = ["most " + base, "more " + base, comp, base + "iest", er, est + "t", "bestest", "most good"]
        qa("eng_sentence", "g_form", "語形変化", 2, f"「{base}」の最上級はどれか。", sup, _wrongs(sup, [est, "most " + base, comp], pool_s), f"{base} の比較級は {comp}、最上級は {sup}。")


# 同意語・反意語：(単語, 意味が近い語, 反対の語)
SYN = [("big", "large", "small"), ("start", "begin", "finish"), ("buy", "purchase", "sell"), ("quick", "fast", "slow"), ("begin", "start", "end"),
       ("smart", "clever", "stupid"), ("rich", "wealthy", "poor"), ("hard", "difficult", "easy"), ("glad", "happy", "sad"), ("kind", "gentle", "cruel"),
       ("huge", "enormous", "tiny"), ("sleepy", "drowsy", "awake"), ("close", "shut", "open"), ("strong", "powerful", "weak"), ("top", "peak", "bottom"),
       ("answer", "reply", "ask"), ("tired", "exhausted", "energetic"), ("quiet", "silent", "noisy"), ("help", "assist", "hinder"), ("choose", "select", "reject"),
       ("often", "frequently", "seldom"), ("empty", "vacant", "full"), ("clear", "obvious", "vague"), ("rapid", "quick", "gradual"), ("ancient", "old", "modern"),
       ("expand", "extend", "shrink"), ("increase", "grow", "decrease"), ("accept", "receive", "refuse"), ("allow", "permit", "forbid"), ("arrive", "reach", "depart")]


def synonyms():
    syns = [s for _, s, _ in SYN]; ants = [a for _, _, a in SYN]
    for w, s, a in SYN:
        others = [x for x in syns + ants if x not in (s, a, w)]; R.shuffle(others)
        qa("eng_word", "w_syn", "同意語・反意語", 2, f"「{w}」に意味が最も近い語はどれか。", s, [a] + others[:2], f"{w} と {s} は近い意味。{w} の反対は {a}。")
        others = [x for x in syns + ants if x not in (s, a, w)]; R.shuffle(others)
        qa("eng_word", "w_syn", "同意語・反意語", 2, f"「{w}」の反対の意味の語はどれか。", a, [s] + others[:2], f"{w} の反対は {a}。")


def generate():
    irregular()
    for diff, body, correct, wrongs, expl in PREP:
        qa("eng_sentence", "g_prep", "前置詞と冠詞", diff, "次の文の（ ）に入るものを選べ。　" + body, correct, wrongs, expl)
    forms()
    synonyms()
