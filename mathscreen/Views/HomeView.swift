import SwiftUI
import FamilyControls

struct HomeView: View {
    @Environment(AppModel.self) private var model
    @State private var editing: GuardRule?

    var body: some View {
        Screen(title: "解くロック") {
            weekCard
            if model.isLocked { lockedCard }
            todayCard
            rulesSection
        }
        .sheet(item: $editing) { rule in
            RuleEditorView(rule: rule, isNew: !model.rules.contains { $0.id == rule.id })
        }
    }

    private var weekCard: some View {
        IsoBarChart(weeks: model.weeklyCorrect(weeks: 1), caption: "今週の正解数")
            .padding(.vertical, 4)
    }

    private var lockedCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("制限中", systemImage: "lock.fill")
                .font(Theme.font(17, .heavy)).foregroundStyle(.white)
            Text("制限中のアプリがあります。\(model.requiredCorrect)問解くと再開できます。")
                .font(Theme.font(14)).foregroundStyle(.white.opacity(0.9))
            Button("問題を解く") { model.showChallenge = true }
                .buttonStyle(.secondary)
        }
        .card(top: Theme.coral, side: Theme.coralDeep)
    }

    private var todayCard: some View {
        let t = model.today
        return VStack(alignment: .leading, spacing: 14) {
            SectionLabel("今日")
            HStack(spacing: 0) {
                StatCell(value: t.triggers, label: "発動")
                Divider().frame(height: 36)
                StatCell(value: t.correct, label: "正解")
                Divider().frame(height: 36)
                StatCell(value: model.currentStreak, label: "連続正解")
            }
        }
        .card()
    }

    private var rulesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("見守るアプリ").font(Theme.font(18, .bold)).foregroundStyle(Theme.ink)
                Spacer()
                Button {
                    editing = GuardRule(selection: FamilyActivitySelection(), thresholdMinutes: 10, questionCount: 1)
                } label: {
                    Label("追加", systemImage: "plus")
                        .font(Theme.font(14, .semibold))
                        .foregroundStyle(Theme.tealDeep)
                }
            }

            if model.authorization != .approved {
                Text("スクリーンタイムへのアクセスが未許可です。「設定」タブから許可してください。")
                    .font(Theme.font(14)).foregroundStyle(Theme.danger)
                    .padding(14).frame(maxWidth: .infinity, alignment: .leading)
                    .well()
            }

            if model.rules.isEmpty {
                Text("「追加」から、使いすぎたくないアプリと時間を決めましょう。")
                    .font(Theme.font(15)).foregroundStyle(Theme.inkSoft)
                    .padding(20).frame(maxWidth: .infinity, alignment: .leading)
                    .well()
            } else {
                VStack(spacing: 0) {
                    ForEach(Array(model.rules.enumerated()), id: \.element.id) { i, rule in
                        if i > 0 { Divider().padding(.leading, 16) }
                        RuleRow(rule: rule, locked: model.lockedRuleIDs.contains(rule.id),
                                onToggle: { model.setEnabled(rule, $0) })
                            .contentShape(Rectangle())
                            .onTapGesture { editing = rule }
                    }
                }
                .card(padding: 0)
            }
        }
    }
}

struct StatCell: View {
    var value: Int
    var label: String

    var body: some View {
        VStack(spacing: 2) {
            Text("\(value)").font(Theme.font(26, .bold)).foregroundStyle(Theme.ink).monospacedDigit()
            Text(label).font(Theme.font(12)).foregroundStyle(Theme.inkSoft)
        }
        .frame(maxWidth: .infinity)
    }
}

struct RuleRow: View {
    var rule: GuardRule
    var locked: Bool
    var onToggle: (Bool) -> Void

    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 6) {
                    Text(rule.title).font(Theme.font(16, .semibold)).foregroundStyle(Theme.ink)
                    if locked {
                        Image(systemName: "lock.fill").font(.system(size: 12)).foregroundStyle(Theme.tealDeep)
                    }
                }
                HStack(spacing: 4) {
                    ForEach(Array(rule.selection.applicationTokens.prefix(4)), id: \.self) { token in
                        Label(token).labelStyle(.iconOnly).frame(width: 18, height: 18)
                    }
                    Text("\(rule.itemCount)件")
                        .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                }
            }
            Spacer()
            Toggle("", isOn: Binding(get: { rule.isEnabled }, set: onToggle))
                .labelsHidden()
                .tint(Theme.tealDeep)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 14)
    }
}
