import SwiftUI

/// 問題集の1件。
struct FeedItem: Identifiable, Hashable {
    let id: String
    let problem: Problem
}

/// マインドマップの木をつくる。
enum BookMap {
    static let stages = ["小学", "中学", "高校", "ノンジャンル"]

    /// 教科 → 小学・中学・高校・ノンジャンル → 単元 の枝。単元の枝のつくりは unitNode で決める。
    private static func subjectNodes(unitNode: (UnitInfo, Subject) -> MapNode) -> [MapNode] {
        var subjects: [MapNode] = []
        for s in Subject.allCases {
            let units = UnitCatalog.units(in: s)
            if units.isEmpty { continue }
            let stageNodes: [MapNode] = stages.compactMap { st in
                let list = units.filter { $0.stage == st }
                guard !list.isEmpty else { return nil }
                let unitNodes = list.map { unitNode($0, s) }
                // 10個を超えるときは、グループ（物理・数学IIなど）に分ける
                var kids = unitNodes
                if list.count > 10 {
                    var order: [String] = []
                    for u in list { let g = u.group ?? "その他"; if !order.contains(g) { order.append(g) } }
                    kids = order.map { g in
                        let members = list.indices.filter { (list[$0].group ?? "その他") == g }
                        return MapNode(id: "gr:\(s.rawValue):\(st):\(g)", title: g, subtitle: "\(members.count)単元", subject: s,
                                       children: members.map { unitNodes[$0] })
                    }
                }
                return MapNode(id: "st:\(s.rawValue):\(st)", title: st, subtitle: "\(list.count)単元", subject: s, children: kids)
            }
            // 「ノンジャンル」の教科は、段階の枝を省いて直接ぶら下げる
            let children = s == .general ? (stageNodes.first?.children ?? []) : stageNodes
            subjects.append(MapNode(id: "sub:\(s.rawValue)", title: s.label, subtitle: units.isEmpty ? nil : "\(units.count)単元", subject: s, children: children))
        }
        return subjects
    }

    /// 問題集：教科 → 小学・中学・高校・ノンジャンル → 単元。
    static func browse() -> MapNode {
        let subjects = subjectNodes { u, s in
            let n = UnitCatalog.problemCount[u.id] ?? 0
            let level = MasteryStore.shared.progress(unit: u.id).level
            return MapNode(id: "u:\(u.id)", title: u.name, subtitle: level == .none ? "\(n)問" : "\(n)問 ・ \(level.label)", subject: s,
                           progress: MasteryStore.shared.progress(unit: u.id))
        }
        return MapNode(id: "root", title: "問題集", children: subjects)
    }

    /// ルールの出題範囲を選ぶ：問題集と同じ形の枝。単元にチェックを付ける。
    static func selector() -> MapNode {
        MapNode(id: "root", title: "出題する範囲",
                children: subjectNodes(unitNode: { u, s in
                    MapNode(id: "u:\(u.id)", title: u.name, subtitle: "\(UnitCatalog.problemCount[u.id] ?? 0)問", subject: s)
                }))
    }
}

/// 問題集：マインドマップをたどって、問題を探す。キーワードで探すこともできる。
struct ProblemBookView: View {
    @Environment(AppModel.self) private var model
    @State private var query = ""
    @State private var results: [FeedItem] = []
    @State private var sheet: ProblemListSheet.Source?
    @State private var selected: FeedItem?
    @State private var tick = 0           // 詳細を閉じたとき、印を読み直す

    private var trimmedQuery: String { query.trimmingCharacters(in: .whitespacesAndNewlines) }

    var body: some View {
        let _ = tick
        Group {
            VStack(alignment: .leading, spacing: 10) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("問題集").font(Theme.font(28, .bold)).foregroundStyle(Theme.ink)
                    Text(trimmedQuery.isEmpty ? "枝をタップして広げ、単元を選んで挑戦。" : "検索結果")
                        .font(Theme.font(14)).foregroundStyle(Theme.inkSoft)
                }
                .padding(.horizontal, 20).padding(.top, 12)

                searchField.padding(.horizontal, 20)

                if trimmedQuery.isEmpty {
                    MindMapView(root: BookMap.browse(),
                                openPath: ScreenshotMode.scene == "book" ? ["root", "sub:math", "st:math:中学", "gr:math:中学:数と式"] : ["root"],
                                initialScale: ScreenshotMode.scene == "book" ? 0.6 : 1) { node in
                        if node.id.hasPrefix("u:") { sheet = .unit(String(node.id.dropFirst(2))) }
                    }
                } else {
                    resultList
                }
            }
            .isoBackground()

        }
        .task(id: query) {                       // 入力が止まってから検索する
            try? await Task.sleep(for: .milliseconds(300))
            if !Task.isCancelled { search() }
        }
        .sheet(item: $sheet) { src in ProblemListSheet(source: src).roomySheet() }
        .sheet(item: $selected, onDismiss: { tick += 1 }) { item in ProblemDetailView(item: item).roomySheet() }
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

    private var resultList: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 14) {
                if results.isEmpty {
                    Text("見つかりませんでした。ほかのキーワードで探してみてください。")
                        .font(Theme.font(15)).foregroundStyle(Theme.inkSoft)
                        .padding(20).frame(maxWidth: .infinity, alignment: .leading).well()
                } else {
                    Text("該当 \(results.count) 問").font(Theme.font(12, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                ForEach(results) { item in
                    ProblemCard(item: item, mark: ProblemMarkStore.shared.mark(item.problem.id))
                        .contentShape(Rectangle())
                        .onTapGesture { selected = item }
                }
            }
            .padding(.horizontal, 20).padding(.bottom, 96)
        }
        .scrollIndicators(.hidden)
    }

    private func search() {
        let tokens = trimmedQuery.lowercased().split(separator: " ").map(String.init)
        guard !tokens.isEmpty else { results = []; return }
        var out: [FeedItem] = []
        for p in ProblemBank.all where ProblemBook.matches(p, tokens: tokens) {
            out.append(FeedItem(id: "b-\(p.id)", problem: p))
            if out.count >= 300 { break }
        }
        results = out
    }
}

