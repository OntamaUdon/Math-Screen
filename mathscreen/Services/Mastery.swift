import Foundation

/// 単元（units.json）。学習指導要領のまとまり。
struct UnitInfo: Codable, Identifiable, Hashable {
    let id: String
    let subject: String
    let stage: String          // 小学 / 中学 / 高校
    let name: String
    let order: Int
    let prereqs: [String]      // 先に身につけたい単元

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
    var count: Int             // 数えている解答の数（直近10回まで）
    var score: Double          // 1発正解の割合
    var level: MasteryLevel
}

/// 問題ごと・単元ごとの「1回目の解答」の記録。単元の完成度は、直近10回の1発正解率で決める。
/// 単語は1語が1問なので、問題ごとの記録（前回まちがえたか）で、苦手な単語を優先して出す。
final class MasteryStore {
    static let shared = MasteryStore()

    private struct Stored: Codable {
        var unit: [String: [Bool]] = [:]
        var problem: [String: [Bool]] = [:]
    }

    private static let key = "mastery.v1"
    private var data: Stored

    private init() {
        if let raw = UserDefaults.standard.data(forKey: Self.key),
           let d = try? JSONDecoder().decode(Stored.self, from: raw) { data = d } else { data = Stored() }
    }

    func record(_ problem: Problem, firstTryCorrect: Bool) {
        if let u = problem.unit {
            data.unit[u, default: []].append(firstTryCorrect)
            data.unit[u] = Array(data.unit[u]!.suffix(10))
        }
        data.problem[problem.id, default: []].append(firstTryCorrect)
        data.problem[problem.id] = Array(data.problem[problem.id]!.suffix(5))
        if let raw = try? JSONEncoder().encode(data) { UserDefaults.standard.set(raw, forKey: Self.key) }
    }

    func progress(unit id: String) -> UnitProgress {
        let r = data.unit[id] ?? []
        guard !r.isEmpty else { return UnitProgress(count: 0, score: 0, level: .none) }
        let score = Double(r.filter { $0 }.count) / Double(r.count)
        let level: MasteryLevel
        if r.count < 3 { level = .learning }
        else if score >= 0.9, r.count >= 10 { level = .complete }
        else if score >= 0.7, r.count >= 5 { level = .good }
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

        // 2) その単元の中で、できぐあいに合う難しさの問題を選ぶ
        let pr = store.progress(unit: unit)
        let target = pr.count < 3 || pr.score < 0.5 ? 1 : (pr.score < 0.8 ? 2 : 3)
        var cands = list.filter { $0.difficulty <= target && $0.id != current }
        if cands.isEmpty { cands = list.filter { $0.id != current } }
        if cands.isEmpty { cands = list }
        let recent = Set(SharedStore.recentProblemIDs)
        let weighted: [(Problem, Double)] = cands.map { p in
            var w = 1.0
            if p.difficulty == target { w *= 2 }
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
