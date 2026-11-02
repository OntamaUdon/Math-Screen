import Foundation
import FamilyControls
import ManagedSettings
import DeviceActivity
import UserNotifications

/// 対象アプリへのシールド（ブロック画面）の付け外し。
enum ShieldController {
    static func lock(_ rule: GuardRule) {
        let store = ManagedSettingsStore(named: rule.storeName)
        let s = rule.selection
        store.shield.applications = s.applicationTokens.isEmpty ? nil : s.applicationTokens
        store.shield.applicationCategories = s.categoryTokens.isEmpty ? nil : .specific(s.categoryTokens)
        store.shield.webDomains = s.webDomainTokens.isEmpty ? nil : s.webDomainTokens
        store.shield.webDomainCategories = s.categoryTokens.isEmpty ? nil : .specific(s.categoryTokens)
    }

    static func unlock(ruleID: UUID) {
        ManagedSettingsStore(named: GuardRule.storeName(for: ruleID)).clearAllSettings()
    }
}

/// DeviceActivity による利用時間の監視。ルールごとに独立した activity を持つ。
enum MonitorScheduler {
    /// 監視を（再）開始する。iOS 17.4 以降の `includesPastActivity: false` により、
    /// 開始した時点からの利用時間だけを数えるので「正解後、次の N 分で再発動」になる。
    static func start(_ rule: GuardRule) throws {
        let center = DeviceActivityCenter()
        center.stopMonitoring([rule.activityName])
        guard rule.isEnabled, rule.itemCount > 0 else { return }

        let schedule = DeviceActivitySchedule(
            intervalStart: DateComponents(hour: 0, minute: 0),
            intervalEnd: DateComponents(hour: 23, minute: 59),
            repeats: true
        )
        let minutes = max(1, rule.thresholdMinutes)
        func event(_ m: Int) -> DeviceActivityEvent {
            DeviceActivityEvent(
                applications: rule.selection.applicationTokens,
                categories: rule.selection.categoryTokens,
                webDomains: rule.selection.webDomainTokens,
                threshold: DateComponents(hour: m / 60, minute: m % 60),
                includesPastActivity: false
            )
        }
        // ロックの本番のイベントに加えて、途中の節目（進み具合の表示用）のイベントも登録する
        var events: [DeviceActivityEvent.Name: DeviceActivityEvent] = [rule.eventName: event(minutes)]
        for m in progressMarks(minutes) { events[progressEventName(rule.id, m)] = event(m) }
        try center.startMonitoring(rule.activityName, during: schedule, events: events)
    }

    /// 制限の10分の1ずつの節目（分）。例：60分なら 6, 12, …, 54。5分なら 1, 2, 3, 4。1分は無し。
    static func progressMarks(_ minutes: Int) -> [Int] {
        var marks = Set<Int>()
        for k in 1...9 {
            let m = Int((Double(minutes) * Double(k) / 10).rounded(.up))
            if m >= 1 && m < minutes { marks.insert(m) }
        }
        return marks.sorted()
    }

    static func progressEventName(_ id: UUID, _ minutes: Int) -> DeviceActivityEvent.Name {
        DeviceActivityEvent.Name("rule.\(id.uuidString).p\(minutes)")
    }

    static func stop(_ rule: GuardRule) {
        DeviceActivityCenter().stopMonitoring([rule.activityName])
    }
}

/// 「問題を解いて解除」通知。シールドから直接アプリを開けないため、通知経由で本体を開く。
enum ChallengeNotification {
    static let identifier = "math-challenge"
    static let deepLink = "mathscreen://challenge"

    static func send(title: String, body: String, completion: (() -> Void)? = nil) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.userInfo = ["deeplink": deepLink]
        let request = UNNotificationRequest(identifier: identifier, content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request) { _ in completion?() }
    }
}
