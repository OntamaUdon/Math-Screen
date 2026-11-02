import SwiftUI

/// アイソメトリックの棒グラフ。手前の1列が今週（月〜日）、過去の週は奥（右上）へ1週ずつ並ぶ。
/// 今日の棒はコーラル、今週は濃い緑、過去の週は薄い緑。
/// 棒の高さは固定の目盛り（`fullAt` 問で満タン）。少ない数でも差が見えるよう、平方根で伸ばす。25問で金色、50問で紫。
struct IsoBarChart: View {
    /// weeks[0] が今週、weeks[1] が1週前…。値は日ごとの正解数。まだ来ていない日は nil。
    var weeks: [[Int?]]
    var caption: String

    private let cos30 = cos(CGFloat.pi / 6)
    private let dayLabels = ["月", "火", "水", "木", "金", "土", "日"]
    private let gap: CGFloat = 1.15        // 棒の間隔（横）
    private let rowGap: CGFloat = 1.9      // 週と週の間隔（奥行き）
    private let fullAt = 100               // この問数で棒が満タン

    private var rows: Int { max(weeks.count, 1) }
    private var height: CGFloat { rows == 1 ? 190 : 210 + 28 * CGFloat(rows - 1) }

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Canvas { ctx, size in draw(ctx, size: size) }
                .frame(height: height)
                .accessibilityElement()
                .accessibilityLabel(Text("\(caption)：今週は " + (weeks.first ?? []).map { $0.map(String.init) ?? "-" }.joined(separator: "、")))
            Text(caption).font(Theme.font(12, .bold)).foregroundStyle(Theme.inkSoft)
        }
    }

    private struct Box { var x, y, z, w, d, h: CGFloat; var top, left, right: Color }

    private func draw(_ ctx: GraphicsContext, size: CGSize) {
        let n = CGFloat(rows)
        let maxBar: CGFloat = rows == 1 ? 2.2 : 1.7
        let span = 7 * gap + 0.4                                  // 台座の長さ
        let depth = (n - 1) * rowGap
        let full = CGFloat(fullAt)

        // 画面に収まる大きさを決める。横 = (10.45 + 奥行き)·cos30·s、縦 = ((10.45 + 奥行き)·0.5 + 棒の高さ + 0.2)·s
        let labelMargin: CGFloat = 46
        let s = min((size.width - labelMargin) / ((10.45 + depth) * cos30),
                    (size.height - 16) / ((10.45 + depth) * 0.5 + maxBar + 0.2))
        let ox = 4 + 1.6 * cos30 * s
        let oy = 6 + ((0.8 + depth) * 0.5 + maxBar + 0.2) * s

        func p(_ x: CGFloat, _ y: CGFloat, _ z: CGFloat) -> CGPoint {
            CGPoint(x: ox + (x - y) * cos30 * s, y: oy + (x + y) * 0.5 * s - z * s)
        }
        func face(_ pts: [(CGFloat, CGFloat, CGFloat)], _ color: Color) {
            var path = Path()
            path.addLines(pts.map { p($0.0, $0.1, $0.2) })
            path.closeSubpath()
            ctx.fill(path, with: .color(color))
        }
        func box(_ b: Box) {
            face([(b.x, b.y + b.d, b.z), (b.x + b.w, b.y + b.d, b.z), (b.x + b.w, b.y + b.d, b.z + b.h), (b.x, b.y + b.d, b.z + b.h)], b.left)
            face([(b.x + b.w, b.y, b.z), (b.x + b.w, b.y + b.d, b.z), (b.x + b.w, b.y + b.d, b.z + b.h), (b.x + b.w, b.y, b.z + b.h)], b.right)
            face([(b.x, b.y, b.z + b.h), (b.x + b.w, b.y, b.z + b.h), (b.x + b.w, b.y + b.d, b.z + b.h), (b.x, b.y + b.d, b.z + b.h)], b.top)
        }

        // 奥にあるもの（x + y が小さいもの）から描く。台座はすべての棒より先。
        var items: [(key: CGFloat, draw: () -> Void)] = []
        for k in 0..<rows {
            let y = -CGFloat(k) * rowGap
            items.append((y - 0.5, {
                box(Box(x: -0.2, y: y - 0.6, z: 0, w: span, d: 1.6, h: 0.2,
                        top: Theme.surface, left: Theme.line, right: Theme.sunkenSide))
            }))
        }
        let todayIndex = weeks.first?.lastIndex(where: { $0 != nil })
        for (k, row) in weeks.enumerated() {
            for (i, value) in row.enumerated() {
                guard let value else { continue }
                let y = -CGFloat(k) * rowGap - 0.3
                let isToday = k == 0 && i == todayIndex
                let colors: (Color, Color, Color) =
                    value >= 50 ? (Theme.violetLight, Theme.violet, Theme.violetDeep)       // 50問以上
                    : value >= 25 ? (Theme.goldLight, Theme.gold, Theme.goldDeep)               // 25問以上
                    : isToday ? (Theme.coralLight, Theme.coral, Theme.coralDeep)
                    : k == 0 ? (Theme.tealLight, Theme.teal, Theme.tealDeep)
                    : (Color(hex: 0xBFEFE8), Color(hex: 0x8ADBD0), Color(hex: 0x5EBFB2))
                let h = max(0.12, sqrt(min(CGFloat(value) / full, 1)) * maxBar)
                items.append((CGFloat(i) * gap + 0.1 + y + 10, {
                    box(Box(x: CGFloat(i) * gap + 0.1, y: y, z: 0.2, w: 0.8, d: 0.8, h: h,
                            top: colors.0, left: colors.1, right: colors.2))
                }))
            }
        }
        for item in items.sorted(by: { $0.key < $1.key }) { item.draw() }

        // 曜日（手前の縁）
        for (i, label) in dayLabels.enumerated() {
            ctx.draw(Text(label).font(Theme.font(10, .bold)).foregroundColor(Theme.inkSoft),
                     at: p(CGFloat(i) * gap + 0.5, 1.3, 0))
        }
        // 週（右の縁）
        for k in 0..<rows {
            let at = p(span - 0.2 + 0.15, -CGFloat(k) * rowGap + 0.2, 0)
            ctx.draw(Text(k == 0 ? "今週" : "\(k)週前").font(Theme.font(10, .bold)).foregroundColor(Theme.inkSoft),
                     at: CGPoint(x: at.x + 22, y: at.y))
        }
        // 今日の数
        if let ti = todayIndex, let v = weeks[0][ti] {
            let h = max(0.12, sqrt(min(CGFloat(v) / full, 1)) * maxBar)
            let top = p(CGFloat(ti) * gap + 0.5, -0.3 + 0.4, 0.2 + h)
            ctx.draw(Text("今日 \(v)").font(Theme.font(11, .heavy)).foregroundColor(Theme.ink),
                     at: CGPoint(x: top.x, y: top.y - 12))
        }
    }
}
