import Foundation

/// 単元（units.json）。学習指導要領のまとまり。
struct UnitInfo: Codable, Identifiable, Hashable {
    let id: String
    let subject: String
    let stage: String          // 小学 / 中学 / 高校
    let name: String
    let order: Int
    let prereqs: [String]      // 先に身につけたい単元
    let group: String?         // マップで、段階の下にまとめる名前（物理・数学II など）

    var subjectInfo: Subject { Subject(rawValue: subject) ?? .math }
}

enum UnitCatalog {
    static let all: [UnitInfo] = {
        guard let url = Bundle.main.url(forResource: "units", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let units = try? JSONDecoder().decode([UnitInfo].self, from: data) else { return [] }
        return units
    }()

    /// 単元ごとの問題数。
    static let problemCount: [String: Int] = Dictionary(grouping: ProblemBank.all, by: { $0.unit ?? "" }).mapValues(\.count)

    /// 単元ごとの、問題の分野（category）。
    static let categories: [String: Set<String>] = Dictionary(grouping: ProblemBank.all, by: { $0.unit ?? "" }).mapValues { Set($0.map(\.category)) }

    /// 問題が1つ以上ある単元だけ（小学の算数などは、問題を足すと自動で出てくる）。
    static let available: [UnitInfo] = all.filter { (problemCount[$0.id] ?? 0) > 0 }

    static func info(_ id: String) -> UnitInfo? { all.first { $0.id == id } }

    static func units(in subject: Subject) -> [UnitInfo] { available.filter { $0.subject == subject.rawValue } }
}

/// 単元のできぐあい。
enum MasteryLevel: Int {
    case none, learning, good, complete

    var label: String {
        switch self {
        case .none: "未学習"
        case .learning: "練習中"
        case .good: "得意"
        case .complete: "完成"
        }
    }
}

struct UnitProgress {
    var count: Int             // 数えている解答の数（直近3回まで）
    var score: Double          // 1発正解の割合
    var level: MasteryLevel
}

/// 問題ごと・単元ごとの「1回目の解答」の記録。単元の完成度は、直近3回の1発正解で決める。
/// 単語は1語が1問なので、問題ごとの記録（前回まちがえたか）で、苦手な単語を優先して出す。
final class MasteryStore {
    static let shared = MasteryStore()

    private struct Stored: Codable {
        var unit: [String: [Bool]] = [:]
        var problem: [String: [Bool]] = [:]
    }

    private static let key = "mastery.v1"
    /// 単元の完成度は、直近これだけの回数の1発正解で決める。
    static let window = 3
    private var data: Stored

    private init() {
        if let raw = UserDefaults.standard.data(forKey: Self.key),
           let d = try? JSONDecoder().decode(Stored.self, from: raw) { data = d } else { data = Stored() }
    }

    func record(_ problem: Problem, firstTryCorrect: Bool) {
        if let u = problem.unit {
            data.unit[u, default: []].append(firstTryCorrect)
            data.unit[u] = Array(data.unit[u]!.suffix(Self.window))
        }
        data.problem[problem.id, default: []].append(firstTryCorrect)
        data.problem[problem.id] = Array(data.problem[problem.id]!.suffix(5))
        if let raw = try? JSONEncoder().encode(data) { UserDefaults.standard.set(raw, forKey: Self.key) }
    }

    func progress(unit id: String) -> UnitProgress {
        let r = Array((data.unit[id] ?? []).suffix(Self.window))
        guard !r.isEmpty else { return UnitProgress(count: 0, score: 0, level: .none) }
        let score = Double(r.filter { $0 }.count) / Double(r.count)
        let level: MasteryLevel
        if r.count < Self.window { level = .learning }       // まだ3回に満たない
        else if score >= 1 { level = .complete }              // 3回とも1発正解
        else if score >= 0.6 { level = .good }                // 3回中2回以上
        else { level = .learning }
        return UnitProgress(count: r.count, score: score, level: level)
    }

