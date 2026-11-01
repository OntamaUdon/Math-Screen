import SwiftUI
import FamilyControls

struct SettingsView: View {
    @Environment(AppModel.self) private var model
    @State private var confirmEmergency = false

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

            VStack(alignment: .leading, spacing: 10) {
                SectionLabel("解除に必要な正解数")
                Picker("解除に必要な正解数", selection: Binding(get: { s.requiredCorrect }, set: { v in
                    var n = s; n.requiredCorrect = v; model.updateSettings(n)
                })) {
                    ForEach(1...3, id: \.self) { Text("\($0)問").tag($0) }
                }
                .pickerStyle(.segmented)
            }

            group("スクリーンタイム") {
                HStack {
                    Text("アクセス").font(Theme.font(16)).foregroundStyle(Theme.ink)
                    Spacer()
                    Text(authLabel).font(Theme.font(15, .semibold))
                        .foregroundStyle(model.authorization == .approved ? Theme.mintDeep : Theme.danger)
                }
                .padding(.horizontal, 18).padding(.vertical, 14)
                if model.authorization != .approved {
                    Divider()
                    Button("許可する") { Task { await model.requestAuthorization() } }
                        .font(Theme.font(16, .semibold)).foregroundStyle(Theme.mintDeep)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal, 18).padding(.vertical, 14)
                }
            }

            group("もしものとき", footer: "制限中でも電話・メッセージなど iOS の基本機能は使えます。どうしても必要なときは、問題を解かずに解除できます（記録に残ります）。") {
                Button("緊急解除") { confirmEmergency = true }
                    .font(Theme.font(16, .semibold))
                    .foregroundStyle(model.isLocked ? Theme.danger : Theme.inkFaint)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 18).padding(.vertical, 14)
                    .disabled(!model.isLocked)
            }

            Text("mathscreen \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "")")
                .font(Theme.font(12)).foregroundStyle(Theme.inkFaint)
                .frame(maxWidth: .infinity)
        }
        .confirmationDialog("緊急解除しますか？", isPresented: $confirmEmergency, titleVisibility: .visible) {
            Button("解除する", role: .destructive) { model.emergencyUnlock() }
        }
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
        .tint(Theme.mintDeep)
        .padding(.horizontal, 18).padding(.vertical, 10)
    }
}
