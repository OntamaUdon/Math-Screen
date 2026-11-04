import Foundation
import FamilyControls
import ManagedSettings
import DeviceActivity
import UserNotifications

/// 「解くロック」自身（と、その拡張機能）は、ロックの対象にしない。
/// ロックされると、問題を解くためにアプリを開けなくなってしまうため。
enum SelfExclusion {
    static let bundleID = "com.ontamaudon.qlock"

    /// 自分のアプリのトークン（取れたら）。カテゴリを選んだときに、その中から自分を除くのに使う。
    static var ownToken: ApplicationToken? { Application(bundleIdentifier: bundleID).token }

    /// 選んだアプリのうち、自分のものを取りのぞく。
    static func strip(_ tokens: Set<ApplicationToken>) -> Set<ApplicationToken> {
        tokens.filter { token in
            guard let id = Application(token: token).bundleIdentifier else { return true }
            return !id.hasPrefix(bundleID)
        }
    }
}

/// 対象アプリへのシールド（ブロック画面）の付け外し。
enum ShieldController {
    static func lock(_ rule: GuardRule) {
        let store = ManagedSettingsStore(named: rule.storeName)
        let s = rule.selection
        let apps = SelfExclusion.strip(s.applicationTokens)
        let own: Set<ApplicationToken> = SelfExclusion.ownToken.map { [$0] } ?? []
        store.shield.applications = apps.isEmpty ? nil : apps
        store.shield.applicationCategories = s.categoryTokens.isEmpty ? nil : .specific(s.categoryTokens, except: own)
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
        do {
            try center.startMonitoring(rule.activityName, during: schedule, events: events)
            let sel = rule.selection
            SharedStore.setDiagNote("monitorStart", "見守りを始めました：アプリ\(sel.applicationTokens.count)・カテゴリ\(sel.categoryTokens.count)・サイト\(sel.webDomainTokens.count)、\(minutes)分")
        } catch {
            SharedStore.setDiagNote("monitorStart", "見守りを始められませんでした：\(error.localizedDescription)")
            throw error
        }
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
