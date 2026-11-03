import Foundation
import FamilyControls
import ManagedSettings
import DeviceActivity

/// アプリ本体と各拡張（Monitor / Shield）で共有する App Group。
enum AppGroup {
    static let identifier = "group.com.ontamaudon.qlock"
    static var defaults: UserDefaults { UserDefaults(suiteName: identifier) ?? .standard }
}

/// 「どのアプリを、何分使ったら問題を出すか」のルール。
struct GuardRule: Codable, Identifiable {
    var id: UUID = UUID()
    var selection: FamilyActivitySelection
    var thresholdMinutes: Int              // 何分使うごとに
    var questionCount: Int = 1             // 何問出すか
    var categories: Set<String>            // 出題する分野（problems.json の category）
    var difficulties: Set<Int> = [1, 2, 3] // （使わなくなった。難しさは正解率から自動で決める）
    var units: Set<String> = []            // 出題する単元。空なら「おまかせ」（できていない単元を優先）
    var isEnabled: Bool = true

    static let mathCategories: Set<String> = ["elem", "junior", "math1a", "math2b", "math3c"]
    static let allCategories: Set<String> = mathCategories.union(
        ["eng_word", "eng_sentence", "soc_geo", "soc_hist", "soc_civ", "sci_bio", "sci_chem", "sci_phys", "sci_earth",
         "ja_kanji", "ja_idiom", "ja_classic", "ja_grammar",
         "triv_math", "triv_eng", "triv_soc", "triv_sci", "triv_ja"])        // ノンジャンル（発展内容・難問）も、新しいルールの初期状態に入れる

    init(id: UUID = UUID(), selection: FamilyActivitySelection, thresholdMinutes: Int,
         questionCount: Int = 1, categories: Set<String> = GuardRule.allCategories,
         difficulties: Set<Int> = [1, 2, 3], units: Set<String> = [], isEnabled: Bool = true) {
        self.id = id
        self.selection = selection
        self.thresholdMinutes = thresholdMinutes
        self.questionCount = questionCount
        self.categories = categories
        self.difficulties = difficulties
        self.units = units
        self.isEnabled = isEnabled
    }

    private enum CodingKeys: String, CodingKey { case id, selection, thresholdMinutes, questionCount, categories, difficulties, units, isEnabled }

    /// 古い保存データ（名前あり・問題数なし）も読めるようにする。
    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(UUID.self, forKey: .id)
        selection = try c.decode(FamilyActivitySelection.self, forKey: .selection)
        thresholdMinutes = try c.decode(Int.self, forKey: .thresholdMinutes)
        questionCount = try c.decodeIfPresent(Int.self, forKey: .questionCount) ?? 1
        categories = try c.decodeIfPresent(Set<String>.self, forKey: .categories) ?? GuardRule.mathCategories   // 古いルールは数学だけ
        difficulties = try c.decodeIfPresent(Set<Int>.self, forKey: .difficulties) ?? [1, 2, 3]
        units = try c.decodeIfPresent(Set<String>.self, forKey: .units) ?? []
        if !categories.isDisjoint(with: GuardRule.mathCategories) { categories.insert("elem") }   // 数学を選んでいたルールにも、小学算数を加える
        isEnabled = try c.decodeIfPresent(Bool.self, forKey: .isEnabled) ?? true
    }

    /// 例：「10分ごとに3問」
    var title: String { "\(Self.durationText(thresholdMinutes))ごとに\(questionCount)問" }

    /// 例：45 → "45分"、90 → "1時間30分"、120 → "2時間"
    static func durationText(_ minutes: Int) -> String {
        let h = minutes / 60, m = minutes % 60
        if h == 0 { return "\(m)分" }
        return m == 0 ? "\(h)時間" : "\(h)時間\(m)分"
    }

    static let maxMinutes = 12 * 60

    var activityName: DeviceActivityName { DeviceActivityName("rule.\(id.uuidString)") }
    var eventName: DeviceActivityEvent.Name { DeviceActivityEvent.Name("rule.\(id.uuidString).limit") }
    var storeName: ManagedSettingsStore.Name { GuardRule.storeName(for: id) }

    static func storeName(for id: UUID) -> ManagedSettingsStore.Name {
        ManagedSettingsStore.Name("rule.\(id.uuidString)")
    }

    var itemCount: Int {
        selection.applicationTokens.count + selection.categoryTokens.count + selection.webDomainTokens.count
    }
}

