import SwiftUI
import StoreKit

/// App Store のレビューのお願い。Apple の標準の画面（SKStoreReviewController）だけを使う。
/// （独自のお願い画面は、審査ガイドライン 5.6.1 で認められていない。表示する・しないは Apple が決め、1年に最大3回まで。結果も教えてもらえない）
/// ロックを解除できた（問題に正解した）直後のうれしい場面で、3回目・15回目・40回目の解除のときだけ頼む。
@MainActor
enum ReviewPrompt {
    private static let countKey = "review.unlocks"
    private static let milestones: Set<Int> = [3, 15, 40]

    /// ロックを解除できたときに呼ぶ。
    static func afterUnlock() {
        guard !ScreenshotMode.active else { return }
        let d = UserDefaults.standard
        let n = d.integer(forKey: countKey) + 1
        d.set(n, forKey: countKey)
        guard milestones.contains(n) else { return }
        // 解除の画面が閉じて、アプリに戻ってから出す
        Task {
            try? await Task.sleep(for: .seconds(2))
            if let scene = UIApplication.shared.connectedScenes.first(where: { $0.activationState == .foregroundActive }) as? UIWindowScene {
                SKStoreReviewController.requestReview(in: scene)
            }
        }
    }
}
