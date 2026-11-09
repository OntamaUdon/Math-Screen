import SwiftUI

struct Problem: Codable, Identifiable, Hashable {
    let id: String
    let category: String
    let difficulty: Int
    let title: String
    let body: String       // LaTeX 混じり（$...$ が数式）。アプリ内の問題画面で KaTeX 表示
    let plain: String      // 文字だけの問題文。iOS のブロック画面は文字しか出せないのでこちらを使う
    let answer: Int        // 整数で答える問題は正解の数、4択問題は正解の番号（0〜3）
    let explanation: String
    let choices: [String]? // 4択問題の選択肢（LaTeX 混じり）。整数で答える問題は nil
    let unit: String?      // 単元の id（units.json）。みんなの問題は nil
    var family: String? = nil   // 酷似した問題のまとまり（数字だけ違う問題、同じ単語の英→和・和→英）。しばらく続けて出さない
    let rate: Double?      // 10人中、何人が1発で正解できそうか（作成時の見積もり、0〜10）。実際の正解率が集まるまでの目安

    var isChoice: Bool { choices != nil }
    static let choiceMarks = ["①", "②", "③", "④"]
    /// 正解の表示。整数なら数、4択なら「①」など。
    var answerText: String { isChoice ? Problem.choiceMarks[min(max(answer, 0), 3)] : "\(answer)" }

    var categoryInfo: ProblemCategory { ProblemCategory(rawValue: category) ?? .junior }
    var difficultyInfo: Difficulty { Difficulty(rawValue: difficulty) ?? .easy }
}

/// 教科。ルールを作るとき、教科ごとにまとめて選べる。
enum Subject: String, CaseIterable, Identifiable {
    case math, english, social, science, japanese, general
    var id: String { rawValue }

    var label: String {
        switch self {
        case .math: "数学"
        case .english: "英語"
        case .social: "社会"
        case .science: "理科"
        case .japanese: "国語"
        case .general: "ノンジャンル"
        }
    }

    var categories: [ProblemCategory] { ProblemCategory.allCases.filter { $0.subject == self } }
}

/// 問題の分野。problems.json の category と同じ文字。
enum ProblemCategory: String, CaseIterable, Identifiable {
    case elem, junior, math1a, math2b, math3c
    case eng_word, eng_sentence
    case soc_geo, soc_hist, soc_civ
    case sci_bio, sci_chem, sci_phys, sci_earth
    case ja_kanji, ja_idiom, ja_classic, ja_grammar
    case triv_gen, triv_math, triv_eng, triv_soc, triv_sci, triv_ja      // ノンジャンル（発展内容・難問・分野に当てはまらない投稿）
    var id: String { rawValue }

    var subject: Subject {
        switch self {
        case .elem, .junior, .math1a, .math2b, .math3c, .triv_math: .math
        case .eng_word, .eng_sentence, .triv_eng: .english
        case .soc_geo, .soc_hist, .soc_civ, .triv_soc: .social
        case .sci_bio, .sci_chem, .sci_phys, .sci_earth, .triv_sci: .science
        case .ja_kanji, .ja_idiom, .ja_classic, .ja_grammar, .triv_ja: .japanese
        case .triv_gen: .general
        }
    }

    var label: String {
        switch self {
        case .elem: "小学算数"
        case .junior: "中学数学"
        case .math1a: "数学I・A"
        case .math2b: "数学II・B"
        case .math3c: "数学III・C"
        case .eng_word: "英単語"
        case .eng_sentence: "英文法・和訳"
        case .soc_geo: "地理"
        case .soc_hist: "歴史"
        case .soc_civ: "公民"
        case .sci_bio: "生物"
        case .sci_chem: "化学"
        case .sci_phys: "物理"
        case .sci_earth: "地学"
        case .ja_kanji: "漢字"
        case .ja_idiom: "語句"
        case .ja_classic: "古文"
        case .ja_grammar: "国語文法"
        case .triv_gen: "どれにも当てはまらない"
        case .triv_math, .triv_eng, .triv_soc, .triv_sci, .triv_ja: "ノンジャンル"
        }
    }
}

enum Difficulty: Int, CaseIterable, Identifiable {
    case easy = 1, medium = 2, hard = 3, expert = 4
    var id: Int { rawValue }

    var label: String {
        switch self {
        case .easy: "初級"
        case .medium: "中級"
        case .hard: "上級"
        case .expert: "最上級"
        }
    }

    var dots: String { String(repeating: "●", count: rawValue) + String(repeating: "○", count: Difficulty.allCases.count - rawValue) }
}

/// アプリ内蔵の問題データベース（Resources/problems.json）。
enum ProblemBank {
    static let all: [Problem] = {
        guard let url = Bundle.main.url(forResource: "problems", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let problems = try? JSONDecoder().decode([Problem].self, from: data) else { return [] }
        return problems
    }()

    /// id から問題を探す。
    static func find(_ id: String) -> Problem? { all.first(where: { $0.id == id }) }

    static func candidates(categories: Set<String>, difficulties: Set<Int>) -> [Problem] {
        all.filter { categories.contains($0.category) && difficulties.contains($0.difficulty) }
    }

    /// 最近出した問題をなるべく避けてランダムに1問選ぶ。
    static func pick(categories: Set<String>, difficulties: Set<Int>, excluding current: String? = nil) -> Problem? {
        var pool = candidates(categories: categories, difficulties: difficulties).filter { Access.isOpen($0) }
        if pool.isEmpty { pool = all.filter { Access.isOpen($0) } }
        let recent = Set(SharedStore.recentProblemIDs)
        let fresh = pool.filter { !recent.contains($0.id) && $0.id != current }
        let chosen = (fresh.isEmpty ? pool.filter { $0.id != current } : fresh).randomElement() ?? pool.randomElement()
        if let chosen { SharedStore.recentProblemIDs.append(chosen.id) }
        return chosen
    }
}
