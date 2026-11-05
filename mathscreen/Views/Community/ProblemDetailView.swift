import SwiftUI

/// 問題を解く。
struct ProblemDetailView: View {
    let item: FeedItem

    @Environment(\.dismiss) private var dismiss
    @State private var stats: (shown: Int, correct: Int)?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                header
                statsLine
                ProblemSolverView(problem: item.problem, onCorrect: { _ in }, continueLabel: "とじる", onContinue: { dismiss() })
                    .id(item.id)
            }
            .padding(.horizontal, 20).padding(.bottom, 40)
        }
        .isoBackground()
        .task { stats = await Community.shared.stats(for: item.problem.id) }
    }

    /// みんなの正答率（1回目の解答だけを数える）。人数が少ないうちは出さない。
    @ViewBuilder private var statsLine: some View {
        if let s = stats, s.shown >= 5 {
            Text("みんなの正答率 \(Int((Double(s.correct) / Double(s.shown) * 100).rounded()))%（\(s.shown)人が挑戦）")
                .font(Theme.font(13, .semibold)).foregroundStyle(Theme.inkSoft)
        } else {
            Text("みんなの正答率：集計中").font(Theme.font(13)).foregroundStyle(Theme.inkFaint)
        }
    }

    private var header: some View {
        HStack {
            Text(item.problem.title).font(Theme.font(20, .bold)).foregroundStyle(Theme.ink)
            Spacer()
            Button("閉じる") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
        }
        .padding(.top, 24)
    }
}
