import SwiftUI

/// App Store 用のスクリーンショットを、シミュレータで撮るための起動引数。
/// 例：`-screenshot home`（ほかに book / solve / stats / plan）。普段の起動では何も起きない。
/// 画面はすべて本物。見せるための見本のデータ（成績、習熟度）だけを、入れておく。
enum ScreenshotMode {
    static var scene: String? {
        let a = CommandLine.arguments
        guard let i = a.firstIndex(of: "-screenshot"), i + 1 < a.count else { return nil }
        return a[i + 1]
    }
    static var active: Bool { scene != nil }

    /// 見本の成績と習熟度を入れる。
    static func seed() {
        guard active else { return }
        let counts = [3, 7, 5, 10, 8, 4, 6]               // 月〜日（今日までのぶん）
        var daily: [String: DailyStats] = [:]
        let cal = Calendar(identifier: .gregorian)
        let today = Date()
        let wd = (cal.component(.weekday, from: today) + 5) % 7        // 月曜=0
        for k in 0...wd {
            let date = cal.date(byAdding: .day, value: -(wd - k), to: today) ?? today
            daily[SharedStore.dayKey(date)] = DailyStats(triggers: 2, unlocks: 2, correct: counts[k], attempts: counts[k] + 2, emergencyUnlocks: 0)
        }
        SharedStore.saveDaily(daily)
        SharedStore.currentStreak = 8
        // 単元の習熟度（メーター）を、いくつか進めておく
        let plan: [(String, Int, [Bool])] = [("e_calc", 3, [true, true, true]), ("e_decfrac", 3, [true, true, false]), ("m_signed", 3, [true, true, true]),
                                             ("m_linear", 3, [true, false, true]), ("m_sqrt", 2, [true, false])]
        for (unit, _, results) in plan {
            let ps = ProblemBank.all.filter { $0.unit == unit }
            for (i, r) in results.enumerated() where i < ps.count { MasteryStore.shared.record(ps[i], firstTryCorrect: r); ProblemMarkStore.shared.record(ps[i].id, r ? .perfect : .once) }
        }
    }
}

/// 問題を解く画面（スクリーンショット用）。
struct ScreenshotSolveView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("問題を解く").font(Theme.font(24, .bold)).foregroundStyle(Theme.ink).padding(.top, 12)
                if let p = ProblemBank.find("g01-1") {
                    ProblemSolverView(problem: p, onCorrect: { _ in }, continueLabel: "つぎへ", onContinue: {})
                }
            }
            .padding(.horizontal, 20)
        }
        .isoBackground()
    }
}
