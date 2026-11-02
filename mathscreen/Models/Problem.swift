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
    let hint: String?      // ヒント（Premium）。答えを直接は言わない
    let unit: String?      // 単元の id（units.json）。みんなの問題は nil
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
    case math, english, social, science
    var id: String { rawValue }

    var label: String {
        switch self {
        case .math: "数学"
        case .english: "英語"
        case .social: "社会"
        case .science: "理科"
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
    var id: String { rawValue }

    var subject: Subject {
        switch self {
        case .elem, .junior, .math1a, .math2b, .math3c: .math
        case .eng_word, .eng_sentence: .english
        case .soc_geo, .soc_hist, .soc_civ: .social
        case .sci_bio, .sci_chem, .sci_phys, .sci_earth: .science
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
        }
    }
}

enum Difficulty: Int, CaseIterable, Identifiable {
    case easy = 1, medium = 2, hard = 3
    var id: Int { rawValue }

    var label: String {
        switch self {
        case .easy: "初級"
        case .medium: "中級"
        case .hard: "上級"
        }
    }

    var dots: String { String(repeating: "●", count: rawValue) + String(repeating: "○", count: 3 - rawValue) }
}

/// アプリ内蔵の問題データベース（Resources/problems.json）。
enum ProblemBank {
    static let all: [Problem] = {
        guard let url = Bundle.main.url(forResource: "problems", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let problems = try? JSONDecoder().decode([Problem].self, from: data) else { return [] }
        return problems
    }()

    static func candidates(categories: Set<String>, difficulties: Set<Int>) -> [Problem] {
        all.filter { categories.contains($0.category) && difficulties.contains($0.difficulty) }
    }

    /// 最近出した問題をなるべく避けてランダムに1問選ぶ。
    static func pick(categories: Set<String>, difficulties: Set<Int>, excluding current: String? = nil) -> Problem? {
        var pool = candidates(categories: categories, difficulties: difficulties)
        if pool.isEmpty { pool = all }
        let recent = Set(SharedStore.recentProblemIDs)
        let fresh = pool.filter { !recent.contains($0.id) && $0.id != current }
        let chosen = (fresh.isEmpty ? pool.filter { $0.id != current } : fresh).randomElement() ?? pool.randomElement()
        if let chosen { SharedStore.recentProblemIDs.append(chosen.id) }
        return chosen
    }
}
