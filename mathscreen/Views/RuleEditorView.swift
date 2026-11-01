import SwiftUI
import FamilyControls

struct RuleEditorView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State var rule: GuardRule
    var isNew: Bool
    @State private var showPicker = false
    @State private var confirmDelete = false

    private let presets = [5, 10, 15, 20, 30, 45, 60, 90]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                HStack {
                    Text(isNew ? "ルールを追加" : "ルールを編集").font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
                    Spacer()
                    Button("閉じる") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                .padding(.top, 24)

                section("名前") {
                    TextField("例：SNS", text: $rule.name)
                        .font(Theme.font(17))
                        .padding(.horizontal, 16).frame(height: 52)
                        .well()
                }

                section("対象のアプリ") {
                    Button {
                        showPicker = true
                    } label: {
                        HStack {
                            Text(rule.itemCount == 0 ? "アプリを選ぶ" : "\(rule.itemCount)件を選択中")
                            Spacer()
                            Image(systemName: "chevron.right").font(.system(size: 13, weight: .semibold)).foregroundStyle(Theme.inkFaint)
                        }
                        .padding(.horizontal, 16)
                    }
                    .buttonStyle(.secondary)
                    if !rule.selection.applicationTokens.isEmpty {
                        ScrollView(.horizontal) {
                            HStack(spacing: 10) {
                                ForEach(Array(rule.selection.applicationTokens), id: \.self) { token in
                                    Label(token).labelStyle(.iconOnly).frame(width: 32, height: 32)
                                }
                            }
                        }
                        .scrollIndicators(.hidden)
                    }
                }

                section("問題を出すまでの時間") {
                    VStack(alignment: .leading, spacing: 14) {
                        HStack(alignment: .firstTextBaseline, spacing: 4) {
                            Text("\(rule.thresholdMinutes)").font(Theme.font(40, .bold)).foregroundStyle(Theme.ink).monospacedDigit()
                            Text("分").font(Theme.font(17, .semibold)).foregroundStyle(Theme.inkSoft)
                            Spacer()
                            Stepper("", value: $rule.thresholdMinutes, in: 1...240).labelsHidden()
                        }
                        LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 8), count: 4), spacing: 8) {
                            ForEach(presets, id: \.self) { m in
                                Button { rule.thresholdMinutes = m } label: {
                                    Tag(text: "\(m)分", isOn: rule.thresholdMinutes == m).frame(maxWidth: .infinity)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                        Text("対象アプリを合計 \(rule.thresholdMinutes) 分使うとロックされます。正解するとカウントがリセットされ、次の \(rule.thresholdMinutes) 分で再びロックされます。")
                            .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .card()
                }

                Button("保存する") {
                    model.save(rule)
                    dismiss()
                }
                .buttonStyle(.primary)
                .disabled(!canSave)
                .opacity(canSave ? 1 : 0.5)

                if !isNew {
                    Button("このルールを削除") { confirmDelete = true }
                        .font(Theme.font(15, .semibold)).foregroundStyle(Theme.danger)
                        .frame(maxWidth: .infinity)
                }
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 40)
        }
        .isoBackground()
        .familyActivityPicker(isPresented: $showPicker, selection: $rule.selection)
        .confirmationDialog("このルールを削除しますか？", isPresented: $confirmDelete, titleVisibility: .visible) {
            Button("削除", role: .destructive) {
                model.delete(rule)
                dismiss()
            }
        }
    }

    private var canSave: Bool {
        rule.itemCount > 0 && !rule.name.trimmingCharacters(in: .whitespaces).isEmpty
    }

    private func section<C: View>(_ title: String, @ViewBuilder content: () -> C) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title)
            content()
        }
    }
}
