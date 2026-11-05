import SwiftUI
import FamilyControls

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
        // 過去8週間ぶんの、見本の正解数（今週は今日まで）
        let pattern = [3, 7, 5, 10, 8, 4, 6, 9, 2, 10, 7, 5, 8, 6, 10, 4, 9, 7, 3, 8, 10, 5, 6]
        var daily: [String: DailyStats] = [:]
        let cal = Calendar(identifier: .gregorian)
        let today = Date()
        let wd = (cal.component(.weekday, from: today) + 5) % 7        // 月曜=0
        var n = 0
        for back in stride(from: 7 * 8 - 1, through: 0, by: -1) {
            // 今週の、まだ来ていない日は入れない
            let date = cal.date(byAdding: .day, value: -back, to: today) ?? today
            let c = pattern[n % pattern.count] - (back > 7 * 4 ? 2 : 0)
            n += 1
            guard c > 0 else { continue }
            daily[SharedStore.dayKey(date)] = DailyStats(triggers: 2, unlocks: 2, correct: c, attempts: c + 2, emergencyUnlocks: 0)
        }
        _ = wd
        SharedStore.saveDaily(daily)
        SharedStore.currentStreak = 8
        // ホームに出す、見本のルール（アプリの選択は、スクリーンタイムの許可がないと作れないので、件数だけを見本にする）
        if scene == "home" {
            let a = GuardRule(selection: FamilyActivitySelection(), thresholdMinutes: 30, questionCount: 1)
            let b = GuardRule(selection: FamilyActivitySelection(), thresholdMinutes: 60, questionCount: 2)
            SharedStore.saveRules([a, b])
            SharedStore.markLocked(a.id)
        }
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
