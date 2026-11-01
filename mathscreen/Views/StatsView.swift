import SwiftUI

struct StatsView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        let total = model.totals
        let accuracy = total.attempts == 0 ? 0 : Int((Double(total.correct) / Double(total.attempts) * 100).rounded())

        Screen(title: "記録") {
            VStack(spacing: 0) {
                row("制限の発動", "\(total.triggers) 回")
                Divider()
                row("累計正解", "\(total.correct) 問")
                Divider()
                row("正答率", "\(accuracy) %")
                Divider()
                row("連続正解日数", "\(model.dayStreak) 日")
                Divider()
                row("いまの連続正解", "\(model.currentStreak) 問")
                Divider()
                row("最高連続正解", "\(model.bestStreak) 問")
            }
            .card(padding: 0)

            weekChart

            VStack(spacing: 0) {
                row("問題で解除した回数", "\(total.unlocks) 回")
                Divider()
                row("緊急解除した回数", "\(total.emergencyUnlocks) 回")
            }
            .card(padding: 0)
        }
    }

    private var weekChart: some View {
        let week = model.lastWeek
        let maxValue = max(1, week.map { max($0.stats.triggers, $0.stats.correct) }.max() ?? 1)
        return VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text("この7日間").font(Theme.font(15, .semibold)).foregroundStyle(Theme.ink)
                Spacer()
                legend("発動", Theme.inkFaint)
                legend("正解", Theme.mintDeep)
            }
            HStack(alignment: .bottom, spacing: 8) {
                ForEach(Array(week.enumerated()), id: \.offset) { _, day in
                    VStack(spacing: 6) {
                        HStack(alignment: .bottom, spacing: 3) {
                            bar(day.stats.triggers, maxValue, Theme.inkFaint.opacity(0.6))
                            bar(day.stats.correct, maxValue, Theme.mintDeep)
                        }
                        .frame(height: 110, alignment: .bottom)
                        Text(day.label).font(Theme.font(12)).foregroundStyle(Theme.inkSoft)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
        }
        .card()
    }

    private func bar(_ v: Int, _ maxValue: Int, _ color: Color) -> some View {
        RoundedRectangle(cornerRadius: 3, style: .continuous)
            .fill(v == 0 ? Theme.sunken : color)
            .frame(width: 8, height: max(4, CGFloat(v) / CGFloat(maxValue) * 110))
    }

    private func legend(_ text: String, _ color: Color) -> some View {
        HStack(spacing: 4) {
            RoundedRectangle(cornerRadius: 2).fill(color).frame(width: 8, height: 8)
            Text(text).font(Theme.font(12)).foregroundStyle(Theme.inkSoft)
        }
    }

    private func row(_ title: String, _ value: String) -> some View {
        HStack {
            Text(title).font(Theme.font(15)).foregroundStyle(Theme.inkSoft)
            Spacer()
            Text(value).font(Theme.font(16, .semibold)).foregroundStyle(Theme.ink).monospacedDigit()
        }
        .padding(.horizontal, 18)
        .padding(.vertical, 14)
    }
}
