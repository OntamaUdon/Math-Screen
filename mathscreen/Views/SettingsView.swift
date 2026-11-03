import SwiftUI
import FamilyControls

struct SettingsView: View {
    @Environment(AppModel.self) private var model
    @State private var confirmEmergency = false
    @State private var showGuide = false
    @State private var showDiagnostics = false
    @State private var confirmDeleteData = false
    @State private var dataMessage: String?
    @State private var showPasscodeSetup = false
    @State private var confirmClearPasscode = false

    var body: some View {
        Screen(title: "設定") {
            if ParentLock.shared.needsLock { lockedView } else { content }
        }
        .onDisappear { ParentLock.shared.lock() }
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
        .confirmationDialog("パスコードを消しますか？", isPresented: $confirmClearPasscode, titleVisibility: .visible) {
            Button("消す", role: .destructive) { ParentLock.shared.clearPasscode() }
        }
        .sheet(isPresented: $showGuide) { OnboardingView(replay: true) }
        .sheet(isPresented: $showDiagnostics) { DiagnosticsView() }
        .sheet(isPresented: $showPasscodeSetup) { PasscodeSetupView() }
    }

    private var lockedView: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("保護者用", systemImage: "lock.fill").font(Theme.font(17, .heavy)).foregroundStyle(Theme.ink)
            Text("設定は、パスコードを知っている人だけが開けます。").font(Theme.font(14)).foregroundStyle(Theme.inkSoft)
            Button("パスコードを入れる") { ParentLock.shared.request {} }.buttonStyle(.primary)
        }
        .card()
    }

    @ViewBuilder private var content: some View {
            group("Premium", footer: "いまは、お金のかからない仮登録です。Premium では、過去の成績・問題の投稿・保護者用パスコードが使えます。") {
                row("いまのプラン", value: model.isPremium ? "Premium（仮登録中）" : "無料",
                    valueColor: model.isPremium ? Theme.tealDeep : Theme.inkSoft)
                Divider().padding(.leading, 18)
                action(model.isPremium ? "仮登録を解除する" : "仮登録する（0円）",
                       color: model.isPremium ? Theme.danger : Theme.tealDeep) { model.setPremium(!model.isPremium) }
            }

            if model.isPremium {
                group("保護者用パスコード", footer: "ルールの変更・設定・Premium の管理を、パスコードで守ります。4回まちがえると、しばらく入力できなくなります（最後の入力から6時間たつと元に戻ります）。パスコードは、この端末の中だけに保存されます。") {
                    row("パスコード", value: ParentLock.shared.hasPasscode ? "設定済み" : "未設定",
                        valueColor: ParentLock.shared.hasPasscode ? Theme.tealDeep : Theme.inkSoft)
                    Divider().padding(.leading, 18)
                    action(ParentLock.shared.hasPasscode ? "パスコードを変える" : "パスコードを決める", color: Theme.tealDeep) { showPasscodeSetup = true }
                    if ParentLock.shared.hasPasscode {
                        Divider().padding(.leading, 18)
                        action("パスコードを消す", color: Theme.danger) { confirmClearPasscode = true }
                    }
                }
            }

            group("スクリーンタイム", footer: checkedFooter) {
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

    /// 許可の状態を最後に確かめた時刻（アプリを開いたときだけ確かめられる）。
    private var checkedFooter: String? {
        guard let checked = ParentLock.authorizationCheckedAt else { return nil }
        let f = DateFormatter(); f.locale = Locale(identifier: "ja_JP"); f.dateFormat = "M/d H:mm"
        var t = "アプリを開いたときに確かめています。最後に確かめたのは \(f.string(from: checked)) です。"
        if model.authorization != .approved, let ok = ParentLock.authorizationApprovedAt {
            t += "許可を最後に確かめられたのは \(f.string(from: ok)) です。"
        }
        return t
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
