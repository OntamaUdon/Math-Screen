import SwiftUI

/// マインドマップの1つの枝。子が空なら葉（タップすると選ばれる）。
struct MapNode: Identifiable {
    let id: String
    var title: String
    var subtitle: String? = nil
    var subject: Subject? = nil
    var children: [MapNode] = []
    var progress: UnitProgress? = nil         // 単元の完成度（問題集のマップで、メーターに出す）

    var tint: (top: Color, side: Color) {
        switch subject {
        case .math: (Theme.teal, Theme.tealDeep)
        case .english: (Theme.violet, Theme.violetDeep)
        case .social: (Theme.gold, Theme.goldDeep)
        case .science: (Theme.coral, Theme.coralDeep)
        case .japanese: (Color(hex: 0x5B8DEF), Color(hex: 0x3A66C4))
        case .general: (Color(hex: 0xFF6FA8), Color(hex: 0xD14780))
        case nil: (Theme.ink, Color(hex: 0x0F1020))
        }
    }

    func contains(_ id: String) -> Bool { self.id == id || children.contains { $0.contains(id) } }
    var allIDs: [String] { [id] + children.flatMap(\.allIDs) }
}

/// 枝から枝へ伸びる線。位置が動くときに、一緒に動く。
private struct EdgeShape: Shape {
    var from: CGPoint
    var to: CGPoint

    var animatableData: AnimatablePair<AnimatablePair<CGFloat, CGFloat>, AnimatablePair<CGFloat, CGFloat>> {
        get { .init(.init(from.x, from.y), .init(to.x, to.y)) }
        set { from = CGPoint(x: newValue.first.first, y: newValue.first.second); to = CGPoint(x: newValue.second.first, y: newValue.second.second) }
    }

    func path(in rect: CGRect) -> Path {
        var p = Path()
        p.move(to: from)
        let mid = (from.x + to.x) / 2
        p.addCurve(to: to, control1: CGPoint(x: mid, y: from.y), control2: CGPoint(x: mid, y: to.y))
        return p
    }
}

/// 指で動かして、つまんで拡大・縮小できるマインドマップ。枝をタップすると開き、葉をタップすると onSelect が呼ばれる。
struct MindMapView: View {
    let root: MapNode
    var selectedID: String? = nil
    var openPath: [String] = []             // 最初から開いておく枝
    /// 枝にチェックを付ける使い方（ルールの出題範囲）。nil なら、ふつうのマップ。
    var checkState: ((MapNode) -> CheckState)? = nil
    var onCheck: ((MapNode) -> Void)? = nil
    var onSelect: (MapNode) -> Void

    enum CheckState { case off, partial, on }

    @State private var expanded: Set<String> = []
    @State private var offset: CGSize = .zero
    @State private var dragStart: CGSize = .zero
    @State private var scale: CGFloat = 1
    @State private var scaleStart: CGFloat = 1
    @State private var viewSize: CGSize = .zero
    @State private var started = false

    private var nodeW: CGFloat { checkState == nil ? 148 : 176 }
    private var colW: CGFloat { nodeW + 48 }
    private let nodeH: CGFloat = 64, rowH: CGFloat = 76, margin: CGFloat = 20

    private struct Placed: Identifiable {
        var id: String { node.id }
        let node: MapNode
        let depth: Int
        let y: CGFloat
        let parent: String?
        let open: Bool
    }

    // MARK: 配置
    private func layout(_ open: Set<String>) -> (items: [Placed], width: CGFloat, height: CGFloat) {
        var items: [Placed] = []
        var maxDepth = 0
        func place(_ node: MapNode, depth: Int, start: CGFloat, parent: String?) -> CGFloat {
            maxDepth = max(maxDepth, depth)
            let kids = open.contains(node.id) ? node.children : []
            var used: CGFloat = 0
            for k in kids { used += place(k, depth: depth + 1, start: start + used, parent: node.id) }
            let slots = max(used, 1)
            items.append(Placed(node: node, depth: depth, y: (start + slots / 2) * rowH, parent: parent, open: open.contains(node.id)))
            return slots
        }
        let total = place(root, depth: 0, start: 0, parent: nil)
        return (items, margin * 2 + CGFloat(maxDepth) * colW + nodeW + 8, total * rowH + 8)
    }

    private func center(_ p: Placed) -> CGPoint {
        CGPoint(x: margin + CGFloat(p.depth) * colW + nodeW / 2, y: p.y)
    }

    var body: some View {
        let l = layout(expanded)
        let byID = Dictionary(uniqueKeysWithValues: l.items.map { ($0.id, $0) })
        GeometryReader { geo in
            ZStack(alignment: .topLeading) {
                ZStack(alignment: .topLeading) {
                    ForEach(l.items) { item in
                        if let pid = item.parent, let parent = byID[pid] {
                            let a = center(parent), b = center(item)
                            EdgeShape(from: CGPoint(x: a.x + nodeW / 2, y: a.y), to: CGPoint(x: b.x - nodeW / 2, y: b.y))
                                .stroke(item.node.tint.side.opacity(0.45), style: StrokeStyle(lineWidth: 2.5, lineCap: .round))
                                .transition(.opacity)
                        }
                    }
                    ForEach(l.items) { item in
                        nodeView(item)
                            .position(center(item))
                            .transition(.opacity.combined(with: .scale(scale: 0.8)))
                    }
                }
                .frame(width: l.width, height: l.height, alignment: .topLeading)
                .scaleEffect(scale, anchor: .topLeading)
                .offset(offset)
            }
            .frame(width: geo.size.width, height: geo.size.height, alignment: .topLeading)
            .clipped()
            .contentShape(Rectangle())
            .simultaneousGesture(
                DragGesture(minimumDistance: 8)
                    .onChanged { v in offset = CGSize(width: dragStart.width + v.translation.width, height: dragStart.height + v.translation.height) }
                    .onEnded { _ in dragStart = offset }
            )
            .simultaneousGesture(
                MagnifyGesture()
                    .onChanged { v in scale = min(max(scaleStart * v.magnification, 0.5), 1.6) }
                    .onEnded { _ in scaleStart = scale }
            )
            .overlay(alignment: .bottomLeading) {
                Button { recenter(animated: true) } label: {
                    Image(systemName: "scope").font(.system(size: 18, weight: .semibold)).foregroundStyle(Theme.tealDeep)
                        .frame(width: 44, height: 44)
                        .background(Slab(top: Theme.surface, side: Theme.surfaceSide, depth: 3, radius: 12))
                }
                .accessibilityLabel("マップを元の位置に戻す")
                .padding(.leading, 14).padding(.bottom, 14)
            }
            .overlay(alignment: .bottom) {
                Text("指で動かす・つまんで拡大").font(Theme.font(11)).foregroundStyle(Theme.inkFaint).padding(.bottom, 8)
            }
            .onAppear { viewSize = geo.size; start() }
            .onChange(of: geo.size) { _, s in viewSize = s }
        }
    }

