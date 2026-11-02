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
    @State private var query = ""
    @State private var unitFilter: String?
    @State private var showUnitPicker = false
    @State private var total = 0

    /// これまでに一覧に出した問題（出した順）。次からは、まだ出していない問題を先に並べる。
    private static let seenKey = "book.seen"
    private static var seen: [String] {
        get { UserDefaults.standard.stringArray(forKey: seenKey) ?? [] }
        set { UserDefaults.standard.set(Array(newValue.suffix(5000)), forKey: seenKey) }
    }

    private var filters: [Filter] {
        [.all] + Subject.allCases.map { Filter.subject($0) } + (model.isPremium ? [.mine] : [])
    }

    var body: some View {
        ZStack(alignment: .bottomTrailing) {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 14) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("問題集").font(Theme.font(28, .bold)).foregroundStyle(Theme.ink)
                        Text("好きな問題を選んで挑戦。")
                            .font(Theme.font(14)).foregroundStyle(Theme.inkSoft)
                    }
                    .padding(.top, 12)

                    searchField

                    TagPicker(items: filters, selection: $filter) { label($0) }

                    if filter != .mine { unitRow }

                    if let error {
                        Text(error).font(Theme.font(13)).foregroundStyle(Theme.danger)
                    }
                    if isFiltering, !items.isEmpty {
                        Text("該当 \(total) 問").font(Theme.font(12, .semibold)).foregroundStyle(Theme.inkSoft)
                    }
                    if items.isEmpty {
                        Text(filter == .mine ? "まだ投稿がありません。右下の + から投稿できます。"
                             : (isFiltering ? "条件に合う問題が見つかりません。キーワードや単元を変えてみてください。" : "問題がありません。"))
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
        .task(id: query) {                       // 入力が止まってから検索する
            try? await Task.sleep(for: .milliseconds(300))
            if !Task.isCancelled { reset() }
        }
        .onChange(of: filter) { _, new in
            // 教科を変えたとき、その教科にない単元の絞り込みは外す
            if let u = unitFilter, let info = UnitCatalog.info(u) {
                switch new {
                case .subject(let s): if info.subject != s.rawValue { unitFilter = nil }
                case .mine: unitFilter = nil
                case .all: break
                }
            }
            reset()
        }
        .onChange(of: unitFilter) { _, _ in reset() }
        .sheet(isPresented: $showUnitPicker) {
            UnitPickerSheet(subjects: pickerSubjects, selected: $unitFilter)
        }
        .onChange(of: model.isPremium) { _, premium in if !premium && filter == .mine { filter = .all } }
        .sheet(item: $selected) { item in
            ProblemDetailView(item: item, isMine: filter == .mine) { Task { await reload() } }
        }
        .sheet(isPresented: $showPost, onDismiss: { Task { await reload() } }) { PostProblemView() }
    }

    private var isFiltering: Bool { !trimmedQuery.isEmpty || unitFilter != nil }
    private var trimmedQuery: String { query.trimmingCharacters(in: .whitespacesAndNewlines) }

    private var pickerSubjects: [Subject] {
        if case .subject(let s) = filter { return [s] }
        return Subject.allCases
    }

    /// 検索欄。問題文・単元名・分野名に、キーワードがすべて含まれる問題を探す。
    private var searchField: some View {
        HStack(spacing: 8) {
            Image(systemName: "magnifyingglass").foregroundStyle(Theme.inkFaint)
            TextField("問題・単語・単元を検索", text: $query)
                .font(Theme.font(16))
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .submitLabel(.search)
            if !query.isEmpty {
                Button { query = "" } label: {
                    Image(systemName: "xmark.circle.fill").foregroundStyle(Theme.inkFaint)
                }
                .accessibilityLabel("検索をクリア")
            }
        }
        .padding(12)
        .well()
    }

    /// 単元で絞り込むボタン。選ぶと、その単元の問題だけが並ぶ。
    private var unitRow: some View {
        HStack(spacing: 8) {
            Button { showUnitPicker = true } label: {
                Label(unitFilter.flatMap { UnitCatalog.info($0)?.name } ?? "単元で絞り込む", systemImage: "line.3.horizontal.decrease.circle")
                    .font(Theme.font(14, .semibold))
                    .foregroundStyle(unitFilter == nil ? Theme.inkSoft : Theme.tealDeep)
            }
            if unitFilter != nil {
                Button { unitFilter = nil } label: {
                    Image(systemName: "xmark.circle.fill").foregroundStyle(Theme.inkFaint)
                }
                .accessibilityLabel("単元の絞り込みを外す")
            }
            Spacer()
        }
    }

    /// 検索のキーワード（空白で区切り、すべて含むものだけ）に合うか。
    private func matches(_ p: Problem, tokens: [String]) -> Bool {
        if tokens.isEmpty { return true }
        let unitName = p.unit.flatMap { UnitCatalog.info($0)?.name } ?? ""
        let hay = (p.plain + " " + p.title + " " + unitName + " " + p.categoryInfo.label).lowercased()
        return tokens.allSatisfy { hay.contains($0) }
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
            Text(p.categoryInfo.label)
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
        total = pool.count
        loadMore()
    }

    private func makePool() -> [FeedItem] {
        let tokens = trimmedQuery.lowercased().split(separator: " ").map(String.init)
        var out: [FeedItem] = []
        switch filter {
        case .mine:
            out = mine.compactMap { r in r.problem.map { FeedItem(id: "m-\(r.id)", problem: $0, row: r) } }
                .filter { matches($0.problem, tokens: tokens) }
        case .all, .subject:
            var subject: Subject?
            if case .subject(let s) = filter { subject = s }
            // 英単語は数が多いので、絞り込みも検索もしないときは一部だけ混ぜる（全部は、ルールの出題で使われる）
            let capWords = !isFiltering
            var wordsLeft = subject == .english ? 600 : 150
            for p in ProblemBank.all.shuffled() where subject == nil || p.categoryInfo.subject == subject {
                if let u = unitFilter, p.unit != u { continue }
                if !matches(p, tokens: tokens) { continue }
                if capWords, p.category == "eng_word" {
                    if wordsLeft == 0 { continue }
                    wordsLeft -= 1
                }
                out.append(FeedItem(id: "b\(cycle)-\(p.id)", problem: p, row: nil))
            }
            if unitFilter == nil {
                for r in community {
                    guard let p = r.problem, subject == nil || p.categoryInfo.subject == subject, matches(p, tokens: tokens) else { continue }
                    out.append(FeedItem(id: "c\(cycle)-\(r.id)", problem: p, row: r))
                }
            }
            if tokens.isEmpty {
                out.shuffle()
                // まだ出していない問題を先に。出したことがある問題は、古く見たものから後ろに回す。
                let order = Dictionary(Self.seen.enumerated().map { ($1, $0) }, uniquingKeysWith: { _, new in new })
                out.sort { (order[$0.problem.id] ?? -1) < (order[$1.problem.id] ?? -1) }
            }
        }
        return out
    }

    /// 末尾に近づいたら20件ずつ足す。使い切ったら混ぜ直して続ける（自分の投稿は一巡で終わり）。
    private func loadMore() {
        if pool.isEmpty, filter != .mine, trimmedQuery.isEmpty {
            cycle += 1
            pool = makePool()
        }
        guard !pool.isEmpty else { return }
        let page = Array(pool.prefix(20))
        items.append(contentsOf: page)
        pool.removeFirst(min(20, pool.count))
        let ids = Set(page.map(\.problem.id))
        Self.seen = Self.seen.filter { !ids.contains($0) } + page.map(\.problem.id)
    }
}


