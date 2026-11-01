import SwiftUI

struct StatsView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        let total = model.totals
        let accuracy = total.attempts == 0 ? 0 : Int((Double(total.correct) / Double(total.attempts) * 100).rounded())

        ClayScreen(title: "記録", subtitle: "どれだけ“考える時間”に変えられたか") {
            LazyVGrid(columns: [GridItem(.flexible(), spacing: 14), GridItem(.flexible(), spacing: 14)], spacing: 14) {
                BigStat(value: "\(total.triggers)", unit: "回", label: "制限の発動", color: Clay.peach)
                BigStat(value: "\(total.correct)", unit: "問", label: "累計正解", color: Clay.mint)
                BigStat(value: "\(accuracy)", unit: "%", label: "正答率", color: Clay.sky)
                BigStat(value: "\(model.dayStreak)", unit: "日", label: "連続正解日数", color: Clay.butter)
                BigStat(value: "\(model.currentStreak)", unit: "問", label: "いまの連続正解", color: Clay.lavender)
                BigStat(value: "\(model.bestStreak)", unit: "問", label: "最高連続正解", color: Clay.surface)
            }

            weekChart

            VStack(alignment: .leading, spacing: 8) {
                row("問題で解除した回数", "\(total.unlocks) 回")
                row("緊急解除した回数", "\(total.emergencyUnlocks) 回")
                row("回答した回数", "\(total.attempts) 回")
            }
            .padding(20)
            .clay()
        }
    }

    private var weekChart: some View {
        let week = model.lastWeek
        let maxValue = max(1, week.map { max($0.stats.triggers, $0.stats.correct) }.max() ?? 1)
        return VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text("この7日間").font(Clay.font(16, .bold)).foregroundStyle(Clay.ink)
                Spacer()
                legend("発動", Clay.peach)
                legend("正解", Clay.mint)
            }
            HStack(alignment: .bottom, spacing: 8) {
                ForEach(Array(week.enumerated()), id: \.offset) { _, day in
                    VStack(spacing: 6) {
                        HStack(alignment: .bottom, spacing: 3) {
                            bar(day.stats.triggers, maxValue, Clay.peach)
                            bar(day.stats.correct, maxValue, Clay.mint)
                        }
                        .frame(height: 120, alignment: .bottom)
                        Text(day.label).font(Clay.font(12, .semibold)).foregroundStyle(Clay.inkSoft)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
            .padding(14)
            .clayWell(radius: 22)
        }
        .padding(20)
        .clay()
    }

    private func bar(_ v: Int, _ maxValue: Int, _ color: Color) -> some View {
        RoundedRectangle(cornerRadius: 6, style: .continuous)
            .fill(color)
            .frame(width: 10, height: max(6, CGFloat(v) / CGFloat(maxValue) * 120))
            .shadow(color: Clay.shadow.opacity(0.5), radius: 2, x: 1, y: 2)
    }

    private func legend(_ text: String, _ color: Color) -> some View {
        HStack(spacing: 4) {
            Circle().fill(color).frame(width: 9, height: 9)
            Text(text).font(Clay.font(12)).foregroundStyle(Clay.inkSoft)
        }
    }

    private func row(_ title: String, _ value: String) -> some View {
        HStack {
            Text(title).font(Clay.font(15)).foregroundStyle(Clay.inkSoft)
            Spacer()
            Text(value).font(Clay.font(15, .semibold)).foregroundStyle(Clay.ink)
        }
        .padding(.vertical, 4)
    }
}

struct BigStat: View {
    var value: String
    var unit: String
    var label: String
    var color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline, spacing: 2) {
                Text(value).font(Clay.font(32, .bold)).foregroundStyle(Clay.ink)
                Text(unit).font(Clay.font(14, .semibold)).foregroundStyle(Clay.ink.opacity(0.6))
            }
            Text(label).font(Clay.font(13, .semibold)).foregroundStyle(Clay.ink.opacity(0.65))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(18)
        .clay(color, radius: 24, depth: 10)
    }
}
