import SwiftUI
import FamilyControls

struct RuleEditorView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State var rule: GuardRule
    var isNew: Bool
    @State private var showPicker = false
    @State private var confirmDelete = false

    private let minuteChoices = [1, 5, 10, 30, 60]
    private let questionChoices = [1, 2, 3, 4, 5]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                HStack {
                    Text(isNew ? "ルールを追加" : "ルールを編集").font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
                    Spacer()
                    Button("閉じる") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                .padding(.top, 24)

                section("制限するアプリ") {
                    Button {
                        showPicker = true
                    } label: {
                        HStack {
                            Text(rule.itemCount == 0 ? "制限するアプリを選ぶ" : "\(rule.itemCount)件を選択中")
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

                section("何分使うごとに") {
                    chips(minuteChoices, selected: rule.thresholdMinutes, label: { "\($0)分" }) { rule.thresholdMinutes = $0 }
                }

                section("何問出すか") {
                    chips(questionChoices, selected: rule.questionCount, label: { "\($0)問" }) { rule.questionCount = $0 }
                }

                section("出題する問題") {
                    VStack(alignment: .leading, spacing: 14) {
                        ForEach(Subject.allCases) { subject in
                            VStack(alignment: .leading, spacing: 8) {
                                HStack {
                                    Text(subject.label).font(Theme.font(15, .bold)).foregroundStyle(Theme.ink)
                                    Spacer()
                                    Button(allSelected(subject) ? "すべて外す" : "すべて選ぶ") { toggleAll(subject) }
                                        .font(Theme.font(13, .semibold)).foregroundStyle(Theme.tealDeep)
                                }
                                LazyVGrid(columns: [GridItem(.adaptive(minimum: 92), spacing: 8)], alignment: .leading, spacing: 8) {
                                    ForEach(subject.categories) { c in
                                        Button { toggle(c) } label: {
                                            Tag(text: c.label, isOn: rule.categories.contains(c.rawValue))
                                        }
                                        .buttonStyle(.plain)
                                    }
                                }
                            }
                        }
                        Text("出題対象：\(ProblemBank.candidates(categories: rule.categories, difficulties: model.settings.difficulties).count) 問")
                            .font(Theme.font(12)).foregroundStyle(Theme.inkSoft)
                    }
                    .card()
                }

                Text("対象のアプリを合計 \(rule.thresholdMinutes) 分使うとロックされ、\(rule.questionCount)問に正解すると再開できます。そこから、また \(rule.thresholdMinutes) 分たつとロックされます。同じ条件（時間と問題数）のルールは、自動で1つにまとめます。")
                    .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)

                Button("保存する") {
                    model.save(rule)
                    dismiss()
                }
                .buttonStyle(.primary)
                .disabled(rule.itemCount == 0 || rule.categories.isEmpty)
                .opacity(rule.itemCount == 0 || rule.categories.isEmpty ? 0.5 : 1)

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
        .familyActivityPicker(
            headerText: "制限するアプリを選んでください。カテゴリを選ぶと、その中のすべてのアプリが対象になります。",
            footerText: nil,
            isPresented: $showPicker,
            selection: $rule.selection
        )
        .confirmationDialog("このルールを削除しますか？", isPresented: $confirmDelete, titleVisibility: .visible) {
            Button("削除", role: .destructive) {
                model.delete(rule)
                dismiss()
            }
        }
    }

    private func allSelected(_ s: Subject) -> Bool { s.categories.allSatisfy { rule.categories.contains($0.rawValue) } }

    /// 教科ごとに、まとめて選ぶ・外す。ただし、全体で最低1つは選んだままにする。
    private func toggleAll(_ s: Subject) {
        let ids = Set(s.categories.map(\.rawValue))
        if allSelected(s) {
            let rest = rule.categories.subtracting(ids)
            if !rest.isEmpty { rule.categories = rest }
        } else {
            rule.categories.formUnion(ids)
        }
    }

    private func toggle(_ c: ProblemCategory) {
        if rule.categories.contains(c.rawValue) {
            if rule.categories.count > 1 { rule.categories.remove(c.rawValue) }
        } else {
            rule.categories.insert(c.rawValue)
        }
    }

    private func chips(_ values: [Int], selected: Int, label: @escaping (Int) -> String,
                       action: @escaping (Int) -> Void) -> some View {
        HStack(spacing: 8) {
            ForEach(values, id: \.self) { v in
                Button { action(v) } label: {
                    Tag(text: label(v), isOn: selected == v)
                }
                .buttonStyle(.plain)
            }
        }
    }

    private func section<C: View>(_ title: String, @ViewBuilder content: () -> C) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title)
            content()
        }
    }
}
