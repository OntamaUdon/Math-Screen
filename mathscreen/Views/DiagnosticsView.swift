import SwiftUI

/// 診断：ブロック画面が出ないときに、どの部分が動いたかを確認する画面。
struct DiagnosticsView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                HStack {
                    Text("診断").font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
                    Spacer()
                    Button("とじる") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                .padding(.top, 24)

                VStack(spacing: 0) {
                    row("使用時間の監視", key: "monitor")
                    Divider().padding(.leading, 18)
                    row("ブロック画面の表示", key: "shieldConfig")
                    Divider().padding(.leading, 18)
                    row("ブロック画面のボタン", key: "shieldAction")
                    Divider().padding(.leading, 18)
                    HStack {
                        Text("ブロック画面の外観").font(Theme.font(15)).foregroundStyle(Theme.inkSoft)
                        Spacer()
                        Text(SharedStore.diagNote("shieldStyle") ?? "まだ動いていません")
                            .font(Theme.font(14, .semibold)).foregroundStyle(Theme.ink)
                    }
                    .padding(.horizontal, 18).padding(.vertical, 14)
                }
                .card(padding: 0)

                Text("最後に動いた時刻です。「まだ動いていません」のままなら、その部分はまだ動いていません。")
                    .font(Theme.font(12)).foregroundStyle(Theme.inkSoft)
            }
            .padding(.horizontal, 20)
        }
        .isoBackground()
    }

    private func row(_ title: String, key: String) -> some View {
        let date = SharedStore.diagDate(key)
        return HStack {
            Text(title).font(Theme.font(15)).foregroundStyle(Theme.inkSoft)
            Spacer()
            Text(date.map { $0.formatted(date: .abbreviated, time: .standard) } ?? "まだ動いていません")
                .font(Theme.font(14, .semibold)).foregroundStyle(date == nil ? Theme.danger : Theme.ink)
        }
        .padding(.horizontal, 18).padding(.vertical, 12)
    }
}
