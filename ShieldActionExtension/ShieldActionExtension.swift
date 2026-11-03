import ManagedSettings
import Foundation

/// シールドのボタンが押されたときの処理。
/// iOS ではシールドから直接アプリを開けないため、通知を送ってからシールドを閉じる（Opal / ScreenZen と同じ方式）。
final class ShieldActionExtension: ShieldActionDelegate {
    override func handle(action: ShieldAction, for application: ApplicationToken,
                         completionHandler: @escaping (ShieldActionResponse) -> Void) {
        respond(to: action, completionHandler)
    }

    override func handle(action: ShieldAction, for webDomain: WebDomainToken,
                         completionHandler: @escaping (ShieldActionResponse) -> Void) {
        respond(to: action, completionHandler)
    }

    override func handle(action: ShieldAction, for category: ActivityCategoryToken,
                         completionHandler: @escaping (ShieldActionResponse) -> Void) {
        respond(to: action, completionHandler)
    }

    private func respond(to action: ShieldAction, _ completionHandler: @escaping (ShieldActionResponse) -> Void) {
        SharedStore.recordDiag("shieldAction")
        switch action {
        case .primaryButtonPressed:
            ChallengeNotification.send(
                title: "解くロック：問題が届きました",
                body: "この通知をタップすると問題が開きます。正解すると、またアプリを使えるよ！"
            ) {
                completionHandler(.close)
            }
        case .secondaryButtonPressed:
            completionHandler(.close)
        @unknown default:
            completionHandler(.close)
        }
    }
}
