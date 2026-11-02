import DeviceActivity
import ManagedSettings
import Foundation

/// 利用時間がしきい値に達したらシールドをかけ、通知で問題へ誘導する。
final class DeviceActivityMonitorExtension: DeviceActivityMonitor {
    override func eventDidReachThreshold(_ event: DeviceActivityEvent.Name, activity: DeviceActivityName) {
        super.eventDidReachThreshold(event, activity: activity)
        SharedStore.recordDiag("monitor")
        guard let rule = SharedStore.rule(forActivity: activity), rule.isEnabled else { return }

        ShieldController.lock(rule)
        SharedStore.markLocked(rule.id)
        if let p = SharedStore.rulePending(ruleID: rule.id) {      // このルールの分野から選んだ問題
            SharedStore.setPendingProblem(id: p.id, body: p.body)
        }
        SharedStore.updateToday { $0.triggers += 1 }

        ChallengeNotification.send(
            title: "\(rule.thresholdMinutes)分たちました",
            body: "ひと休み。タップして\(rule.questionCount)問解くと再開できます。"
        )
    }
}
