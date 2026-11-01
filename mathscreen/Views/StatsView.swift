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
        return VStack(alignment: .leading, spacing: 10) {
            Text("この7日間").font(Theme.font(15, .bold)).foregroundStyle(Theme.ink)
            IsoBarChart(values: week.map(\.stats.correct), labels: week.map(\.label), caption: "正解数（コーラルが今日）")
            Text("発動 \(week.reduce(0) { $0 + $1.stats.triggers }) 回 ・ 正解 \(week.reduce(0) { $0 + $1.stats.correct }) 問")
                .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
        }
        .card()
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
