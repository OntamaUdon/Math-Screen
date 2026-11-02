import SwiftUI
import FamilyControls

struct RuleEditorView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State var rule: GuardRule
    var isNew: Bool
    @State private var showPicker = false
    @State private var confirmDelete = false
    @State private var pickUnits = false

    private let questionChoices = [1, 2, 3, 4, 5]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                HStack {
                    Text(isNew ? "ルールを追加" : "ルールを編集").font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
                    Spacer()
                    Button("保存") {
                        model.save(rule)
                        dismiss()
                    }
                    .font(Theme.font(16, .bold)).foregroundStyle(canSave ? Theme.tealDeep : Theme.inkFaint)
                    .disabled(!canSave)
                }
                .padding(.top, 24)

                section("制限するアプリ") {
                    Button {
                        showPicker = true
                    } label: {
                        HStack(spacing: 10) {
                            Image(systemName: rule.itemCount == 0 ? "plus.app.fill" : "checkmark.app.fill")
                                .font(.system(size: 26))
                            VStack(alignment: .leading, spacing: 2) {
                                Text(rule.itemCount == 0 ? "制限するアプリを選ぶ" : "\(rule.itemCount)件を選択中")
                                    .font(Theme.font(20, .heavy))
                                if rule.itemCount > 0 { Text("タップして変更").font(Theme.font(12, .semibold)).opacity(0.85) }
                            }
                            Spacer()
                            Image(systemName: "chevron.right").font(.system(size: 15, weight: .bold))
                        }
                        .padding(.horizontal, 16).padding(.vertical, 8)
                    }
                    .buttonStyle(IsoButtonStyle(kind: rule.itemCount == 0 ? .alert : .primary))
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

                section("どれだけ使うごとに") {
                    VStack(spacing: 6) {
                        HStack(spacing: 0) {
                            Picker("時間", selection: hoursBinding) {
                                ForEach(0...12, id: \.self) { Text("\($0)時間").tag($0) }
                            }
                            .pickerStyle(.wheel)
                            Picker("分", selection: minutesBinding) {
                                ForEach(0..<60, id: \.self) { Text("\($0)分").tag($0) }
                            }
                            .pickerStyle(.wheel)
                            .disabled(rule.thresholdMinutes >= GuardRule.maxMinutes)
                        }
                        .frame(height: 140)
                        .clipped()
                    }
                    .card(padding: 10)
                }

                section("何問出すか") {
                    chips(questionChoices, selected: rule.questionCount, label: { "\($0)問" }) { rule.questionCount = $0 }
                }

                section("出題する教科") {
                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 72), spacing: 8)], alignment: .leading, spacing: 8) {
                        ForEach(Subject.allCases) { s in
                            Button { toggleSubject(s) } label: { Tag(text: s.label, isOn: subjectOn(s)) }
                                .buttonStyle(.plain)
                        }
                    }
                }

                section("出題のしかた") {
                    VStack(alignment: .leading, spacing: 12) {
                        modeCard("おまかせ", detail: "できていない単元を優先して出します。できてきたら、むずかしい問題や次の単元へ進みます。",
                                 icon: "wand.and.stars", isOn: !pickUnits) {
                            pickUnits = false
                            rule.units = []
                        }
                        modeCard("単元を選ぶ", detail: "出したい単元にチェックを入れると、その単元だけが出ます。",
                                 icon: "checklist", isOn: pickUnits) { pickUnits = true }
                        if pickUnits {
                            Text(rule.units.isEmpty ? "出したい単元をタップしてチェックしてください。" : "チェックした単元：\(rule.units.count) 件")
                                .font(Theme.font(13, .semibold))
                                .foregroundStyle(rule.units.isEmpty ? Theme.danger : Theme.tealDeep)
                            UnitListView(subjects: Subject.allCases.filter { subjectOn($0) }, selection: $rule.units)
                        }
                    }
                }

                Text("対象のアプリを合計 \(GuardRule.durationText(rule.thresholdMinutes)) 使うとロックされ、\(rule.questionCount)問に正解すると再開できます。そこから、また \(GuardRule.durationText(rule.thresholdMinutes)) たつとロックされます。同じ条件（時間と問題数）のルールは、自動で1つにまとめます。")
                    .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)

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
        .onAppear { pickUnits = !rule.units.isEmpty }
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

    /// ダイアルの「時間」。変えたあと、全体が1分〜12時間に収まるようにする。
    private var hoursBinding: Binding<Int> {
        Binding(get: { rule.thresholdMinutes / 60 },
                set: { setTotal($0 * 60 + rule.thresholdMinutes % 60) })
    }
    private var minutesBinding: Binding<Int> {
        Binding(get: { rule.thresholdMinutes % 60 },
                set: { setTotal(rule.thresholdMinutes / 60 * 60 + $0) })
    }
    private func setTotal(_ total: Int) { rule.thresholdMinutes = min(max(total, 1), GuardRule.maxMinutes) }

    private var canSave: Bool { rule.itemCount > 0 && !rule.categories.isEmpty && (!pickUnits || !rule.units.isEmpty) }

    private func subjectOn(_ s: Subject) -> Bool { s.categories.contains { rule.categories.contains($0.rawValue) } }

    /// 教科を足す・外す。ただし、最低1つの教科は残す。外した教科の単元のチェックも外す。
    private func toggleSubject(_ s: Subject) {
        let ids = Set(s.categories.map(\.rawValue))
        if subjectOn(s) {
            let rest = rule.categories.subtracting(ids)
            guard !rest.isEmpty else { return }
            rule.categories = rest
            let unitIDs = Set(UnitCatalog.all.filter { $0.subject == s.rawValue }.map(\.id))
            rule.units.subtract(unitIDs)
        } else {
            rule.categories.formUnion(ids)
        }
    }

    /// 「おまかせ」「単元を選ぶ」の選択肢。選ばれている方は色がつき、チェックが入る。
    private func modeCard(_ title: String, detail: String, icon: String, isOn: Bool, _ action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: icon).font(.system(size: 22)).foregroundStyle(isOn ? Theme.tealDeep : Theme.inkFaint)
                    .frame(width: 28)
                VStack(alignment: .leading, spacing: 4) {
                    Text(title).font(Theme.font(16, .bold)).foregroundStyle(Theme.ink)
                    Text(detail).font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 4)
                Image(systemName: isOn ? "checkmark.circle.fill" : "circle")
                    .font(.system(size: 24)).foregroundStyle(isOn ? Theme.tealDeep : Theme.inkFaint)
            }
            .card(padding: 14, top: isOn ? Color(hex: 0xE3F6F3) : Theme.surface, side: isOn ? Theme.tealDeep : Theme.surfaceSide, depth: isOn ? 4 : 6)
        }
        .buttonStyle(.plain)
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
