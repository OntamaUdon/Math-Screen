import SwiftUI

struct Problem: Codable, Identifiable, Hashable {
    let id: String
    let category: String
    let difficulty: Int
    let title: String
    let body: String
    let answer: Int
    let explanation: String

    var categoryInfo: ProblemCategory { ProblemCategory(rawValue: category) ?? .junior }
    var difficultyInfo: Difficulty { Difficulty(rawValue: difficulty) ?? .easy }
}

enum ProblemCategory: String, CaseIterable, Identifiable {
    case junior, math1a, math2b, math3c
    var id: String { rawValue }

    var label: String {
        switch self {
        case .junior: "中学数学"
        case .math1a: "数学I・A"
        case .math2b: "数学II・B"
        case .math3c: "数学III・C"
        }
    }

    var color: Color {
        switch self {
        case .junior: Clay.mint
        case .math1a: Clay.sky
        case .math2b: Clay.lavender
        case .math3c: Clay.peach
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
