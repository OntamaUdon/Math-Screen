import SwiftUI
import FamilyControls
import UserNotifications

@MainActor
@Observable
final class AppModel {
    static let shared = AppModel()

    var rules: [GuardRule] = []
    var lockedRuleIDs: Set<UUID> = []
    var settings = ChallengeSettings()
    var daily: [String: DailyStats] = [:]
    var currentStreak = 0
    var bestStreak = 0
    var authorization: AuthorizationStatus = .notDetermined
    var hasOnboarded = false
    var showChallenge = false
    var lastError: String?

    private init() { refresh() }

    // MARK: 状態の読み込み（拡張が書き換えるので前面に来るたびに呼ぶ）
    func refresh() {
        rules = SharedStore.loadRules()
        lockedRuleIDs = SharedStore.lockedRuleIDs
        settings = SharedStore.settings
        daily = SharedStore.loadDaily()
        currentStreak = SharedStore.currentStreak
        bestStreak = SharedStore.bestStreak
        hasOnboarded = SharedStore.hasOnboarded
        authorization = AuthorizationCenter.shared.authorizationStatus
        ensurePendingProblem()
    }

    // MARK: 次に出す問題
    /// ブロック画面に表示する問題を、まだ決まっていなければ決めておく。
    func ensurePendingProblem() {
        guard SharedStore.pendingProblemID.flatMap({ id in ProblemBank.all.first { $0.id == id } }) == nil else { return }
        setPendingProblem(ProblemBank.pick(categories: settings.categories, difficulties: settings.difficulties))
    }

    var pendingProblem: Problem? {
        SharedStore.pendingProblemID.flatMap { id in ProblemBank.all.first { $0.id == id } }
    }

    func setPendingProblem(_ problem: Problem?) {
        SharedStore.setPendingProblem(id: problem?.id, body: problem?.plain)
    }

    var isLocked: Bool { !lockedRuleIDs.isEmpty }
    var lockedRules: [GuardRule] { rules.filter { lockedRuleIDs.contains($0.id) } }
    var today: DailyStats { daily[SharedStore.dayKey()] ?? DailyStats() }

    // MARK: 権限
    func requestAuthorization() async {
        do {
            try await AuthorizationCenter.shared.requestAuthorization(for: .individual)
        } catch {
            lastError = "スクリーンタイムへのアクセスが許可されませんでした。（\(error.localizedDescription)）"
        }
        _ = try? await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge])
        authorization = AuthorizationCenter.shared.authorizationStatus
    }

    func finishOnboarding() {
        SharedStore.hasOnboarded = true
        hasOnboarded = true
    }

    // MARK: ルール
    func save(_ rule: GuardRule) {
        if let i = rules.firstIndex(where: { $0.id == rule.id }) { rules[i] = rule } else { rules.append(rule) }
        SharedStore.saveRules(rules)
        if !rule.isEnabled { release(rule.id) }
        restartMonitoring(rule)
    }

    func delete(_ rule: GuardRule) {
        MonitorScheduler.stop(rule)
        release(rule.id)
        rules.removeAll { $0.id == rule.id }
        SharedStore.saveRules(rules)
    }

    func setEnabled(_ rule: GuardRule, _ enabled: Bool) {
        var r = rule
        r.isEnabled = enabled
        save(r)
    }

    private func restartMonitoring(_ rule: GuardRule) {
        do {
            if rule.isEnabled { try MonitorScheduler.start(rule) } else { MonitorScheduler.stop(rule) }
        } catch {
            lastError = "監視を開始できませんでした。（\(error.localizedDescription)）"
        }
    }

    private func release(_ id: UUID) {
        ShieldController.unlock(ruleID: id)
        SharedStore.markUnlocked(id)
        lockedRuleIDs = SharedStore.lockedRuleIDs
    }

    // MARK: 解答の記録
    func recordAnswer(correct: Bool) {
        SharedStore.updateToday {
            $0.attempts += 1
            if correct { $0.correct += 1 }
        }
        SharedStore.currentStreak = correct ? SharedStore.currentStreak + 1 : 0
        refresh()
    }

    /// 規定数に正解した：すべてのロックを外し、カウントをリセットして監視を再開する。
    func completeChallenge() {
        unlockAll()
        SharedStore.updateToday { $0.unlocks += 1 }
        refresh()
        showChallenge = false
    }

    /// 緊急解除（記録には残る）。
    func emergencyUnlock() {
        unlockAll()
        SharedStore.updateToday { $0.emergencyUnlocks += 1 }
        refresh()
        showChallenge = false
    }

    private func unlockAll() {
        for id in lockedRuleIDs {
            release(id)
            if let rule = rules.first(where: { $0.id == id }) { restartMonitoring(rule) }
        }
        UNUserNotificationCenter.current().removeDeliveredNotifications(withIdentifiers: [ChallengeNotification.identifier])
        // 次のロックでは別の問題を出す
        setPendingProblem(ProblemBank.pick(categories: settings.categories, difficulties: settings.difficulties,
                                           excluding: SharedStore.pendingProblemID))
    }

    // MARK: 設定
    func updateSettings(_ s: ChallengeSettings) {
        settings = s
        SharedStore.settings = s
        if let p = pendingProblem, !(s.categories.contains(p.category) && s.difficulties.contains(p.difficulty)) {
            setPendingProblem(ProblemBank.pick(categories: s.categories, difficulties: s.difficulties))
        }
    }

    // MARK: 集計
    var totals: DailyStats {
        daily.values.reduce(into: DailyStats()) { t, d in
            t.triggers += d.triggers; t.unlocks += d.unlocks; t.correct += d.correct
            t.attempts += d.attempts; t.emergencyUnlocks += d.emergencyUnlocks
        }
    }

    /// 1問以上正解した日が今日（または昨日）まで何日続いているか。
    var dayStreak: Int {
        let cal = Calendar(identifier: .gregorian)
        var date = Date()
        if (daily[SharedStore.dayKey(date)]?.correct ?? 0) == 0 {
            date = cal.date(byAdding: .day, value: -1, to: date) ?? date
        }
        var count = 0
        while (daily[SharedStore.dayKey(date)]?.correct ?? 0) > 0 {
            count += 1
            date = cal.date(byAdding: .day, value: -1, to: date) ?? date
        }
        return count
    }

    /// 直近7日分（古い順）。
    var lastWeek: [(label: String, stats: DailyStats)] {
        let cal = Calendar(identifier: .gregorian)
        let f = DateFormatter()
        f.locale = Locale(identifier: "ja_JP")
        f.dateFormat = "E"
        return (0..<7).reversed().map { offset in
            let date = cal.date(byAdding: .day, value: -offset, to: Date()) ?? Date()
            return (f.string(from: date), daily[SharedStore.dayKey(date)] ?? DailyStats())
        }
    }
}
