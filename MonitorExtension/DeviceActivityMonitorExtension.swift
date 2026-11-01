import DeviceActivity
import ManagedSettings
import Foundation

/// 利用時間がしきい値に達したらシールドをかけ、通知で問題へ誘導する。
final class DeviceActivityMonitorExtension: DeviceActivityMonitor {
    override func eventDidReachThreshold(_ event: DeviceActivityEvent.Name, activity: DeviceActivityName) {
        super.eventDidReachThreshold(event, activity: activity)
        guard let rule = SharedStore.rule(forActivity: activity), rule.isEnabled else { return }

        ShieldController.lock(rule)
        SharedStore.markLocked(rule.id)
        SharedStore.updateToday { $0.triggers += 1 }

        ChallengeNotification.send(
            title: "\(rule.name)：\(rule.thresholdMinutes)分たちました",
            body: "ひと休み。タップして1問解くと再開できます。"
        )
    }
}