/// 単元を選ぶ画面。教科 → 小学・中学・高校の順に並び、問題数が出る。
struct UnitPickerSheet: View {
    var subjects: [Subject]
    @Binding var selected: String?
    @Environment(\.dismiss) private var dismiss

    private let stages = ["小学", "中学", "高校"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Text("単元を選ぶ").font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
                    Spacer()
                    Button("閉じる") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                .padding(.top, 24)

                Button { selected = nil; dismiss() } label: {
                    HStack {
                        Text("すべての単元").font(Theme.font(16, .semibold)).foregroundStyle(Theme.ink)
                        Spacer()
                        if selected == nil { Image(systemName: "checkmark").foregroundStyle(Theme.tealDeep) }
                    }
                    .padding(.horizontal, 16).padding(.vertical, 14)
                    .card(padding: 0)
                }
                .buttonStyle(.plain)

                ForEach(subjects) { subject in
                    let units = UnitCatalog.units(in: subject)
                    if !units.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text(subject.label).font(Theme.font(16, .bold)).foregroundStyle(Theme.ink)
                            VStack(spacing: 0) {
                                ForEach(stages, id: \.self) { stage in
                                    let list = units.filter { $0.stage == stage }
                                    if !list.isEmpty {
                                        Text(stage).font(Theme.font(11, .bold)).foregroundStyle(Theme.inkSoft)
                                            .padding(.horizontal, 16).padding(.top, 10).padding(.bottom, 2)
                                            .frame(maxWidth: .infinity, alignment: .leading)
                                        ForEach(list) { unit in row(unit) }
                                    }
                                }
                            }
                            .padding(.bottom, 6)
                            .card(padding: 0)
                        }
                    }
                }
            }
            .padding(.horizontal, 20).padding(.bottom, 40)
        }
        .isoBackground()
    }

    private func row(_ unit: UnitInfo) -> some View {
        Button { selected = unit.id; dismiss() } label: {
            HStack {
                Text(unit.name).font(Theme.font(15)).foregroundStyle(Theme.ink)
                Spacer()
                Text("\(UnitCatalog.problemCount[unit.id] ?? 0) 問").font(Theme.font(12)).foregroundStyle(Theme.inkFaint)
                if selected == unit.id { Image(systemName: "checkmark").foregroundStyle(Theme.tealDeep) }
            }
            .padding(.horizontal, 16).padding(.vertical, 10)
            .background(selected == unit.id ? Theme.teal.opacity(0.12) : Color.clear)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }
}
