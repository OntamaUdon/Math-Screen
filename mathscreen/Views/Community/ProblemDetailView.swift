import SwiftUI

/// 問題を解く + コメントを読む・書く。
struct ProblemDetailView: View {
    let item: FeedItem
    let isMine: Bool
    var onChanged: () -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var comments: [CommentRow] = []
    @State private var text = ""
    @State private var sending = false
    @State private var message: String?
    @State private var myID: String?
    @State private var blockTarget: String?
    @State private var confirmDelete = false

    private let reasons = ["不適切な内容", "答えがまちがっている", "その他"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                header
                ProblemSolverView(problem: item.problem, onCorrect: { _ in }, continueLabel: "とじる", onContinue: { dismiss() })
                    .id(item.id)

                if let message {
                    Text(message).font(Theme.font(13)).foregroundStyle(Theme.tealDeep)
                }
                commentsSection
            }
            .padding(.horizontal, 20).padding(.bottom, 40)
        }
        .scrollDismissesKeyboard(.interactively)
        .isoBackground()
        .task {
            myID = try? await Community.shared.userID()
            await loadComments()
        }
        .confirmationDialog("この人の投稿とコメントを、今後表示しませんか？", isPresented: Binding(
            get: { blockTarget != nil }, set: { if !$0 { blockTarget = nil } }), titleVisibility: .visible) {
            Button("ブロックする", role: .destructive) {
                if let a = blockTarget { run { try await Community.shared.block(a); onChanged(); await loadComments() } }
            }
        }
        .confirmationDialog("この投稿を削除しますか？", isPresented: $confirmDelete, titleVisibility: .visible) {
            Button("削除", role: .destructive) {
                if let r = item.row { run { try await Community.shared.deletePost(r.id); onChanged(); dismiss() } }
            }
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

    // MARK: コメント
    private var commentsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("コメント（\(comments.count)）").font(Theme.font(16, .bold)).foregroundStyle(Theme.ink)

            HStack(alignment: .bottom, spacing: 8) {
                TextField("コメントを書く（300字まで）", text: $text, axis: .vertical)
                    .font(Theme.font(15)).lineLimit(1...4)
                    .padding(12).well()
                Button { Task { await send() } } label: {
                    Image(systemName: "paperplane.fill").font(.system(size: 18)).foregroundStyle(.white)
                        .frame(width: 46, height: 46)
                        .background(Slab(top: canSend ? Theme.teal : Theme.inkFaint, side: canSend ? Theme.tealDeep : Theme.sunkenSide, depth: 3, radius: 10))
                }
                .disabled(!canSend)
                .padding(.trailing, 3).padding(.bottom, 3)
            }

            if comments.isEmpty {
                Text("まだコメントはありません。").font(Theme.font(14)).foregroundStyle(Theme.inkSoft)
            } else {
                VStack(spacing: 0) {
                    ForEach(Array(comments.enumerated()), id: \.element.id) { i, c in
                        if i > 0 { Divider().padding(.leading, 16) }
                        commentRow(c)
                    }
                }
                .card(padding: 0)
            }
        }
    }

    private func commentRow(_ c: CommentRow) -> some View {
        let mine = c.author == myID
        return VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(mine ? "あなた" : "匿名").font(Theme.font(12, .bold)).foregroundStyle(mine ? Theme.tealDeep : Theme.inkSoft)
                Text(c.dateText).font(Theme.font(11)).foregroundStyle(Theme.inkFaint)
                Spacer()
                Menu {
                    if mine {
                        Button("削除", role: .destructive) { run { try await Community.shared.deleteComment(c.id); await loadComments() } }
                    } else {
                        Menu("通報する") {
                            ForEach(reasons, id: \.self) { reason in
                                Button(reason) { run { try await Community.shared.reportComment(c.id, reason: reason); message = "通報しました。ありがとうございます。" } }
                            }
                        }
                        Button("この人をブロック", role: .destructive) { blockTarget = c.author }
                    }
                } label: {
                    Image(systemName: "ellipsis").font(.system(size: 15)).foregroundStyle(Theme.inkFaint).padding(6)
                }
            }
            Text(c.body).font(Theme.font(15)).foregroundStyle(Theme.ink).fixedSize(horizontal: false, vertical: true)
        }
        .padding(.horizontal, 16).padding(.vertical, 12)
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var canSend: Bool {
        let t = text.trimmingCharacters(in: .whitespacesAndNewlines)
        return !t.isEmpty && t.count <= 300 && !sending
    }

    private func send() async {
        sending = true
        defer { sending = false }
        do {
            try await Community.shared.postComment(key: item.problem.id, body: text.trimmingCharacters(in: .whitespacesAndNewlines))
            text = ""
            message = nil
            await loadComments()
        } catch { message = error.localizedDescription }
    }

    private func loadComments() async {
        do { comments = try await Community.shared.comments(for: item.problem.id) }
        catch { message = error.localizedDescription }
    }

    private func run(_ work: @escaping () async throws -> Void) {
        Task {
            do { try await work() } catch { message = error.localizedDescription }
        }
    }
}