/// 1日分の記録。
struct DailyStats: Codable {
    var triggers: Int = 0        // 制限が発動した回数
    var unlocks: Int = 0         // 問題を解いて解除した回数
    var correct: Int = 0         // 正解数
    var attempts: Int = 0        // 回答した回数（不正解を含む）
    var emergencyUnlocks: Int = 0
}

/// 出題設定。
struct ChallengeSettings: Codable, Equatable {
    var difficulties: Set<Int> = [1, 2, 3]
    var categories: Set<String> = ["elem", "junior", "math1a", "math2b", "math3c"]
    var requiredCorrect: Int = 1
}

/// App Group の UserDefaults に保存するデータへのアクセス。
enum SharedStore {
    private static var d: UserDefaults { AppGroup.defaults }

    private enum Key {
        static let rules = "rules"
        static let locked = "lockedRuleIDs"
        static let daily = "dailyStats"
        static let settings = "challengeSettings"
        static let streak = "currentStreak"
        static let bestStreak = "bestStreak"
        static let recent = "recentProblemIDs"
        static let onboarded = "hasOnboarded"
        static let pendingID = "pendingProblemID"
        static let pendingBody = "pendingProblemBody"
    }

    // MARK: ルール
    static func loadRules() -> [GuardRule] {
        guard let data = d.data(forKey: Key.rules),
              let rules = try? JSONDecoder().decode([GuardRule].self, from: data) else { return [] }
        return rules
    }

    static func saveRules(_ rules: [GuardRule]) {
        if let data = try? JSONEncoder().encode(rules) { d.set(data, forKey: Key.rules) }
    }

    static func rule(forActivity activity: DeviceActivityName) -> GuardRule? {
        loadRules().first { $0.activityName == activity }
    }

    /// ロックがかかった時の「何分使ったか」（ブロック画面の文に使う）。
    static var pendingMinutes: Int {
        get { d.integer(forKey: "pendingMinutes") }
        set { d.set(newValue, forKey: "pendingMinutes") }
    }

    // MARK: ルールごとに用意した「次に出す問題」（ロックがかかるとき、監視の拡張機能がブロック画面用にコピーする）
    static func setRulePending(ruleID: UUID, id: String, body: String) {
        var m = d.dictionary(forKey: "rulePending") as? [String: [String]] ?? [:]
        m[ruleID.uuidString] = [id, body]
        d.set(m, forKey: "rulePending")
    }

    static func rulePending(ruleID: UUID) -> (id: String, body: String)? {
        guard let m = d.dictionary(forKey: "rulePending") as? [String: [String]],
              let v = m[ruleID.uuidString], v.count == 2 else { return nil }
        return (v[0], v[1])
    }

    static func removeRulePending(ruleID: UUID) {
        var m = d.dictionary(forKey: "rulePending") as? [String: [String]] ?? [:]
        m[ruleID.uuidString] = nil
        d.set(m, forKey: "rulePending")
    }

    // MARK: 使用時間の進み具合（制限の10分の1ずつの節目で、監視の拡張機能が記録する）
    static func setRuleProgress(ruleID: UUID, minutes: Int) {
        var m = d.dictionary(forKey: "ruleProgress") as? [String: Int] ?? [:]
        m[ruleID.uuidString] = minutes
        d.set(m, forKey: "ruleProgress")
    }

    static func ruleProgress(ruleID: UUID) -> Int {
        (d.dictionary(forKey: "ruleProgress") as? [String: Int])?[ruleID.uuidString] ?? 0
    }

