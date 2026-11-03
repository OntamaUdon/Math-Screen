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

    /// 復習の予定（間隔をあけた反復）。1発正解のたびに間隔がのびて、まちがえると近いうちに戻ってくる。
    struct Schedule: Codable {
        var streak: Int        // 連続で1発正解した回数
        var due: Double        // 次に復習する時刻（1970年からの秒）
        var last: Double       // 最後に解いた時刻
    }

    private struct Stored: Codable {
        var unit: [String: [Bool]] = [:]
        var problem: [String: [Bool]] = [:]
        var sched: [String: Schedule]? = nil
        var fam: [String: Double]? = nil      // 酷似した問題のまとまり → 最後に解いた時刻
    }

    /// 1発正解が続くほど、のびる間隔（日）。
    static let intervalDays: [Double] = [1, 3, 7, 14, 30, 60, 120]
    /// まちがえたあと、また出てくるまでの時間（秒）。すぐ同じ問題が出ないよう少しあける。
    static let relearnDelay: Double = 3600

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
        // 復習の予定を更新する
        let now = Date().timeIntervalSince1970
        var s = data.sched?[problem.id] ?? Schedule(streak: 0, due: now, last: now)
        if firstTryCorrect {
            s.streak += 1
            s.due = now + Self.intervalDays[min(s.streak - 1, Self.intervalDays.count - 1)] * 86400
        } else {
            s.streak = 0
            s.due = now + Self.relearnDelay
        }
        s.last = now
        if let f = problem.family {
            if data.fam == nil { data.fam = [:] }
            data.fam?[f] = now
        }
        if data.sched == nil { data.sched = [:] }
        data.sched?[problem.id] = s
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

    /// 酷似した問題を最後に解いてから、何秒たったか（解いたことがなければ nil）。
    func familyAge(of problem: Problem) -> Double? {
        guard let f = problem.family, let t = data.fam?[f] else { return nil }
        return Date().timeIntervalSince1970 - t
    }

    func schedule(_ problemID: String) -> Schedule? { data.sched?[problemID] }

    func seen(_ problemID: String) -> Bool { !(data.problem[problemID] ?? []).isEmpty }
    func lastWasWrong(_ problemID: String) -> Bool { data.problem[problemID]?.last == false }
}

/// 出す問題の選び方：できていない単元を優先し、できてきたら難しい問題へ、先に身につけたい単元ができたら次の単元へ。
enum Adaptive {
    /// `units` に「community:教科」が入っているか、`community` で渡されると、承認された「みんなの問題」もまぜる。
    static func pick(categories: Set<String>, units: Set<String>, community: Set<String> = [], excluding current: String? = nil) -> Problem? {
        let store = MasteryStore.shared
        let commIDs = community.union(units.filter(CommunityCache.isCommunity))
        var pool = ProblemBank.all.filter { categories.contains($0.category) && (units.isEmpty || units.contains($0.unit ?? "")) }
        pool += CommunityCache.shared.problems(for: commIDs)
        if pool.isEmpty { pool = ProblemBank.all.filter { categories.contains($0.category) } }
        if pool.isEmpty { return ProblemBank.pick(categories: categories, difficulties: [1, 2, 3], excluding: current) }

        let now = Date().timeIntervalSince1970
        let lastUnitKey = "adaptive.lastUnit"

        // 0) 復習の時期がきた問題があれば、一定の確率で先に出す（間隔をあけた反復）。
        //    予定が過ぎているほど、また前回まちがえた問題ほど、出やすい。
        let due = pool.filter { p in
            guard p.id != current, let s = store.schedule(p.id) else { return false }
            return s.due <= now
        }
        if !due.isEmpty, Double.random(in: 0..<1) < min(0.5, 0.2 + 0.05 * Double(min(due.count, 6))) {
            let weighted: [(Problem, Double)] = due.map { p in
                let s = store.schedule(p.id)!
                let overdueDays = min((now - s.due) / 86400, 14)
                return (p, 1 + overdueDays / 7 + (s.streak == 0 ? 1 : 0))
            }
            if let c = choose(weighted) {
                SharedStore.recentProblemIDs.append(c.id)
                if let u = c.unit { UserDefaults.standard.set(u, forKey: lastUnitKey) }
                return c
            }
        }

        let byUnit = Dictionary(grouping: pool, by: { $0.unit ?? "" })
        let auto = units.isEmpty
        let lastUnit = UserDefaults.standard.string(forKey: lastUnitKey)

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
            // おまかせでは、ノンジャンル（発展内容・難問）は、ほかの単元よりやや出にくくする
            if auto, UnitCatalog.info(uid)?.stage == "ノンジャンル" { w *= 0.25 }
            // 同じ単元が続かないようにして、いろいろな単元をまぜる（交互練習）
            if byUnit.count > 1, uid == lastUnit { w *= 0.5 }
            unitWeights.append((uid, w))
        }
        guard let unit = choose(unitWeights), let list = byUnit[unit] else { return nil }
        UserDefaults.standard.set(unit, forKey: lastUnitKey)