    // MARK: 枝
    @ViewBuilder private func nodeView(_ item: Placed) -> some View {
        let n = item.node
        let tint = n.tint
        let isRoot = item.depth == 0
        let isLeaf = n.children.isEmpty
        let filled = isRoot || item.depth == 1
        let selected = selectedID == n.id
        let ink: Color = filled ? .white : Theme.ink
        ZStack {
            Slab(top: filled ? tint.top : (selected ? tint.top.opacity(0.25) : Theme.surface), side: filled ? tint.side : Theme.surfaceSide,
                 depth: 4, radius: 12)
            if !filled { RoundedRectangle(cornerRadius: 12, style: .continuous).stroke(tint.top.opacity(selected ? 1 : 0.6), lineWidth: 2) }
            HStack(spacing: 6) {
                if let cs = checkState?(n) {
                    Image(systemName: cs == .on ? "checkmark.square.fill" : (cs == .partial ? "minus.square.fill" : "square"))
                        .font(.system(size: 24))
                        .foregroundStyle(cs == .off ? (filled ? Color.white.opacity(0.85) : Theme.inkFaint) : (filled ? Color.white : tint.top))
                        .frame(width: 34, height: nodeH)
                        .contentShape(Rectangle())
                        .onTapGesture { onCheck?(n) }
                }
                VStack(alignment: .leading, spacing: 1) {
                    Text(n.title).font(Theme.font(isRoot ? 16 : 14, .bold)).foregroundStyle(ink)
                        .lineLimit(2).minimumScaleFactor(0.8).multilineTextAlignment(.leading)
                    if let s = n.subtitle {
                        Text(s).font(Theme.font(11)).foregroundStyle(filled ? Color.white.opacity(0.85) : Theme.inkSoft).lineLimit(1)
                    }
                    if let pr = n.progress { MasteryMeter(progress: pr).padding(.top, 3) }
                }
                Spacer(minLength: 0)
                if !isLeaf {
                    Image(systemName: item.open ? "minus.circle.fill" : "plus.circle.fill")
                        .font(.system(size: 16)).foregroundStyle(filled ? Color.white.opacity(0.9) : tint.top)
                } else if selected {
                    Image(systemName: "checkmark.circle.fill").font(.system(size: 16)).foregroundStyle(tint.side)
                }
            }
            .padding(.leading, checkState == nil ? 10 : 2).padding(.trailing, 10)
        }
        .frame(width: nodeW, height: nodeH)
        .contentShape(Rectangle())
        .onTapGesture { tap(item) }
        .accessibilityElement(children: .combine)
        .accessibilityAddTraits(.isButton)
    }

    // MARK: 動き
    private func tap(_ item: Placed) {
        guard !item.node.children.isEmpty else { onSelect(item.node); return }
        var next = expanded
        if next.contains(item.id) {
            for id in item.node.allIDs { next.remove(id) }
        } else {
            // 同じ階層のほかの枝は閉じる（広がりすぎないように）
            if let pid = item.parent, let parent = find(pid, in: root) {
                for sib in parent.children where sib.id != item.id { for id in sib.allIDs { next.remove(id) } }
            }
            next.insert(item.id)
        }
        // タップした枝が、画面上で同じ位置に残るようにずらす
        let before = layout(expanded).items.first { $0.id == item.id }
        let after = layout(next).items.first { $0.id == item.id }
        withAnimation(.snappy(duration: 0.35)) {
            expanded = next
            if let b = before, let a = after {
                offset.height += (b.y - a.y) * scale
                dragStart = offset
            }
        }
    }

    private func find(_ id: String, in node: MapNode) -> MapNode? {
        if node.id == id { return node }
        for c in node.children { if let f = find(id, in: c) { return f } }
        return nil
    }

    private func start() {
        guard !started else { return }
        started = true
        expanded = Set(openPath)
        recenter(animated: false)
    }

    /// 根を左端の中央に置く。選択中の枝があるときは、そこが見えるようにする。
    private func recenter(animated: Bool) {
        scale = 1; scaleStart = 1
        let l = layout(expanded)
        let target = selectedID.flatMap { id in l.items.first { $0.id == id } } ?? l.items.first { $0.depth == 0 }
        guard let t = target else { return }
        let c = center(t)
        let x: CGFloat = t.depth == 0 ? 0 : -(c.x - viewSize.width + nodeW + 40)
        let new = CGSize(width: min(x, 0), height: viewSize.height / 2 - c.y)
        if animated { withAnimation(.snappy) { offset = new } } else { offset = new }
        dragStart = new
    }
}