    static func clearRuleProgress(ruleID: UUID) {
        var m = d.dictionary(forKey: "ruleProgress") as? [String: Int] ?? [:]
        m[ruleID.uuidString] = nil
        d.set(m, forKey: "ruleProgress")
    }

    // MARK: ロック状態
    static var lockedRuleIDs: Set<UUID> {
        get { Set((d.stringArray(forKey: Key.locked) ?? []).compactMap(UUID.init(uuidString:))) }
        set { d.set(newValue.map(\.uuidString), forKey: Key.locked) }
    }

    static func markLocked(_ id: UUID) { lockedRuleIDs.insert(id) }
    static func markUnlocked(_ id: UUID) { lockedRuleIDs.remove(id) }

    // MARK: 記録
    static func dayKey(_ date: Date = Date()) -> String {
        let f = DateFormatter()
        f.calendar = Calendar(identifier: .gregorian)
        f.locale = Locale(identifier: "en_US_POSIX")
        f.dateFormat = "yyyy-MM-dd"
        return f.string(from: date)
    }

    static func loadDaily() -> [String: DailyStats] {
        guard let data = d.data(forKey: Key.daily),
              let v = try? JSONDecoder().decode([String: DailyStats].self, from: data) else { return [:] }
        return v
    }

    static func updateToday(_ change: (inout DailyStats) -> Void) {
        var all = loadDaily()
        let key = dayKey()
        var today = all[key] ?? DailyStats()
        change(&today)
        all[key] = today
        if let data = try? JSONEncoder().encode(all) { d.set(data, forKey: Key.daily) }
    }

    static var currentStreak: Int {
        get { d.integer(forKey: Key.streak) }
        set {
            d.set(newValue, forKey: Key.streak)
            if newValue > bestStreak { d.set(newValue, forKey: Key.bestStreak) }
        }
    }

    static var bestStreak: Int { d.integer(forKey: Key.bestStreak) }

    // MARK: Premium（本物の課金ができるまでの、仮登録。お金はかからない）
    static var isPremium: Bool {
        get { d.bool(forKey: "isPremium") }
        set { d.set(newValue, forKey: "isPremium") }
    }

    // MARK: 診断（拡張機能が動いたかどうかを、アプリの設定画面で確認するため）
    static func diagNote(_ key: String) -> String? { d.string(forKey: "diagNote.\(key)") }
    static func recordDiag(_ key: String) { d.set(Date().timeIntervalSince1970, forKey: "diag.\(key)") }
    static func diagDate(_ key: String) -> Date? {
        let t = d.double(forKey: "diag.\(key)")
        return t > 0 ? Date(timeIntervalSince1970: t) : nil
    }

    // MARK: 出題設定
    static var settings: ChallengeSettings {
        get {
            guard let data = d.data(forKey: Key.settings),
                  let s = try? JSONDecoder().decode(ChallengeSettings.self, from: data) else { return ChallengeSettings() }
            return s
        }
        set { if let data = try? JSONEncoder().encode(newValue) { d.set(data, forKey: Key.settings) } }
    }

    static var recentProblemIDs: [String] {
        get { d.stringArray(forKey: Key.recent) ?? [] }
        set { d.set(Array(newValue.suffix(500)), forKey: Key.recent) }
    }

    // MARK: 次に出す問題（ブロック画面に表示し、通知から開いた問題画面でも同じものを出す）
    static var pendingProblemID: String? { d.string(forKey: Key.pendingID) }
    static var pendingProblemBody: String? { d.string(forKey: Key.pendingBody) }

    static func setPendingProblem(id: String?, body: String?) {
        d.set(id, forKey: Key.pendingID)
        d.set(body, forKey: Key.pendingBody)
    }

    static var hasOnboarded: Bool {
        get { d.bool(forKey: Key.onboarded) }
        set { d.set(newValue, forKey: Key.onboarded) }
    }
}