        // 2) その単元の中で、いまの力に合う難しさの問題を選ぶ。
        //    難しさは、全員の1発正解率（連続値）。できていないうちは正解率の高い問題、できてきたら正解率の低い問題。
        //    ちょうどよい難しさ（8割ほど正解できる）を、少し頑張れば解ける問題として狙う。
        let pr = store.progress(unit: unit)
        let ability = pr.count < 3 ? 0.0 : pr.score                // 0...1
        let targetRate = 0.9 - 0.35 * ability                      // 力が0なら正解率90%の問題、力が1なら55%の問題
        var cands = list.filter { $0.id != current }
        if cands.isEmpty { cands = list }
        let recent = Set(SharedStore.recentProblemIDs)
        let weighted: [(Problem, Double)] = cands.map { p in
            let gap = (DifficultyStore.shared.correctRate(p) - targetRate) / 0.15
            var w = exp(-gap * gap) + 0.02                         // 目標の正解率に近いほど出やすい
            if let s = store.schedule(p.id) {
                // 一度解いた問題は、復習の時期がくるまでは出にくくする
                w *= s.due <= now ? 2 : 0.03
            } else {
                w *= 1.5                                           // まだ解いたことがない問題を、少し優先
            }
            if recent.contains(p.id) { w *= 0.05 }
            // 解いたばかりの問題に酷似した問題は、しばらく出しにくくする（1日以内は強く、1週間かけてもとに戻る）
            if let age = store.familyAge(of: p) {
                if age < 86400 { w *= 0.08 } else if age < 3 * 86400 { w *= 0.3 } else if age < 7 * 86400 { w *= 0.6 }
            }
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


/// 問題集に出す、解いた結果の印。いちばんよい結果を残す。
/// 1発正解＝☆、1回まちがえて正解＝◎、2回以上まちがえて正解＝〇、解かずに変更＝△。
enum ProblemMark: Int {
    case skipped = 1, many = 2, once = 3, perfect = 4

    var symbol: String {
        switch self {
        case .perfect: "☆"
        case .once: "◎"
        case .many: "〇"
        case .skipped: "△"
        }
    }

    var label: String {
        switch self {
        case .perfect: "1発正解"
        case .once: "1回まちがえて正解"
        case .many: "2回以上まちがえて正解"
        case .skipped: "解かずに変更"
        }
    }

    /// 解いたとき：まちがえた回数から決める。
    static func solved(wrongCount: Int) -> ProblemMark { wrongCount == 0 ? .perfect : (wrongCount == 1 ? .once : .many) }
}

final class ProblemMarkStore {
    static let shared = ProblemMarkStore()
    private static let key = "problem.marks.v1"
    private var marks: [String: Int]

    private init() { marks = (UserDefaults.standard.dictionary(forKey: Self.key) as? [String: Int]) ?? [:] }

    func mark(_ id: String) -> ProblemMark? { marks[id].flatMap(ProblemMark.init) }

    /// いままでより良い結果のときだけ、残す。
    func record(_ id: String, _ mark: ProblemMark) {
        guard (marks[id] ?? 0) < mark.rawValue else { return }
        marks[id] = mark.rawValue
        UserDefaults.standard.set(marks, forKey: Self.key)
    }
}


/// 承認された「みんなの問題」を端末に保存しておく。ルールの出題範囲で選ばれたときに使う。
final class CommunityCache {
    static let shared = CommunityCache()
    static let prefix = "community:"
    private static let key = "community.cache.v1"
    private static let stampKey = "community.cache.at"
    private var rows: [CommunityRow]

    private init() {
        if let raw = UserDefaults.standard.data(forKey: Self.key),
           let r = try? JSONDecoder().decode([CommunityRow].self, from: raw) { rows = r } else { rows = [] }
    }

    static func isCommunity(_ unitID: String) -> Bool { unitID.hasPrefix(prefix) }

    /// 「community:math」のような単元の指定に合う、承認済みの問題。
    func problems(for ids: Set<String>) -> [Problem] {
        guard !ids.isEmpty else { return [] }
        return rows.compactMap { row in
            let subject = ProblemCategory(rawValue: row.genre)?.subject.rawValue ?? Subject.general.rawValue
            let unit = Self.prefix + subject
            return ids.contains(unit) ? row.problem(unit: unit) : nil
        }
    }

    func problem(id: String) -> Problem? {
        guard let row = rows.first(where: { "c-" + $0.id == id }) else { return nil }
        let subject = ProblemCategory(rawValue: row.genre)?.subject.rawValue ?? Subject.general.rawValue
        return row.problem(unit: Self.prefix + subject)
    }

    /// 6時間に1回、サーバーから取り直す（ネットにつながらないときは、前回のものを使う）。
    func refreshIfNeeded() async {
        let last = UserDefaults.standard.double(forKey: Self.stampKey)
        guard Date().timeIntervalSince1970 - last > 6 * 3600 else { return }
        guard let fresh = try? await Community.shared.approved() else { return }
        rows = fresh
        if let raw = try? JSONEncoder().encode(fresh) { UserDefaults.standard.set(raw, forKey: Self.key) }
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: Self.stampKey)
    }
}
