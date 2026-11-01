import SwiftUI
import FamilyControls

struct SettingsView: View {
    @Environment(AppModel.self) private var model
    @State private var confirmEmergency = false

    var body: some View {
        let s = model.settings
        ClayScreen(title: "設定") {
            card("出題する分野") {
                ForEach(ProblemCategory.allCases) { c in
                    toggleRow(c.label, color: c.color, isOn: s.categories.contains(c.rawValue)) { on in
                        var n = s
                        if on { n.categories.insert(c.rawValue) } else if n.categories.count > 1 { n.categories.remove(c.rawValue) }
                        model.updateSettings(n)
                    }
                }
            }

            card("難易度") {
                ForEach(Difficulty.allCases) { d in
                    toggleRow("\(d.label)  \(d.dots)", color: Clay.butter, isOn: s.difficulties.contains(d.rawValue)) { on in
                        var n = s
                        if on { n.difficulties.insert(d.rawValue) } else if n.difficulties.count > 1 { n.difficulties.remove(d.rawValue) }
                        model.updateSettings(n)
                    }
                }
                Text("出題対象：\(ProblemBank.candidates(categories: s.categories, difficulties: s.difficulties).count) 問")
                    .font(Clay.font(13)).foregroundStyle(Clay.inkSoft)
            }

            card("解除に必要な正解数") {
                HStack(spacing: 12) {
                    ForEach(1...3, id: \.self) { n in
                        Button {
                            var ns = s; ns.requiredCorrect = n; model.updateSettings(ns)
                        } label: {
                            ClayChip(text: "\(n)問", color: Clay.lavender, isOn: s.requiredCorrect == n)
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }

            card("スクリーンタイム") {
                HStack {
                    Text("アクセス").font(Clay.font(16)).foregroundStyle(Clay.ink)
                    Spacer()
                    Text(authLabel).font(Clay.font(15, .semibold))
                        .foregroundStyle(model.authorization == .approved ? Clay.mintDeep : Clay.peachDeep)
                }
                if model.authorization != .approved {
                    Button("許可する") { Task { await model.requestAuthorization() } }
                        .buttonStyle(.clay(Clay.sky))
                }
            }

            card("もしものとき") {
                Text("制限中でも電話・メッセージなど iOS の基本機能は使えます。どうしても必要なときは、問題を解かずに解除できます（記録に残ります）。")
                    .font(Clay.font(13)).foregroundStyle(Clay.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
                Button("緊急解除") { confirmEmergency = true }
                    .buttonStyle(.clay(Clay.peach))
                    .disabled(!model.isLocked)
                    .opacity(model.isLocked ? 1 : 0.5)
            }

            Text("mathscreen \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "")")
                .font(Clay.font(12)).foregroundStyle(Clay.inkFaint)
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

    private func card<C: View>(_ title: String, @ViewBuilder content: () -> C) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(title).font(Clay.font(16, .bold)).foregroundStyle(Clay.ink)
            content()
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .clay()
    }

    private func toggleRow(_ title: String, color: Color, isOn: Bool, set: @escaping (Bool) -> Void) -> some View {
        HStack(spacing: 12) {
            Circle().fill(color).frame(width: 14, height: 14)
            Text(title).font(Clay.font(16)).foregroundStyle(Clay.ink)
            Spacer()
            Toggle("", isOn: Binding(get: { isOn }, set: set)).labelsHidden().tint(Clay.mintDeep)
        }
    }
}