enum ProblemBook {
    /// 検索のキーワード（空白で区切り、すべて含むものだけ）に合うか。
    static func matches(_ p: Problem, tokens: [String]) -> Bool {
        if tokens.isEmpty { return true }
        let unitName = p.unit.flatMap { UnitCatalog.info($0)?.name } ?? ""
        let hay = (p.plain + " " + p.title + " " + unitName + " " + p.categoryInfo.label).lowercased()
        return tokens.allSatisfy { hay.contains($0) }
    }
}

/// 問題の一覧の1行。
struct ProblemCard: View {
    let item: FeedItem
    var mark: ProblemMark? = nil          // 解いた結果の印（☆◎〇△）

    private func markColor(_ m: ProblemMark) -> Color {
        switch m {
        case .perfect: Theme.gold
        case .once: Theme.tealDeep
        case .many: Theme.teal
        case .skipped: Theme.coral
        }
    }

    var body: some View {
        let p = item.problem
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 6) {
                if let mark {
                    Text(mark.symbol).font(Theme.font(18, .heavy)).foregroundStyle(markColor(mark))
                        .accessibilityLabel(mark.label)
                }
                Text(p.title).font(Theme.font(16, .bold)).foregroundStyle(Theme.ink)
                Spacer(minLength: 4)
            }
            Text(p.categoryInfo.label)
                .font(Theme.font(12, .semibold)).foregroundStyle(Theme.inkSoft)
            Text(p.plain).font(Theme.font(14)).foregroundStyle(Theme.inkSoft).lineLimit(2)
        }
        .card(padding: 14)
    }
}

/// マップで選んだ単元の問題一覧。
struct ProblemListSheet: View {
    enum Source: Identifiable, Hashable {
        case unit(String)
        var id: String {
            switch self {
            case .unit(let u): "u:\(u)"
            }
        }
    }

    let source: Source
    @Environment(\.dismiss) private var dismiss
    @State private var items: [FeedItem] = []
    @State private var selected: FeedItem?
    @State private var tick = 0

    private var title: String {
        switch source {
        case .unit(let u): UnitCatalog.info(u)?.name ?? "単元"
        }
    }

    var body: some View {
        let _ = tick
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 14) {
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(title).font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
                        if case .unit(let u) = source, let info = UnitCatalog.info(u) {
                            Text("\(info.subjectInfo.label) ・ \(info.stage)").font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                        }
                    }
                    Spacer()
                    Button("閉じる") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                .padding(.top, 24)

                Text("☆ 1発正解　◎ 1回まちがえて正解　〇 2回以上まちがえて正解　△ 解かずに変更")
                    .font(Theme.font(11)).foregroundStyle(Theme.inkSoft)
                if items.isEmpty {
                    Text("この単元には、まだ問題がありません。").font(Theme.font(15)).foregroundStyle(Theme.inkSoft)
                        .padding(20).frame(maxWidth: .infinity, alignment: .leading).well()
                } else {
                    Text("\(items.count) 問").font(Theme.font(12, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                ForEach(items) { item in
                    ProblemCard(item: item, mark: ProblemMarkStore.shared.mark(item.problem.id))
                        .contentShape(Rectangle())
                        .onTapGesture { selected = item }
                }
            }
            .padding(.horizontal, 20).padding(.bottom, 40)
        }
        .scrollIndicators(.hidden)
        .isoBackground()
        .onAppear { load() }
        .sheet(item: $selected, onDismiss: { tick += 1 }) { item in
            ProblemDetailView(item: item).roomySheet()
        }
    }

    private func load() {
        switch source {
        case .unit(let u):
            // やさしい問題（正解しやすい見積もり）から並べる
            items = ProblemBank.all.filter { $0.unit == u }
                .enumerated().sorted { ($0.element.rate ?? 5, -$0.offset) > ($1.element.rate ?? 5, -$1.offset) }
                .map { FeedItem(id: "b-\($0.element.id)", problem: $0.element) }
        }
    }
}
