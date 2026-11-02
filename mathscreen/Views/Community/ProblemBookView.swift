import SwiftUI

/// 問題集の1件。アプリ内蔵の問題か、みんなが投稿した問題。
struct FeedItem: Identifiable, Hashable {
    let id: String
    let problem: Problem
    let row: CommunityRow?      // みんなの問題のとき
    var isCommunity: Bool { row != nil }
}

/// 問題集：内蔵の問題と、承認された投稿を混ぜて、スクロールでいくらでも見られる。
struct ProblemBookView: View {
    enum Filter: Hashable { case all, subject(Subject), mine }

    @Environment(AppModel.self) private var model
    @State private var filter: Filter = .all
    @State private var community: [CommunityRow] = []
    @State private var mine: [CommunityRow] = []
    @State private var items: [FeedItem] = []
    @State private var pool: [FeedItem] = []
    @State private var cycle = 0
    @State private var selected: FeedItem?
    @State private var showPost = false
    @State private var error: String?

    private var filters: [Filter] {
        [.all] + Subject.allCases.map { Filter.subject($0) } + (model.isPremium ? [.mine] : [])
    }

    var body: some View {
        ZStack(alignment: .bottomTrailing) {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 14) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("問題集").font(Theme.font(28, .bold)).foregroundStyle(Theme.ink)
                        Text("好きな問題を選んで挑戦。タップすると、コメントも見られます。")
                            .font(Theme.font(14)).foregroundStyle(Theme.inkSoft)
                    }
                    .padding(.top, 12)

                    TagPicker(items: filters, selection: $filter) { label($0) }

                    if let error {
                        Text(error).font(Theme.font(13)).foregroundStyle(Theme.danger)
                    }
                    if items.isEmpty {
                        Text(filter == .mine ? "まだ投稿がありません。右下の + から投稿できます。" : "問題がありません。")
                            .font(Theme.font(15)).foregroundStyle(Theme.inkSoft)
                            .padding(20).frame(maxWidth: .infinity, alignment: .leading).well()
                    }
                    ForEach(items) { item in
                        card(item)
                            .contentShape(Rectangle())
                            .onTapGesture { selected = item }
                            .onAppear { if item.id == items.last?.id { loadMore() } }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 96)
            }
            .scrollIndicators(.hidden)
            .isoBackground()

            if model.isPremium {        // 投稿できるのは Premium だけ。無料では何も出さない。
                Button { showPost = true } label: {
                    Image(systemName: "plus").font(.system(size: 26, weight: .bold)).foregroundStyle(.white)
                        .frame(width: 60, height: 60)
                        .background(Slab(top: Theme.teal, side: Theme.tealDeep, depth: 5, radius: 16))
                }
                .padding(.trailing, 25).padding(.bottom, 14)
            }
        }
        .task { await reload() }
        .onChange(of: filter) { _, _ in reset() }
        .onChange(of: model.isPremium) { _, premium in if !premium && filter == .mine { filter = .all } }
        .sheet(item: $selected) { item in
            ProblemDetailView(item: item, isMine: filter == .mine) { Task { await reload() } }
        }
        .sheet(isPresented: $showPost, onDismiss: { Task { await reload() } }) { PostProblemView() }
    }

    private func label(_ f: Filter) -> String {
        switch f {
        case .all: "すべて"
        case .subject(let s): s.label
        case .mine: "自分の投稿"
        }
    }

    private func card(_ item: FeedItem) -> some View {
        let p = item.problem
        return VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 6) {
                Text(p.title).font(Theme.font(16, .bold)).foregroundStyle(Theme.ink)
                Spacer(minLength: 4)
                if filter == .mine, let r = item.row {
                    Text(r.statusLabel).font(Theme.font(12, .bold))
                        .foregroundStyle(r.status == "approved" ? Theme.tealDeep : (r.status == "pending" ? Theme.inkSoft : Theme.danger))
                } else if item.isCommunity {
                    Text("みんなの").font(Theme.font(11, .bold)).foregroundStyle(Theme.tealDeep)
                }
            }
            Text("\(p.categoryInfo.label) ・ \(p.difficultyInfo.label)")
                .font(Theme.font(12, .semibold)).foregroundStyle(Theme.inkSoft)
            Text(p.plain).font(Theme.font(14)).foregroundStyle(Theme.inkSoft).lineLimit(2)
            if filter == .mine, let note = item.row?.reviewNote, item.row?.status == "rejected", !note.isEmpty {
                Text("理由：\(note)").font(Theme.font(12)).foregroundStyle(Theme.danger)
            }
        }
        .card(padding: 14)
    }

    // MARK: 読み込み
    private func reload() async {
        error = nil
        do { community = try await Community.shared.approved() }
        catch { community = []; self.error = "みんなの問題を読み込めませんでした（内蔵の問題は使えます）。" }
        if model.isPremium { mine = (try? await Community.shared.mine()) ?? [] } else { mine = [] }
        reset()
    }

    private func reset() {
        items = []
        cycle = 0
        pool = makePool()
        loadMore()
    }

    private func makePool() -> [FeedItem] {
        var out: [FeedItem] = []
        switch filter {
        case .mine:
            out = mine.compactMap { r in r.problem.map { FeedItem(id: "m-\(r.id)", problem: $0, row: r) } }
        case .all, .subject:
            var subject: Subject?
            if case .subject(let s) = filter { subject = s }
            for p in ProblemBank.all where subject == nil || p.categoryInfo.subject == subject {
                out.append(FeedItem(id: "b\(cycle)-\(p.id)", problem: p, row: nil))
            }
            for r in community {
                guard let p = r.problem, subject == nil || p.categoryInfo.subject == subject else { continue }
                out.append(FeedItem(id: "c\(cycle)-\(r.id)", problem: p, row: r))
            }
            out.shuffle()
        }
        return out
    }

    /// 末尾に近づいたら20件ずつ足す。使い切ったら混ぜ直して続ける（自分の投稿は一巡で終わり）。
    private func loadMore() {
        if pool.isEmpty, filter != .mine {
            cycle += 1
            pool = makePool()
        }
        guard !pool.isEmpty else { return }
        items.append(contentsOf: pool.prefix(20))
        pool.removeFirst(min(20, pool.count))
    }
}
