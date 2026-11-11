import SwiftUI
import StoreKit

/// App Store のレビューのお願い。Apple の標準の画面（SKStoreReviewController）だけを使う。
/// （独自のお願い画面は、審査ガイドライン 5.6.1 で認められていない。表示する・しないは Apple が決め、1年に最大3回まで。結果も教えてもらえない）
/// ロックを解除できた（問題に正解した）直後のうれしい場面で、1〜5回目の解除のうち、ランダムに選んだ1回だけ頼む。
/// 設定の「レビューのお願いを出す」をオフにすると、それ以降は出さない。
@MainActor
enum ReviewPrompt {
    private static let countKey = "review.unlocks"
    private static let pickKey = "review.pick"        // 1〜5回目のうち、頼む回（はじめの1回だけ、ランダムに決める）
    private static let doneKey = "review.done"
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
        guard !d.bool(forKey: doneKey) else { return }
        let n = d.integer(forKey: countKey) + 1
        d.set(n, forKey: countKey)
        var pick = d.integer(forKey: pickKey)
        if pick == 0 { pick = Int.random(in: 1...5); d.set(pick, forKey: pickKey) }
        guard n == pick else {
            if n > 5 { d.set(true, forKey: doneKey) }
            return
        }
        d.set(true, forKey: doneKey)
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
