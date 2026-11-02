import SwiftUI

/// みんなの問題：公開済みの問題を解く／自分の投稿を見る。
struct CommunityView: View {
    @Environment(AppModel.self) private var model
    @State private var showMine = false
    @State private var rows: [CommunityRow] = []
    @State private var loading = false
    @State private var error: String?
    @State private var selected: CommunityRow?
    @State private var showPost = false
    @State private var showPremiumAlert = false

    var body: some View {
        Screen(title: "みんなの問題", subtitle: "ほかの人が作った問題に挑戦。Premium なら、自分でも投稿できます。") {
            HStack(spacing: 8) {
                Button { showMine = false } label: { Tag(text: "みんなの問題", isOn: !showMine) }.buttonStyle(.plain)
                Button { showMine = true } label: { Tag(text: "自分の投稿", isOn: showMine) }.buttonStyle(.plain)
            }
            Button {
                if model.isPremium { showPost = true } else { showPremiumAlert = true }
            } label: { Label("問題を投稿する", systemImage: "plus") }
                .buttonStyle(.primary)

            if let error {
                Text(error).font(Theme.font(14)).foregroundStyle(Theme.danger)
                    .padding(14).frame(maxWidth: .infinity, alignment: .leading).well()
            }
            if loading && rows.isEmpty {
                ProgressView().frame(maxWidth: .infinity).padding(20)
            } else if rows.isEmpty && error == nil {
                Text(showMine ? "まだ投稿がありません。" : "公開されている問題は、まだありません。")
                    .font(Theme.font(15)).foregroundStyle(Theme.inkSoft)
                    .padding(20).frame(maxWidth: .infinity, alignment: .leading).well()
            } else {
                VStack(spacing: 0) {
                    ForEach(Array(rows.enumerated()), id: \.element.id) { i, r in
                        if i > 0 { Divider().padding(.leading, 16) }
                        row(r).contentShape(Rectangle()).onTapGesture { selected = r }
                    }
                }
                .card(padding: 0)
            }
        }
        .task(id: showMine) { await load() }
        .refreshable { await load() }
        .sheet(item: $selected) { r in
            CommunityDetailView(row: r, isMine: showMine) { Task { await load() } }
        }
        .sheet(isPresented: $showPost, onDismiss: { Task { await load() } }) { PostProblemView() }
        .alert("Premium の機能です", isPresented: $showPremiumAlert) {
            Button("仮登録する（0円）") { model.setPremium(true) }
            Button("やめる", role: .cancel) {}
        } message: {
            Text("問題の投稿は Premium で使えます。いまは、お金のかからない仮登録ができます。")
        }
    }

    private func row(_ r: CommunityRow) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(r.title).font(Theme.font(16, .semibold)).foregroundStyle(Theme.ink)
                Spacer()
                if showMine {
                    Text(r.statusLabel).font(Theme.font(12, .bold))
                        .foregroundStyle(r.status == "approved" ? Theme.tealDeep : (r.status == "pending" ? Theme.inkSoft : Theme.danger))
                }
            }
            Text("\(ProblemCategory(rawValue: r.genre)?.label ?? r.genre) ・ \(Difficulty(rawValue: r.difficulty)?.label ?? "")")
                .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
            if showMine, r.status == "rejected", let note = r.reviewNote, !note.isEmpty {
                Text("理由：\(note)").font(Theme.font(12)).foregroundStyle(Theme.danger)
            }
        }
        .padding(.horizontal, 16).padding(.vertical, 14)
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func load() async {
        loading = true; error = nil
        defer { loading = false }
        do { rows = showMine ? try await Community.shared.mine() : try await Community.shared.approved() }
        catch { rows = []; self.error = error.localizedDescription }
    }
}

/// 1問を解く。通報・ブロック・（自分の投稿なら）削除もここから。
struct CommunityDetailView: View {
    let row: CommunityRow
    let isMine: Bool
    var onChanged: () -> Void
    @Environment(\.dismiss) private var dismiss
    @State private var showReport = false
    @State private var confirmBlock = false
    @State private var confirmDelete = false
    @State private var message: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Text(row.title).font(Theme.font(20, .bold)).foregroundStyle(Theme.ink)
                    Spacer()
                    Button("閉じる") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                .padding(.top, 24)

                if let p = row.problem {
                    ProblemSolverView(problem: p, onCorrect: { _ in }, continueLabel: "とじる", onContinue: { dismiss() })
                } else {
                    Text("この問題は表示できません。").foregroundStyle(Theme.danger)
                }

                if let message {
                    Text(message).font(Theme.font(13)).foregroundStyle(Theme.tealDeep)
                }

                if isMine {
                    Button("この投稿を削除") { confirmDelete = true }
                        .font(Theme.font(15, .semibold)).foregroundStyle(Theme.danger)
                        .frame(maxWidth: .infinity)
                } else {
                    HStack(spacing: 24) {
                        Button("通報する") { showReport = true }
                        Button("この人をブロック") { confirmBlock = true }
                    }
                    .font(Theme.font(14, .semibold)).foregroundStyle(Theme.inkSoft)
                    .frame(maxWidth: .infinity)
                }
            }
            .padding(.horizontal, 20).padding(.bottom, 40)
        }
        .isoBackground()
        .confirmationDialog("通報の理由", isPresented: $showReport, titleVisibility: .visible) {
            ForEach(["不適切な内容", "答えがまちがっている", "その他"], id: \.self) { reason in
                Button(reason) { run { try await Community.shared.report(row.id, reason: reason); message = "通報しました。ありがとうございます。" } }
            }
        }
        .confirmationDialog("この人の投稿を、今後表示しませんか？", isPresented: $confirmBlock, titleVisibility: .visible) {
            Button("ブロックする", role: .destructive) {
                run { try await Community.shared.block(row.author); onChanged(); dismiss() }
            }
        }
        .confirmationDialog("この投稿を削除しますか？", isPresented: $confirmDelete, titleVisibility: .visible) {
            Button("削除", role: .destructive) {
                run { try await Community.shared.deletePost(row.id); onChanged(); dismiss() }
            }
        }
    }

    private func run(_ work: @escaping () async throws -> Void) {
        Task {
            do { try await work() } catch { message = error.localizedDescription }
        }
    }
}
