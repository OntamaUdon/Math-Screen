import SwiftUI
import FamilyControls

struct SettingsView: View {
    @Environment(AppModel.self) private var model
    @State private var confirmEmergency = false
    @State private var showGuide = false
    @State private var showDiagnostics = false
    @State private var showPasscodeSetup = false
    @State private var shareTick = 0
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
        .confirmationDialog("パスコードを消しますか？", isPresented: $confirmClearPasscode, titleVisibility: .visible) {
            Button("消す", role: .destructive) { ParentLock.shared.clearPasscode() }
        }
        .sheet(isPresented: $showGuide) { OnboardingView(replay: true).roomySheet() }
        .sheet(isPresented: $showDiagnostics) { DiagnosticsView().roomySheet() }
        .sheet(isPresented: $showPasscodeSetup) { PasscodeSetupView().roomySheet() }
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
            group("解くロックプラン", footer: "アプリロックと数学の問題、記録は無料です。英語・理科・社会・国語の問題などは、解くロックプランで使えます。初めての方は、7日間無料です。") {
                row("いまのプラン", value: model.isPremium ? "解くロックプラン" : "無料",
                    valueColor: model.isPremium ? Theme.tealDeep : Theme.inkSoft)
                Divider().padding(.leading, 18)
                action(Purchases.shared.isSubscribed ? "プランの管理（解約など）" : "プランを見る", color: Theme.tealDeep) {
                    if Purchases.shared.isSubscribed { Purchases.shared.openManage() } else { model.showPlan = true }
                }
                Divider().padding(.leading, 18)
                action("購入を復元", color: Theme.tealDeep) { Task { await Purchases.shared.restore() } }
                if Purchases.isTestFlight {        // TestFlight のときだけ。商品の審査が終わる前に、自分で試すため
                    Divider().padding(.leading, 18)
                    action(SharedStore.isPremium ? "テスト用：無料で使うをやめる" : "テスト用：無料で使う（TestFlight だけ）",
                           color: Theme.inkSoft) { model.setPremium(!SharedStore.isPremium) }
                }
            }

            if model.isPremium {
                group("保護者用設定", footer: "オンにすると、ルールの変更・設定・プランの管理に、パスコードが必要になります。使う人が知らない4桁の数字にしてください。この設定は、設定の画面の中にあるので、パスコードを知らないと、オフにできません。4回まちがえると、しばらく入力できなくなります。パスコードは、この端末の中だけに保存されます。") {
                    HStack {
                        Text("保護者用設定").font(Theme.font(16)).foregroundStyle(Theme.ink)
                        Spacer()
                        Toggle("", isOn: Binding(
                            get: { ParentLock.shared.isEnabled },
                            set: { on in
                                if on { if ParentLock.shared.hasPasscode { ParentLock.shared.setEnabled(true) } else { showPasscodeSetup = true } }
                                else { ParentLock.shared.setEnabled(false) }
                            }))
                            .labelsHidden().tint(Theme.tealDeep)
                    }
                    .padding(.horizontal, 18).padding(.vertical, 10)
                    if ParentLock.shared.hasPasscode {
                        Divider().padding(.leading, 18)
                        action("パスコードを変える", color: Theme.tealDeep) { showPasscodeSetup = true }
                        Divider().padding(.leading, 18)
                        action("パスコードを消す", color: Theme.danger) { confirmClearPasscode = true }
                    } else {
                        Divider().padding(.leading, 18)
                        action("パスコードを決める", color: Theme.tealDeep) { showPasscodeSetup = true }
                    }
                }
            }

            group("問題の共有", footer: "「分からない」や、正解したあとに、問題の画像を X や LINE などで共有できます。答えと解説は入りません。保護者用設定をオンにすると、最初はオフになります。") {
                HStack {
                    Text("問題を共有できる").font(Theme.font(16)).foregroundStyle(Theme.ink)
                    Spacer()
                    Toggle("", isOn: Binding(get: { ShareSetting.isAllowed }, set: { ShareSetting.set($0); shareTick += 1 }))
                        .labelsHidden().tint(Theme.tealDeep)
                }
                .padding(.horizontal, 18).padding(.vertical, 10)
                .id(shareTick)
            }

            group("レビューのお願い", footer: "ロックを解除できたあと、App Store のレビューをお願いする画面が出ることがあります（数回までです）。オフにすると、今後は出しません。") {
                HStack {
                    Text("レビューのお願いを出す").font(Theme.font(16)).foregroundStyle(Theme.ink)
                    Spacer()
                    Toggle("", isOn: Binding(get: { !ReviewPrompt.optedOut }, set: { ReviewPrompt.optedOut = !$0; shareTick += 1 }))
                        .labelsHidden().tint(Theme.tealDeep)
                }
                .padding(.horizontal, 18).padding(.vertical, 10)
                .id(shareTick)
            }

            group("スクリーンタイム", footer: checkedFooter) {
                row("アクセス", value: authLabel, valueColor: model.authorization == .approved ? Theme.tealDeep : Theme.danger)
                if model.authorization != .approved {
                    Divider().padding(.leading, 18)
                    action("許可する", color: Theme.tealDeep) { Task { await model.requestAuthorization() } }
                }
            }

            group("通知", footer: "ロック中に、ブロック画面から問題を開くために使います。") {
                row("通知", value: model.notificationStatus == .authorized ? "許可済み" : (model.notificationStatus == .denied ? "オフ" : "未設定"),
                    valueColor: model.notificationStatus == .authorized ? Theme.tealDeep : Theme.inkSoft)
                if model.notificationStatus != .authorized {
                    Divider().padding(.leading, 18)
                    action(model.notificationStatus == .denied ? "通知の設定を開く" : "許可する", color: Theme.tealDeep) {
                        if model.notificationStatus == .denied {
                            if let url = URL(string: UIApplication.openNotificationSettingsURLString) { UIApplication.shared.open(url) }
                        } else {
                            Task { await model.requestNotifications() }
                        }
                    }
                }
            }

            group("もしものとき", footer: "制限中でも、電話などの iOS の基本機能は使えます。どうしても必要なときは、問題を解かずに解除できます（記録に残ります）。") {
                action("緊急解除", color: model.isLocked ? Theme.danger : Theme.inkFaint) { confirmEmergency = true }
                    .disabled(!model.isLocked)
            }

            if LegalLinks.privacy != nil || LegalLinks.terms != nil {
                group("規約など") {
                    if let url = LegalLinks.terms {
                        link("利用規約") { UIApplication.shared.open(url) }
                    }
                    if LegalLinks.terms != nil && LegalLinks.privacy != nil { Divider().padding(.leading, 18) }
                    if let url = LegalLinks.privacy {
                        link("プライバシーポリシー") { UIApplication.shared.open(url) }
                    }
                }
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
