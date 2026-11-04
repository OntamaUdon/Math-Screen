import SwiftUI
import DeviceActivity
import FamilyControls

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

                VStack(spacing: 0) {
                    note("許可", AuthorizationCenter.shared.authorizationStatus == .approved ? "許可済み" : "許可されていません")
                    Divider().padding(.leading, 18)
                    note("オンのルール", "\(AppModel.shared.rules.filter(\.isEnabled).count) 件")
                    Divider().padding(.leading, 18)
                    note("見守り中の数（iOS側）", "\(DeviceActivityCenter().activities.count) 件")
                    Divider().padding(.leading, 18)
                    note("見守りの開始", SharedStore.diagNote("monitorStart") ?? "まだ開始していません")
                    Divider().padding(.leading, 18)
                    note("今日の開始", SharedStore.diagNote("monitorInterval") ?? "まだ動いていません")
                    Divider().padding(.leading, 18)
                    note("しきい値", SharedStore.diagNote("monitorEvent") ?? "まだ動いていません")
                }
                .card(padding: 0)

                Text("最後に動いた時刻です。「まだ動いていません」のままなら、その部分はまだ動いていません。")
                    .font(Theme.font(12)).foregroundStyle(Theme.inkSoft)
            }
            .padding(.horizontal, 20)
        }
        .isoBackground()
    }

    private func note(_ title: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title).font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
            Text(value).font(Theme.font(14, .semibold)).foregroundStyle(Theme.ink)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 18).padding(.vertical, 12)
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
