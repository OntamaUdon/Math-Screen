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
        ZStack {
            ClayBackdrop()
            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    HStack {
                        Text(isNew ? "ルールを追加" : "ルールを編集").font(Clay.font(24, .bold)).foregroundStyle(Clay.ink)
                        Spacer()
                        Button("閉じる") { dismiss() }.font(Clay.font(15, .semibold)).foregroundStyle(Clay.inkSoft)
                    }
                    .padding(.top, 24)

                    section("名前") {
                        TextField("例：SNS", text: $rule.name)
                            .font(Clay.font(18, .medium))
                            .padding(.horizontal, 18).frame(height: 56)
                            .clayWell()
                    }

                    section("対象のアプリ") {
                        Button {
                            showPicker = true
                        } label: {
                            HStack {
                                Image(systemName: "square.grid.2x2.fill")
                                Text(rule.itemCount == 0 ? "アプリを選ぶ" : "\(rule.itemCount)件を選択中（変更する）")
                                Spacer()
                                Image(systemName: "chevron.right").font(.system(size: 14, weight: .bold))
                            }
                        }
                        .buttonStyle(.clay(Clay.sky))
                        if !rule.selection.applicationTokens.isEmpty {
                            ScrollView(.horizontal) {
                                HStack(spacing: 10) {
                                    ForEach(Array(rule.selection.applicationTokens), id: \.self) { token in
                                        Label(token).labelStyle(.iconOnly).frame(width: 34, height: 34)
                                    }
                                }
                                .padding(.vertical, 6)
                            }
                            .scrollIndicators(.hidden)
                        }
                    }

                    section("問題を出すまでの時間") {
                        VStack(spacing: 16) {
                            HStack(alignment: .firstTextBaseline, spacing: 4) {
                                Text("\(rule.thresholdMinutes)").font(Clay.font(44, .bold)).foregroundStyle(Clay.ink)
                                    .contentTransition(.numericText())
                                Text("分").font(Clay.font(18, .semibold)).foregroundStyle(Clay.inkSoft)
                                Spacer()
                                Stepper("", value: $rule.thresholdMinutes, in: 1...240, step: 1).labelsHidden()
                            }
                            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 10), count: 4), spacing: 10) {
                                ForEach(presets, id: \.self) { m in
                                    Button { withAnimation { rule.thresholdMinutes = m } } label: {
                                        ClayChip(text: "\(m)分", color: Clay.butter, isOn: rule.thresholdMinutes == m)
                                            .frame(maxWidth: .infinity)
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                            Text("対象アプリを合計 \(rule.thresholdMinutes) 分使うとロックされます。正解するとカウントがリセットされ、次の \(rule.thresholdMinutes) 分で再びロックされます。")
                                .font(Clay.font(13)).foregroundStyle(Clay.inkSoft)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(18)
                        .clay()
                    }

                    Button("保存する") {
                        model.save(rule)
                        dismiss()
                    }
                    .buttonStyle(.clay(Clay.lavender))
                    .disabled(rule.itemCount == 0 || rule.name.trimmingCharacters(in: .whitespaces).isEmpty)
                    .opacity(rule.itemCount == 0 ? 0.55 : 1)

                    if !isNew {
                        Button("このルールを削除") { confirmDelete = true }
                            .font(Clay.font(15, .semibold)).foregroundStyle(Clay.peachDeep)
                            .frame(maxWidth: .infinity)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 40)
            }
        }
        .familyActivityPicker(isPresented: $showPicker, selection: $rule.selection)
        .confirmationDialog("このルールを削除しますか？", isPresented: $confirmDelete, titleVisibility: .visible) {
            Button("削除", role: .destructive) {
                model.delete(rule)
                dismiss()
            }
        }
    }

    private func section<C: View>(_ title: String, @ViewBuilder content: () -> C) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title).font(Clay.font(14, .semibold)).foregroundStyle(Clay.inkSoft)
            content()
        }
    }
}
