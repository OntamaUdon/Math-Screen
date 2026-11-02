import DeviceActivity
import ManagedSettings
import Foundation

/// 利用時間がしきい値に達したらシールドをかけ、通知で問題へ誘導する。
final class DeviceActivityMonitorExtension: DeviceActivityMonitor {
    /// 毎日 0 時に監視の期間が始まる。進み具合を 0 に戻す。
    override func intervalDidStart(for activity: DeviceActivityName) {
        super.intervalDidStart(for: activity)
        if let rule = SharedStore.rule(forActivity: activity) { SharedStore.clearRuleProgress(ruleID: rule.id) }
    }

    override func eventDidReachThreshold(_ event: DeviceActivityEvent.Name, activity: DeviceActivityName) {
        super.eventDidReachThreshold(event, activity: activity)
        SharedStore.recordDiag("monitor")
        guard let rule = SharedStore.rule(forActivity: activity), rule.isEnabled else { return }

        // 途中の節目（…p6 など）なら、進み具合を記録するだけで、ロックはかけない
        let name = event.rawValue
        if !name.hasSuffix(".limit"), let r = name.range(of: ".p", options: .backwards), let m = Int(name[r.upperBound...]) {
            SharedStore.setRuleProgress(ruleID: rule.id, minutes: m)
            return
        }
        SharedStore.setRuleProgress(ruleID: rule.id, minutes: rule.thresholdMinutes)

        ShieldController.lock(rule)
        SharedStore.markLocked(rule.id)
        if let p = SharedStore.rulePending(ruleID: rule.id) {      // このルールの分野から選んだ問題
            SharedStore.setPendingProblem(id: p.id, body: p.body)
        }
        SharedStore.pendingMinutes = rule.thresholdMinutes
        SharedStore.updateToday { $0.triggers += 1 }

        ChallengeNotification.send(
            title: "\(rule.thresholdMinutes)分たちました",
            body: "ひと休み。タップして\(rule.questionCount)問解くと再開できます。"
        )
    }
}
