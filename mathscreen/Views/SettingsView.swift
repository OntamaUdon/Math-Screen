import SwiftUI
import FamilyControls

struct SettingsView: View {
    @Environment(AppModel.self) private var model
    @State private var confirmEmergency = false
    @State private var showGuide = false
    @State private var showDiagnostics = false
    @State private var confirmDeleteData = false
    @State private var dataMessage: String?

    var body: some View {
        Screen(title: "設定") {
            group("Premium", footer: "いまは、お金のかからない仮登録です。Premium では、過去の成績・ヒント・問題の変更が使えます。") {
                row("いまのプラン", value: model.isPremium ? "Premium（仮登録中）" : "無料",
                    valueColor: model.isPremium ? Theme.tealDeep : Theme.inkSoft)
                Divider().padding(.leading, 18)
                action(model.isPremium ? "仮登録を解除する" : "仮登録する（0円）",
                       color: model.isPremium ? Theme.danger : Theme.tealDeep) { model.setPremium(!model.isPremium) }
            }

            group("スクリーンタイム") {
                row("アクセス", value: authLabel, valueColor: model.authorization == .approved ? Theme.tealDeep : Theme.danger)
                if model.authorization != .approved {
                    Divider().padding(.leading, 18)
                    action("許可する", color: Theme.tealDeep) { Task { await model.requestAuthorization() } }
                }
            }

            group("コミュニティ", footer: dataMessage ?? "投稿した問題・通報・ブロックの記録をサーバーから消します。ほかの人の画面からも消えます。") {
                action("投稿したデータをすべて削除", color: Theme.danger) { confirmDeleteData = true }
            }

            group("もしものとき", footer: "制限中でも、電話などの iOS の基本機能は使えます。どうしても必要なときは、問題を解かずに解除できます（記録に残ります）。") {
                action("緊急解除", color: model.isLocked ? Theme.danger : Theme.inkFaint) { confirmEmergency = true }
                    .disabled(!model.isLocked)
            }

            group("このアプリについて") {
                link("使い方を見る") { showGuide = true }
                Divider().padding(.leading, 18)
                link("診断") { showDiagnostics = true }
                Divider().padding(.leading, 18)
                row("バージョン", value: Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "",
                    valueColor: Theme.inkSoft)
            }
        }
        .alert("緊急解除しますか？", isPresented: $confirmEmergency) {
            Button("緊急解除する", role: .destructive) { model.emergencyUnlock() }
            Button("緊急解除しない", role: .cancel) {}
        } message: {
            Text("問題を解かずにすべての制限を外します。記録には「緊急解除」として残ります。")
        }
        .confirmationDialog("投稿したデータをすべて削除しますか？", isPresented: $confirmDeleteData, titleVisibility: .visible) {
            Button("削除する", role: .destructive) {
                Task {
                    do { try await Community.shared.deleteMyData(); dataMessage = "削除しました。" }
                    catch { dataMessage = error.localizedDescription }
                }
            }
        }
        .sheet(isPresented: $showGuide) { OnboardingView(replay: true) }
        .sheet(isPresented: $showDiagnostics) { DiagnosticsView() }
    }

    private var authLabel: String {
        switch model.authorization {
        case .approved: "許可済み"
        case .denied: "拒否されています"
        default: "未設定"
        }
    }

    // MARK: 部品
    private func row(_ title: String, value: String, valueColor: Color) -> some View {
        HStack {
            Text(title).font(Theme.font(16)).foregroundStyle(Theme.ink)
            Spacer()
            Text(value).font(Theme.font(15, .semibold)).foregroundStyle(valueColor)
        }
        .padding(.horizontal, 18).padding(.vertical, 14)
    }

    private func action(_ title: String, color: Color, _ run: @escaping () -> Void) -> some View {
        Button(action: run) {
            Text(title).font(Theme.font(16, .semibold)).foregroundStyle(color)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 18).padding(.vertical, 14)
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }

    private func link(_ title: String, _ run: @escaping () -> Void) -> some View {
        Button(action: run) {
            HStack {
                Text(title).font(Theme.font(16)).foregroundStyle(Theme.ink)
                Spacer()
                Image(systemName: "chevron.right").font(.system(size: 13, weight: .semibold)).foregroundStyle(Theme.inkFaint)
            }
            .padding(.horizontal, 18).padding(.vertical, 14)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }

    /// 見出し + 白いリスト + 補足文。
    private func group<C: View>(_ title: String, footer: String? = nil, @ViewBuilder content: () -> C) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            SectionLabel(title)
            VStack(spacing: 0) { content() }
                .card(padding: 0)
            if let footer {
                Text(footer).font(Theme.font(12)).foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}
