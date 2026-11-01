import SwiftUI
import FamilyControls

struct HomeView: View {
    @Environment(AppModel.self) private var model
    @State private var editing: GuardRule?

    var body: some View {
        ClayScreen(title: "mathscreen", subtitle: "スマホを使いすぎる時間を、考える時間に。") {
            if model.isLocked { lockedCard }
            todayCard
            rulesSection
        }
        .sheet(item: $editing) { rule in
            RuleEditorView(rule: rule, isNew: !model.rules.contains { $0.id == rule.id })
        }
    }

    private var lockedCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 10) {
                Image(systemName: "lock.fill").font(.system(size: 20, weight: .bold))
                Text("制限中").font(Clay.font(20, .bold))
            }
            .foregroundStyle(Clay.ink)
            Text(model.lockedRules.map(\.name).joined(separator: "・") + " がロックされています。1問解いて再開しよう。")
                .font(Clay.font(15)).foregroundStyle(Clay.ink.opacity(0.8))
            Button("問題を解く") { model.showChallenge = true }
                .buttonStyle(.clay(Clay.surface))
        }
        .padding(22)
        .clay(Clay.lavender)
    }

    private var todayCard: some View {
        let t = model.today
        return VStack(alignment: .leading, spacing: 16) {
            Text("今日").font(Clay.font(15, .semibold)).foregroundStyle(Clay.inkSoft)
            HStack(spacing: 12) {
                StatBubble(value: "\(t.triggers)", label: "発動", color: Clay.peach)
                StatBubble(value: "\(t.correct)", label: "正解", color: Clay.mint)
                StatBubble(value: "\(model.currentStreak)", label: "連続正解", color: Clay.butter)
            }
        }
        .padding(20)
        .clay()
    }

    private var rulesSection: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text("見守るアプリ").font(Clay.font(20, .bold)).foregroundStyle(Clay.ink)
                Spacer()
                Button {
                    editing = GuardRule(name: "ルール\(model.rules.count + 1)", selection: FamilyActivitySelection(), thresholdMinutes: 15)
                } label: {
                    Image(systemName: "plus").font(.system(size: 17, weight: .bold)).foregroundStyle(Clay.ink)
                        .frame(width: 44, height: 44)
                        .clay(Clay.mint, radius: 22, depth: 8)
                }
                .buttonStyle(.plain)
            }

            if model.authorization != .approved {
                Text("スクリーンタイムへのアクセスが未許可です。「設定」タブから許可してください。")
                    .font(Clay.font(14)).foregroundStyle(Clay.peachDeep)
                    .padding(16).frame(maxWidth: .infinity, alignment: .leading)
                    .clayWell()
            }

            if model.rules.isEmpty {
                VStack(spacing: 10) {
                    Image(systemName: "hourglass").font(.system(size: 30)).foregroundStyle(Clay.inkFaint)
                    Text("＋ から、使いすぎたくないアプリと\n時間を決めましょう").multilineTextAlignment(.center)
                        .font(Clay.font(15)).foregroundStyle(Clay.inkSoft)
                }
                .padding(28).frame(maxWidth: .infinity)
                .clayWell(radius: 26)
            }

            ForEach(model.rules) { rule in
                RuleCard(rule: rule, locked: model.lockedRuleIDs.contains(rule.id),
                         onToggle: { model.setEnabled(rule, $0) })
                    .onTapGesture { editing = rule }
            }
        }
    }
}

struct StatBubble: View {
    var value: String
    var label: String
    var color: Color

    var body: some View {
        VStack(spacing: 4) {
            Text(value).font(Clay.font(26, .bold)).foregroundStyle(Clay.ink).contentTransition(.numericText())
            Text(label).font(Clay.font(12, .semibold)).foregroundStyle(Clay.ink.opacity(0.65))
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 16)
        .clay(color, radius: 22, depth: 8)
    }
}

struct RuleCard: View {
    var rule: GuardRule
    var locked: Bool
    var onToggle: (Bool) -> Void

    var body: some View {
        HStack(spacing: 14) {
            ZStack {
                Circle().fill(locked ? Clay.lavender : Clay.sky).frame(width: 50, height: 50)
                Image(systemName: locked ? "lock.fill" : "timer").font(.system(size: 20, weight: .semibold))
                    .foregroundStyle(Clay.ink)
            }
            .clay(locked ? Clay.lavender : Clay.sky, radius: 25, depth: 6)

            VStack(alignment: .leading, spacing: 5) {
                Text(rule.name).font(Clay.font(17, .semibold)).foregroundStyle(Clay.ink)
                HStack(spacing: 4) {
                    ForEach(Array(rule.selection.applicationTokens.prefix(4)), id: \.self) { token in
                        Label(token).labelStyle(.iconOnly).frame(width: 20, height: 20)
                    }
                    Text("\(rule.itemCount)件 ・ \(rule.thresholdMinutes)分ごと")
                        .font(Clay.font(13)).foregroundStyle(Clay.inkSoft)
                }
            }
            Spacer()
            Toggle("", isOn: Binding(get: { rule.isEnabled }, set: onToggle))
                .labelsHidden()
                .tint(Clay.mintDeep)
        }
        .padding(16)
        .clay()
        .contentShape(Rectangle())
    }
}
