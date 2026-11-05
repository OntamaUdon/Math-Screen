import Foundation
import StoreKit
import UIKit

/// 解くロックプランの課金（StoreKit 2）。月額300円・年額2,400円。初めての購入には7日間の無料トライアルが付く
/// （トライアルや価格は、App Store Connect の商品の設定で決まる）。
@MainActor
@Observable
final class Purchases {
    static let shared = Purchases()

    /// App Store Connect の商品ID（自動更新サブスクリプション。同じグループに入っている）。
    static let monthlyID = "com.ontamaudon.qlock.plan.monthly"
    static let yearlyID = "com.ontamaudon.qlock.plan.yearly"
    private static let ids = [monthlyID, yearlyID]

    enum State { case unknown, subscribed, notSubscribed }

    /// まだ確かめていない間は .unknown。このあいだは、ロックを止めない（起動直後に一瞬だけ「未契約」に見えるのを防ぐ）。
    private(set) var state: State = .unknown
    var isSubscribed: Bool { state == .subscribed }
    private(set) var products: [Product] = []
    private(set) var introEligible = false
    private(set) var message: String?
    private(set) var busy = false
    private var updates: Task<Void, Never>?

    private init() {}

    /// TestFlight（サンドボックス）のビルドか。App Store の本番では false。
    /// TestFlight のときだけ、設定に「テスト用：無料で使う」を出す（商品の審査が終わる前に、自分で試すため）。
    static var isTestFlight: Bool { Bundle.main.appStoreReceiptURL?.lastPathComponent == "sandboxReceipt" }

    /// アプリの起動時に1回。購入の更新を受け取り、いまの状態と商品を読み込む。
    func start() {
        guard updates == nil else { return }
        updates = Task { [weak self] in
            for await result in Transaction.updates {
                if case .verified(let t) = result { await t.finish() }
                await self?.refresh()
            }
        }
        Task { await refresh(); await load() }
    }

    func load() async {
        do {
            products = try await Product.products(for: Self.ids).sorted { $0.price < $1.price }
            if let p = products.first { introEligible = await p.subscription?.isEligibleForIntroOffer ?? false }
            if products.isEmpty { message = "プランの情報を読み込めませんでした。しばらくしてから、もう一度お試しください。" }
        } catch {
            message = "プランの情報を読み込めませんでした。通信を確かめて、もう一度お試しください。"
        }
    }

    /// 購入する。成功したら true（取り消したときは false）。
    @discardableResult
    func purchase(_ product: Product) async -> Bool {
        message = nil; busy = true; defer { busy = false }
        do {
            switch try await product.purchase() {
            case .success(let result):
                guard case .verified(let t) = result else { message = "購入を確認できませんでした。"; return false }
                await t.finish()
                await refresh()
                return isSubscribed
            case .userCancelled:
                return false
            case .pending:
                message = "購入の承認待ちです。承認されると、使えるようになります。"
                return false
            @unknown default:
                return false
            }
        } catch {
            message = "購入できませんでした。もう一度お試しください。"
            return false
        }
    }

    /// 「購入を復元」。App Store と同期して、いまの状態を調べ直す。
    func restore() async {
        message = nil; busy = true; defer { busy = false }
        do { try await AppStore.sync() } catch { message = "復元できませんでした。通信を確かめて、もう一度お試しください。" }
        await refresh()
        if !isSubscribed && message == nil { message = "復元できる購入が見つかりませんでした。" }
    }

    /// 有効なサブスクリプション（無料トライアル中を含む）があるかを調べる。解約・返金されたものは含まない。
    func refresh() async {
        var active = false
        for await result in Transaction.currentEntitlements {
            if case .verified(let t) = result, Self.ids.contains(t.productID), t.revocationDate == nil {
                if let exp = t.expirationDate, exp < Date() { continue }
                active = true
            }
        }
        state = active ? .subscribed : .notSubscribed
        AppModel.shared.refresh()
    }

    /// 解約・管理の画面（Apple のサブスクリプションの画面）を開く。
    func openManage() {
        if let url = URL(string: "https://apps.apple.com/account/subscriptions") { UIApplication.shared.open(url) }
    }
}
