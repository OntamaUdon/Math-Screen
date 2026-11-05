import SwiftUI
import StoreKit

/// 解くロックプランの案内と購入の画面。
struct PlanView: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(AppModel.self) private var model
    /// スクリーンショット用：商品の情報を読み込まずに、見本の価格を出す（審査用の画像を撮るときだけ）。
    var sample = false
    private let purchases = Purchases.shared

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                HStack {
                    Text("解くロックプラン").font(Theme.font(24, .bold)).foregroundStyle(Theme.ink)
                    Spacer()
                    Button("閉じる") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                .padding(.top, 24)

                if purchases.isSubscribed {
                    VStack(alignment: .leading, spacing: 10) {
                        Label("プランを利用中です", systemImage: "checkmark.circle.fill")
                            .font(Theme.font(17, .bold)).foregroundStyle(Theme.tealDeep)
                        Text("解約や、お支払いの確認は、下のボタンから行えます。")
                            .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                        Button("プランの管理（解約など）") { purchases.openManage() }.buttonStyle(.secondary)
                    }
                    .card()
                } else {
                    what
                    products
                }

                if let message = purchases.message {
                    Text(message).font(Theme.font(13, .semibold)).foregroundStyle(Theme.danger)
                }

                Button("購入を復元") { Task { await purchases.restore() } }
                    .buttonStyle(.quiet)
                    .disabled(purchases.busy)

                disclosure
            }
            .padding(.horizontal, 20).padding(.bottom, 40)
        }
        .scrollIndicators(.hidden)
        .isoBackground()
        .task { if purchases.products.isEmpty { await purchases.load() } }
        .onChange(of: purchases.isSubscribed) { _, on in if on { model.refresh() } }
    }

    private var what: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("無料で使えるもの").font(Theme.font(14, .bold)).foregroundStyle(Theme.inkSoft)
            Text("問題集（見る・探す・解く）と、記録。")
                .font(Theme.font(15)).foregroundStyle(Theme.ink)
            Divider()
            Text("プランで使えるもの").font(Theme.font(14, .bold)).foregroundStyle(Theme.inkSoft)
            VStack(alignment: .leading, spacing: 6) {
                feature("アプリロック（使いすぎたら問題が出て、解くまでロック）")
                feature("ロック中の「別の問題」")
                feature("問題の投稿")
                feature("保護者用のパスコード")
            }
        }
        .card()
    }

    private func feature(_ text: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: "checkmark").font(.system(size: 13, weight: .bold)).foregroundStyle(Theme.tealDeep).padding(.top, 3)
            Text(text).font(Theme.font(15)).foregroundStyle(Theme.ink).fixedSize(horizontal: false, vertical: true)
        }
    }

    @ViewBuilder private var products: some View {
        if sample {
            VStack(spacing: 14) {
                sampleButton("月額　¥300 / 月", "最初の7日間は無料", primary: false)
                sampleButton("年額　¥2,400 / 年", "最初の7日間は無料（月あたり約200円）", primary: true)
            }
        } else if purchases.products.isEmpty {
            VStack(alignment: .leading, spacing: 10) {
                Text(purchases.message == nil ? "プランの情報を読み込み中です…" : "プランの情報を読み込めませんでした。")
                    .font(Theme.font(14)).foregroundStyle(Theme.inkSoft)
                Button("もう一度読み込む") { Task { await purchases.load() } }.buttonStyle(.secondary)
            }
            .card()
        } else {
            VStack(spacing: 14) {
                ForEach(purchases.products, id: \.id) { p in
                    Button { Task { await purchases.purchase(p) } } label: {
                        VStack(spacing: 2) {
                            Text(title(p)).font(Theme.font(17, .bold))
                            Text(detail(p)).font(Theme.font(13)).opacity(0.9)
                        }
                        .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(p.id == Purchases.yearlyID ? .primary : .secondary)
                    .disabled(purchases.busy)
                }
            }
        }
    }

    private func sampleButton(_ title: String, _ detail: String, primary: Bool) -> some View {
        Button {} label: {
            VStack(spacing: 2) {
                Text(title).font(Theme.font(17, .bold))
                Text(detail).font(Theme.font(13)).opacity(0.9)
            }
            .frame(maxWidth: .infinity)
        }
        .buttonStyle(primary ? .primary : .secondary)
    }

    private func title(_ p: Product) -> String {
        let unit = p.id == Purchases.yearlyID ? "年" : "月"
        return "\(p.id == Purchases.yearlyID ? "年額" : "月額")　\(p.displayPrice) / \(unit)"
    }

    private func detail(_ p: Product) -> String {
        var s = purchases.introEligible ? "最初の7日間は無料" : "いつでも解約できます"
        if p.id == Purchases.yearlyID { s += "（月あたり約\(Int((NSDecimalNumber(decimal: p.price).doubleValue / 12).rounded()))円）" }
        return s
    }

    /// Apple の審査で、購入の前に見せる必要がある説明。
    private var disclosure: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("・無料トライアルのあとは、選んだプランの料金が、Apple ID に請求されます。")
            Text("・期間の終了の24時間前までに解約しない限り、自動で更新されます。無料トライアルの期間中に解約すると、請求されません。")
            Text("・解約は、iPhone の「設定」→ 自分の名前 →「サブスクリプション」から行えます。")
            if LegalLinks.terms != nil || LegalLinks.privacy != nil {
                HStack(spacing: 16) {
                    if let u = LegalLinks.terms { Link("利用規約", destination: u) }
                    if let u = LegalLinks.privacy { Link("プライバシーポリシー", destination: u) }
                }
                .font(Theme.font(13, .semibold)).foregroundStyle(Theme.tealDeep)
            }
        }
        .font(Theme.font(12)).foregroundStyle(Theme.inkSoft)
        .fixedSize(horizontal: false, vertical: true)
    }
}
