import Foundation
import StoreKit

/// 解くロックプランの課金（StoreKit 2）。まだ画面にはつないでいない（設定の「仮登録」のまま）。
/// App Store Connect に下の商品を登録してから、設定画面とつなぐ。手順は docs/BILLING.md。
@MainActor
@Observable
final class Purchases {
    static let shared = Purchases()

    /// App Store Connect に登録する商品ID（自動更新サブスクリプション。同じグループに入れる）。
    static let monthlyID = "com.ontamaudon.qlock.plan.monthly"      // 月300円
    static let yearlyID = "com.ontamaudon.qlock.plan.yearly"        // 年2,400円
    private static let ids = [monthlyID, yearlyID]

    private(set) var products: [Product] = []
    private(set) var isSubscribed = false
    private(set) var message: String?
    private var updates: Task<Void, Never>?

    private init() {}

    /// アプリの起動時に1回。購入の更新を受け取り、いまの状態と商品を読み込む。
    func start() {
        guard updates == nil else { return }
        updates = Task { [weak self] in
            for await result in Transaction.updates {
                if case .verified(let t) = result { await t.finish() }
                await self?.refresh()
            }
        }
        Task { await load(); await refresh() }
    }

    func load() async {
        do {
            products = try await Product.products(for: Self.ids).sorted { $0.price < $1.price }
        } catch {
            message = "商品を読み込めませんでした。"
        }
    }

    /// 購入する。成功したら true（ユーザーが取り消したときは false）。
    @discardableResult
    func purchase(_ product: Product) async -> Bool {
        message = nil
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
                message = "購入の承認待ちです。"
                return false
            @unknown default:
                return false
            }
        } catch {
            message = "購入できませんでした。"
            return false
        }
    }

    /// 「購入を復元」。App Store と同期して、いまの状態を調べ直す。
    func restore() async {
        message = nil
        do { try await AppStore.sync() } catch { message = "復元できませんでした。" }
        await refresh()
    }

    /// 有効なサブスクリプションがあるかを調べる（解約・返金されたものは含まない）。
    func refresh() async {
        var active = false
        for await result in Transaction.currentEntitlements {
            if case .verified(let t) = result, Self.ids.contains(t.productID), t.revocationDate == nil {
                if let exp = t.expirationDate, exp < Date() { continue }
                active = true
            }
        }
        isSubscribed = active
    }
}
