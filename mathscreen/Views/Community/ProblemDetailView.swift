import SwiftUI

/// 問題を解く。みんなの問題なら、通報・ブロック・削除もここから。
struct ProblemDetailView: View {
    let item: FeedItem
    let isMine: Bool
    var onChanged: () -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var message: String?
    @State private var stats: (shown: Int, correct: Int)?
    @State private var myID: String?
    @State private var blockTarget: String?
    @State private var confirmDelete = false

    private let reasons = ["不適切な内容", "答えがまちがっている", "その他"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                header
                statsLine
                ProblemSolverView(problem: item.problem, onCorrect: { _ in }, continueLabel: "とじる", onContinue: { dismiss() })
                    .id(item.id)

                if let message {
                    Text(message).font(Theme.font(13)).foregroundStyle(Theme.tealDeep)
                }
            }
            .padding(.horizontal, 20).padding(.bottom, 40)
        }
        .isoBackground()
        .task {
            stats = await Community.shared.stats(for: item.problem.id)
            myID = try? await Community.shared.userID()
        }
        .confirmationDialog("この人の投稿とコメントを、今後表示しませんか？", isPresented: Binding(
            get: { blockTarget != nil }, set: { if !$0 { blockTarget = nil } }), titleVisibility: .visible) {
            Button("ブロックする", role: .destructive) {
                if let a = blockTarget { run { try await Community.shared.block(a); onChanged() } }
            }
        }
        .confirmationDialog("この投稿を削除しますか？", isPresented: $confirmDelete, titleVisibility: .visible) {
            Button("削除", role: .destructive) {
                if let r = item.row { run { try await Community.shared.deletePost(r.id); onChanged(); dismiss() } }
            }
        }
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
            if let r = item.row {
                Menu {
                    if isMine || r.author == myID {
                        Button("この投稿を削除", role: .destructive) { confirmDelete = true }
                    } else {
                        Menu("通報する") {
                            ForEach(reasons, id: \.self) { reason in
                                Button(reason) { run { try await Community.shared.report(r.id, reason: reason); message = "通報しました。ありがとうございます。" } }
                            }
                        }
                        Button("この人をブロック", role: .destructive) { blockTarget = r.author }
                    }
                } label: {
                    Image(systemName: "ellipsis.circle").font(.system(size: 22)).foregroundStyle(Theme.inkSoft)
                }
            }
            Button("閉じる") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
        }
        .padding(.top, 24)
    }

    private func run(_ work: @escaping () async throws -> Void) {
        Task {
            do { try await work() } catch { message = error.localizedDescription }
        }
    }
}
