import Foundation
import FamilyControls
import ManagedSettings
import DeviceActivity

/// アプリ本体と各拡張（Monitor / Shield）で共有する App Group。
enum AppGroup {
    static let identifier = "group.com.mathscreen.mathscreen"
    static var defaults: UserDefaults { UserDefaults(suiteName: identifier) ?? .standard }
}

/// 「どのアプリを、何分使ったら問題を出すか」のルール。
struct GuardRule: Codable, Identifiable {
    var id: UUID = UUID()
    var name: String
    var selection: FamilyActivitySelection
    var thresholdMinutes: Int
    var isEnabled: Bool = true

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
    var categories: Set<String> = ["junior", "math1a", "math2b", "math3c"]
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
        set { d.set(Array(newValue.suffix(30)), forKey: Key.recent) }
    }

    static var hasOnboarded: Bool {
        get { d.bool(forKey: Key.onboarded) }
        set { d.set(newValue, forKey: Key.onboarded) }
    }
}
