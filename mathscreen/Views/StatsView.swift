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
            if !model.isPremium { premiumCard }

            VStack(spacing: 0) {
                row("問題で解除した回数", "\(total.unlocks) 回")
                Divider()
                row("緊急解除した回数", "\(total.emergencyUnlocks) 回")
            }
            .card(padding: 0)
        }
    }

    private var weekChart: some View {
        let weeks = model.weeklyCorrect(weeks: model.isPremium ? AppModel.premiumWeeks : 1)
        return VStack(alignment: .leading, spacing: 10) {
            Text(model.isPremium ? "過去の成績" : "今週の成績").font(Theme.font(15, .bold)).foregroundStyle(Theme.ink)
            IsoBarChart(weeks: weeks, caption: model.isPremium ? "正解数（手前が今週、奥が過去。10問ごとに色が変わる）" : "正解数（25問で金色、50問で紫）")
        }
        .card()
    }

    /// 無料のとき：過去の成績は Premium、という案内。
    private var premiumCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("過去の成績を見る", systemImage: "lock.fill")
                .font(Theme.font(16, .bold)).foregroundStyle(Theme.ink)
            Text("Premium にすると、過去の週も、グラフの奥（右上）に並べて見られます。初回7日間無料、そのあと月300円／年2,000円の予定です。")
                .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                .fixedSize(horizontal: false, vertical: true)
            Button("仮登録する（0円）") { model.setPremium(true) }
                .buttonStyle(.primary)
            Text("課金の仕組みができるまでの、仮の登録です。お金はかかりません。")
                .font(Theme.font(12)).foregroundStyle(Theme.inkFaint)
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