    func seen(_ problemID: String) -> Bool { !(data.problem[problemID] ?? []).isEmpty }
    func lastWasWrong(_ problemID: String) -> Bool { data.problem[problemID]?.last == false }
}

/// 出す問題の選び方：できていない単元を優先し、できてきたら難しい問題へ、先に身につけたい単元ができたら次の単元へ。
enum Adaptive {
    static func pick(categories: Set<String>, units: Set<String>, excluding current: String? = nil) -> Problem? {
        let store = MasteryStore.shared
        var pool = ProblemBank.all.filter { categories.contains($0.category) && (units.isEmpty || units.contains($0.unit ?? "")) }
        if pool.isEmpty { pool = ProblemBank.all.filter { categories.contains($0.category) } }
        if pool.isEmpty { return ProblemBank.pick(categories: categories, difficulties: [1, 2, 3], excluding: current) }

        let byUnit = Dictionary(grouping: pool, by: { $0.unit ?? "" })
        let auto = units.isEmpty

        // 1) 単元を選ぶ
        var unitWeights: [(String, Double)] = []
        for (uid, _) in byUnit {
            var w: Double
            switch store.progress(unit: uid).level {
            case .none: w = 1.0
            case .learning: w = 1.6
            case .good: w = 0.6
            case .complete: w = 0.15
            }
            // おまかせのときは、先に身につけたい単元が「得意」になるまで、その単元を後回しにする
            if auto, let info = UnitCatalog.info(uid),
               info.prereqs.contains(where: { byUnit[$0] != nil && store.progress(unit: $0).level.rawValue < MasteryLevel.good.rawValue }) {
                w *= 0.1
            }
            unitWeights.append((uid, w))
        }
        guard let unit = choose(unitWeights), let list = byUnit[unit] else { return nil }

        // 2) その単元の中で、いまの力に合う難しさの問題を選ぶ。
        //    難しさは、全員の1発正解率（連続値）。できていないうちは正解率の高い問題、できてきたら正解率の低い問題。
        let pr = store.progress(unit: unit)
        let ability = pr.count < 3 ? 0.0 : pr.score                // 0...1
        let targetRate = 0.9 - 0.4 * ability                       // 力が0なら正解率90%の問題、力が1なら50%の問題
        var cands = list.filter { $0.id != current }
        if cands.isEmpty { cands = list }
        let recent = Set(SharedStore.recentProblemIDs)
        let weighted: [(Problem, Double)] = cands.map { p in
            let gap = (DifficultyStore.shared.correctRate(p) - targetRate) / 0.15
            var w = exp(-gap * gap) + 0.02                         // 目標の正解率に近いほど出やすい
            if store.lastWasWrong(p.id) { w *= 3 } else if !store.seen(p.id) { w *= 1.5 }
            if recent.contains(p.id) { w *= 0.05 }
            return (p, w)
        }
        let chosen = choose(weighted)
        if let chosen { SharedStore.recentProblemIDs.append(chosen.id) }
        return chosen
    }

    private static func choose<T>(_ items: [(T, Double)]) -> T? {
        let total = items.reduce(0) { $0 + $1.1 }
        guard total > 0 else { return items.randomElement()?.0 }
        var r = Double.random(in: 0..<total)
        for (item, w) in items {
            r -= w
            if r < 0 { return item }
        }
        return items.last?.0
    }
}


/// 問題の難しさ：全員の1発正解率（サーバーの problem_stats）から、連続値で測る。
/// 解いた人がまだ少ない問題は、はじめに付けた見積もり（10人中何人が正解できそうか、rate）を、5人ぶんの重さで混ぜて評価する。
final class DifficultyStore {
    static let shared = DifficultyStore()

    private var stats: [String: [Int]] = [:]          // 問題 id → [出題数, 正解数]
    private static let cacheKey = "difficulty.stats.v1"
    private static let stampKey = "difficulty.stats.at"

    private init() {
        if let raw = UserDefaults.standard.data(forKey: Self.cacheKey),
           let d = try? JSONDecoder().decode([String: [Int]].self, from: raw) { stats = d }
    }

    /// 全員の1発正解率の見積もり（0...1）。大きいほど易しい。
    func correctRate(_ p: Problem) -> Double {
        let prior: Double = p.rate.map { $0 / 10 } ?? 0.6          // 見積もりがない問題（みんなの投稿）は 6 割
        let s = stats[p.id] ?? [0, 0]
        return (Double(s[1]) + 5 * prior) / (Double(s[0]) + 5)
    }

    /// 難しさ（0...1）。大きいほど難しい。
    func difficulty(_ p: Problem) -> Double { 1 - correctRate(p) }

    /// 1日に1回、サーバーから集計を取り直す。
    func refreshIfNeeded() async {
        let last = UserDefaults.standard.double(forKey: Self.stampKey)
        guard Date().timeIntervalSince1970 - last > 24 * 3600 else { return }
        guard let all = await Community.shared.allStats() else { return }
        stats = all
        if let raw = try? JSONEncoder().encode(all) { UserDefaults.standard.set(raw, forKey: Self.cacheKey) }
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: Self.stampKey)
    }
}
