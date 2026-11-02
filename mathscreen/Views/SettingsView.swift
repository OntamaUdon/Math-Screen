import SwiftUI
import FamilyControls

struct SettingsView: View {
    @Environment(AppModel.self) private var model
    @State private var confirmEmergency = false
    @State private var showGuide = false

    var body: some View {
        let s = model.settings
        Screen(title: "設定") {
            group("出題する分野") {
                ForEach(ProblemCategory.allCases) { c in
                    toggleRow(c.label, isOn: s.categories.contains(c.rawValue)) { on in
                        var n = s
                        if on { n.categories.insert(c.rawValue) } else if n.categories.count > 1 { n.categories.remove(c.rawValue) }
                        model.updateSettings(n)
                    }
                }
            }

            group("難易度", footer: "出題対象：\(ProblemBank.candidates(categories: s.categories, difficulties: s.difficulties).count) 問") {
                ForEach(Difficulty.allCases) { d in
                    toggleRow(d.label, isOn: s.difficulties.contains(d.rawValue)) { on in
                        var n = s
                        if on { n.difficulties.insert(d.rawValue) } else if n.difficulties.count > 1 { n.difficulties.remove(d.rawValue) }
                        model.updateSettings(n)
                    }
                }
            }

            group("スクリーンタイム") {
                HStack {
                    Text("アクセス").font(Theme.font(16)).foregroundStyle(Theme.ink)
                    Spacer()
                    Text(authLabel).font(Theme.font(15, .semibold))
                        .foregroundStyle(model.authorization == .approved ? Theme.tealDeep : Theme.danger)
                }
                .padding(.horizontal, 18).padding(.vertical, 14)
                if model.authorization != .approved {
                    Divider()
                    Button("許可する") { Task { await model.requestAuthorization() } }
                        .font(Theme.font(16, .semibold)).foregroundStyle(Theme.tealDeep)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal, 18).padding(.vertical, 14)
                }
            }

            group("このアプリについて") {
                Button { showGuide = true } label: {
                    HStack {
                        Text("使い方を見る").font(Theme.font(16)).foregroundStyle(Theme.ink)
                        Spacer()
                        Image(systemName: "chevron.right").font(.system(size: 13, weight: .semibold)).foregroundStyle(Theme.inkFaint)
                    }
                    .padding(.horizontal, 18).padding(.vertical, 14)
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
            }

            group("診断", footer: "ブロック画面が出ない・普通の画面が出るときに、どの部分が動いたかを確認するための表示です。「まだ動いていません」のままなら、その部分が動いていません。") {
                diagRow("使用時間の監視", key: "monitor")
                Divider().padding(.leading, 18)
                diagRow("ブロック画面の表示", key: "shieldConfig")
                Divider().padding(.leading, 18)
                diagRow("ブロック画面のボタン", key: "shieldAction")
                Divider().padding(.leading, 18)
                HStack {
                    Text("問題の画像").font(Theme.font(15)).foregroundStyle(Theme.inkSoft)
                    Spacer()
                    Text(ProblemImageStore.exists(forID: SharedStore.pendingProblemID ?? "") ? "あり" : "なし")
                        .font(Theme.font(15, .semibold)).foregroundStyle(Theme.ink)
                }
                .padding(.horizontal, 18).padding(.vertical, 12)
            }

            group("もしものとき", footer: "制限中でも電話・メッセージなど iOS の基本機能は使えます。どうしても必要なときは、問題を解かずに解除できます（記録に残ります）。") {
                Button("緊急解除") { confirmEmergency = true }
                    .font(Theme.font(16, .semibold))
                    .foregroundStyle(model.isLocked ? Theme.danger : Theme.inkFaint)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 18).padding(.vertical, 14)
                    .disabled(!model.isLocked)
            }

            Text("解くロック \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "")")
                .font(Theme.font(12)).foregroundStyle(Theme.inkFaint)
                .frame(maxWidth: .infinity)
        }
        .alert("緊急解除しますか？", isPresented: $confirmEmergency) {
            Button("緊急解除する", role: .destructive) { model.emergencyUnlock() }
            Button("緊急解除しない", role: .cancel) {}
        } message: {
            Text("問題を解かずにすべての制限を外します。記録には「緊急解除」として残ります。")
        }
        .sheet(isPresented: $showGuide) { OnboardingView(replay: true) }
    }

    private func diagRow(_ title: String, key: String) -> some View {
        HStack {
            Text(title).font(Theme.font(15)).foregroundStyle(Theme.inkSoft)
            Spacer()
            Text(SharedStore.diagDate(key).map { $0.formatted(date: .abbreviated, time: .standard) } ?? "まだ動いていません")
                .font(Theme.font(14, .semibold)).foregroundStyle(SharedStore.diagDate(key) == nil ? Theme.danger : Theme.ink)
        }
        .padding(.horizontal, 18).padding(.vertical, 12)
    }

    private var authLabel: String {
        switch model.authorization {
        case .approved: "許可済み"
        case .denied: "拒否されています"
        default: "未設定"
        }
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

    private func toggleRow(_ title: String, isOn: Bool, set: @escaping (Bool) -> Void) -> some View {
        Toggle(isOn: Binding(get: { isOn }, set: set)) {
            Text(title).font(Theme.font(16)).foregroundStyle(Theme.ink)
        }
        .tint(Theme.tealDeep)
        .padding(.horizontal, 18).padding(.vertical, 10)
    }
}
