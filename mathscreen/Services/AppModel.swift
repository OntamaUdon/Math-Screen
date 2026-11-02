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
    var ruleProgress: [UUID: Int] = [:]     // ルールごとの、使った時間の目安（分）
    var isPremium = false          // 仮登録（0円）。本物の課金に差し替える予定
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
        isPremium = SharedStore.isPremium
        ruleProgress = Dictionary(uniqueKeysWithValues: rules.map { ($0.id, SharedStore.ruleProgress(ruleID: $0.id)) })
        authorization = AuthorizationCenter.shared.authorizationStatus
        ensurePendingProblem()
    }

    // MARK: 次に出す問題
    /// ブロック画面に表示する問題を、まだ決まっていなければ決めておく。
    func ensurePendingProblem() {
        for rule in rules { ensureRulePending(rule) }
        guard pendingProblem == nil else {
            prepareImages()      // 問題は決まっているが画像がまだ（更新直後・起動直後など）
            return
        }
        if let first = rules.first, let p = SharedStore.rulePending(ruleID: first.id).flatMap({ r in ProblemBank.all.first { $0.id == r.id } }) {
            setPendingProblem(p)
        } else {
            setPendingProblem(ProblemBank.pick(categories: settings.categories, difficulties: settings.difficulties))
        }
    }

    /// ルールの分野から、次に出す問題を用意する（まだなければ、または分野が変わっていれば）。
    private func ensureRulePending(_ rule: GuardRule) {
        if let r = SharedStore.rulePending(ruleID: rule.id),
           let p = ProblemBank.all.first(where: { $0.id == r.id }),
           rule.categories.contains(p.category), rule.difficulties.contains(p.difficulty) { return }
        refreshRulePending(rule)
    }

    private func refreshRulePending(_ rule: GuardRule, excluding: String? = nil) {
        guard let p = ProblemBank.pick(categories: rule.categories, difficulties: rule.difficulties, excluding: excluding) else { return }
        SharedStore.setRulePending(ruleID: rule.id, id: p.id, body: p.plain)
    }

    /// 2問目以降に出す問題の難しさ。ロック中のルールの難しさをまとめたもの。
    var challengeDifficulties: Set<Int> {
        let d = lockedRules.reduce(into: Set<Int>()) { $0.formUnion($1.difficulties) }
        return d.isEmpty ? settings.difficulties : d
    }

    /// 2問目以降に出す問題の分野。ロック中のルールの分野をまとめたもの。
    var challengeCategories: Set<String> {
        let cats = lockedRules.reduce(into: Set<String>()) { $0.formUnion($1.categories) }
        return cats.isEmpty ? settings.categories : cats
    }

    var pendingProblem: Problem? {
        SharedStore.pendingProblemID.flatMap { id in ProblemBank.all.first { $0.id == id } }
    }

    func setPendingProblem(_ problem: Problem?) {
        SharedStore.setPendingProblem(id: problem?.id, body: problem?.plain)
        prepareImages()
    }

    /// ブロック画面には問題を出さなくなったので、以前に作った問題の画像を片づけるだけ。
    private func prepareImages() {
        ProblemImageStore.prune(keeping: [])
    }

    var isLocked: Bool { !lockedRuleIDs.isEmpty }
    /// 解除に必要な正解数。ロック中のルールの問題数のうち、いちばん多いもの。
    var requiredCorrect: Int { max(1, lockedRules.map(\.questionCount).max() ?? 1) }
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
        var rule = rule
        // 同じ条件（時間・問題数・出題する分野・難しさ）のルールがすでにあれば、アプリを足して1つにまとめる
        if let i = rules.firstIndex(where: { $0.id != rule.id && $0.thresholdMinutes == rule.thresholdMinutes
                                              && $0.questionCount == rule.questionCount && $0.categories == rule.categories
                                              && $0.difficulties == rule.difficulties }) {
            var target = rules[i]
            target.selection.applicationTokens.formUnion(rule.selection.applicationTokens)
            target.selection.categoryTokens.formUnion(rule.selection.categoryTokens)
            target.selection.webDomainTokens.formUnion(rule.selection.webDomainTokens)
            if rules.contains(where: { $0.id == rule.id }) { delete(rule) }   // 編集前の元のルールは消す
            rule = target
        }
        if let i = rules.firstIndex(where: { $0.id == rule.id }) { rules[i] = rule } else { rules.append(rule) }
        SharedStore.saveRules(rules)
        ensureRulePending(rule)
        prepareImages()
        if !rule.isEnabled { release(rule.id) }
        restartMonitoring(rule)
    }

    func delete(_ rule: GuardRule) {
        MonitorScheduler.stop(rule)
        release(rule.id)
        SharedStore.removeRulePending(ruleID: rule.id)
        rules.removeAll { $0.id == rule.id }
        SharedStore.saveRules(rules)
    }

    func setEnabled(_ rule: GuardRule, _ enabled: Bool) {
        var r = rule
        r.isEnabled = enabled
        save(r)
    }

    private func restartMonitoring(_ rule: GuardRule) {
        SharedStore.clearRuleProgress(ruleID: rule.id)       // 使った時間の目安を 0 に戻す
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
            if let rule = rules.first(where: { $0.id == id }) {
                restartMonitoring(rule)
                refreshRulePending(rule, excluding: SharedStore.rulePending(ruleID: rule.id)?.id)   // 次のロックでは別の問題
            }
        }
        UNUserNotificationCenter.current().removeDeliveredNotifications(withIdentifiers: [ChallengeNotification.identifier])
        SharedStore.setPendingProblem(id: nil, body: nil)
        ensurePendingProblem()
    }

    // MARK: 設定
    func updateSettings(_ s: ChallengeSettings) {
        settings = s
        SharedStore.settings = s
        if let p = pendingProblem, !(s.categories.contains(p.category) && s.difficulties.contains(p.difficulty)) {
            setPendingProblem(ProblemBank.pick(categories: s.categories, difficulties: s.difficulties))
        }
    }

    // MARK: Premium（仮登録）
    func setPremium(_ on: Bool) {
        SharedStore.isPremium = on
        isPremium = on
    }

    // MARK: 集計
    /// 月曜はじまりのカレンダーの週ごとの正解数。[0] が今週、[1] が1週前…。まだ来ていない日は nil。
    func weeklyCorrect(weeks count: Int) -> [[Int?]] {
        var cal = Calendar(identifier: .gregorian)
        cal.firstWeekday = 2
        let now = Date()
        guard let thisWeek = cal.dateInterval(of: .weekOfYear, for: now)?.start else { return [] }
        return (0..<max(count, 1)).map { k in
            let weekStart = cal.date(byAdding: .day, value: -7 * k, to: thisWeek) ?? thisWeek
            return (0..<7).map { d -> Int? in
                let date = cal.date(byAdding: .day, value: d, to: weekStart) ?? weekStart
                if date > now && !cal.isDate(date, inSameDayAs: now) { return nil }
                return daily[SharedStore.dayKey(date)]?.correct ?? 0
            }
        }
    }

    /// 記録の画面に出す週の数（Premium のとき）。
    static let premiumWeeks = 8
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
