import SwiftUI
import StoreKit

/// App Store のレビューのお願い。Apple の標準の画面（SKStoreReviewController）だけを使う。
/// （独自のお願い画面は、審査ガイドライン 5.6.1 で認められていない。表示する・しないは Apple が決め、1年に最大3回まで。
///   レビューを書いたかどうかも、アプリには教えてもらえない）
/// ロックを解除できた（問題に正解した）直後に、1〜5 のランダムな回数の解除ごとに、くり返し頼む。
/// レビューを書いた人や、上限に達した人には、Apple の判断で出なくなる。
/// 設定の「レビューのお願いを出す」をオフにすると、それ以降は出さない。
@MainActor
enum ReviewPrompt {
    private static let leftKey = "review.left"         // 次に頼むまで、あと何回の解除か
    private static let optOutKey = "review.optOut"

    /// 設定のスイッチ。オフ（true）にすると、今後出さない。
    static var optedOut: Bool {
        get { UserDefaults.standard.bool(forKey: optOutKey) }
        set { UserDefaults.standard.set(newValue, forKey: optOutKey) }
    }

    /// ロックを解除できたときに呼ぶ。
    static func afterUnlock() {
        guard !ScreenshotMode.active, !optedOut else { return }
        let d = UserDefaults.standard
        var left = d.integer(forKey: leftKey)
        if left <= 0 { left = Int.random(in: 1...5) }       // はじめて：1〜5 回目のどこかで頼む
        left -= 1
        if left > 0 { d.set(left, forKey: leftKey); return }
        d.set(Int.random(in: 1...5), forKey: leftKey)        // 次は、また 1〜5 回あとに
        // 解除の画面が閉じて、アプリに戻ってから出す
        Task {
            try? await Task.sleep(for: .seconds(2))
            guard !optedOut else { return }
            if let scene = UIApplication.shared.connectedScenes.first(where: { $0.activationState == .foregroundActive }) as? UIWindowScene {
                SKStoreReviewController.requestReview(in: scene)
            }
        }
    }
}
