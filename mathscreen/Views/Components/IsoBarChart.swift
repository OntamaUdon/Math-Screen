import SwiftUI

/// アイソメトリックの棒グラフ。手前の1列が今週（月〜日）、過去の週は奥（右上）へ1週ずつ並ぶ。
/// 今日の棒はコーラル、今週は濃い緑、過去の週は薄い緑。
/// 棒の高さは固定の目盛り（`fullAt` 問で満タン）。少ない数でも差が見えるよう、平方根で伸ばす。
/// 色は10問ごとに変わり、数が増えるほど少しずつ華やかになる（水色→緑→金→橙→桃→紫→藍→赤→銀→黒金）。色の見方は、グラフの下に凡例を並べる。
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
            legend
            Text(caption).font(Theme.font(12, .bold)).foregroundStyle(Theme.inkSoft)
        }
    }

    /// 色が何問を表すか。1日の正解数がこの数に届くと、その色になる。
    private var legend: some View {
        HStack(spacing: 0) {
            ForEach(1...10, id: \.self) { tier in
                VStack(spacing: 2) {
                    RoundedRectangle(cornerRadius: 3, style: .continuous)
                        .fill(Self.tierColors(tier).1)
                        .frame(height: 10)
                        .overlay(RoundedRectangle(cornerRadius: 3, style: .continuous).stroke(Self.tierColors(tier).2.opacity(0.5), lineWidth: 1))
                    Text(tier == 10 ? "100~" : "\(tier * 10)").font(Theme.font(9, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                .frame(maxWidth: .infinity)
                .padding(.horizontal, 1.5)
            }
        }
        .accessibilityHidden(true)
    }

    /// 10問ごとの色（top, 左の面, 右の面）。10問=水色、20=緑、30=金、40=橙、50=桃、60=紫、70=藍、80=赤、90=銀、100〜=黒と金。
    private static func tierColors(_ tier: Int) -> (Color, Color, Color) {
        switch min(tier, 10) {
        case 1: return (Color(hex: 0xBDE3FF), Color(hex: 0x5BB8F5), Color(hex: 0x2F86C9))
        case 2: return (Color(hex: 0xC4F0B0), Color(hex: 0x6FD04F), Color(hex: 0x3FA32E))
        case 3: return (Color(hex: 0xFFE08A), Color(hex: 0xF2B632), Color(hex: 0xC48A12))
        case 4: return (Color(hex: 0xFFC999), Color(hex: 0xFF9A3C), Color(hex: 0xD1701A))
        case 5: return (Color(hex: 0xFFC2DA), Color(hex: 0xFF6FA8), Color(hex: 0xD14780))
        case 6: return (Color(hex: 0xCDB6FF), Color(hex: 0x9B7BF0), Color(hex: 0x6B4FC0))
        case 7: return (Color(hex: 0xA9B8FF), Color(hex: 0x4A5FE0), Color(hex: 0x2B3AA8))
        case 8: return (Color(hex: 0xFF9AA0), Color(hex: 0xE0323F), Color(hex: 0xA81F2B))
        case 9: return (Color(hex: 0xFFFFFF), Color(hex: 0xD5DAE6), Color(hex: 0x9AA3B8))
        default: return (Color(hex: 0xFFD25E), Color(hex: 0x3A3E58), Color(hex: 0x23263A))
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
        // 横に余った分は左右に分け、グラフを真ん中に置く
        let slack = max(0, (size.width - labelMargin - (10.45 + depth) * cos30 * s) / 2)
        let ox = 4 + 1.6 * cos30 * s + slack
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
                let tier = value / 10
                let colors: (Color, Color, Color) =
                    tier >= 1 ? Self.tierColors(tier)
                    : isToday ? (Theme.coralLight, Theme.coral, Theme.coralDeep)
                    : k == 0 ? (Theme.tealLight, Theme.teal, Theme.tealDeep)
                    : (Color(hex: 0xBFEFE8), Color(hex: 0x8ADBD0), Color(hex: 0x5EBFB2))
                let h = max(0.12, sqrt(min(CGFloat(value) / full, 1)) * maxBar)
                items.append((CGFloat(i) * gap + 0.1 + y + 10, {
                    let bx = CGFloat(i) * gap + 0.1
                    box(Box(x: bx, y: y, z: 0.2, w: 0.8, d: 0.8, h: h,
                            top: colors.0, left: colors.1, right: colors.2))
                    if tier >= 5 {          // 50問〜：上の面に光沢
                        face([(bx + 0.14, y + 0.14, 0.2 + h), (bx + 0.5, y + 0.14, 0.2 + h),
                              (bx + 0.5, y + 0.3, 0.2 + h), (bx + 0.14, y + 0.3, 0.2 + h)], .white.opacity(0.55))
                    }
                    if tier >= 8 {          // 80問〜：てっぺんに星
                        let t = p(bx + 0.4, y + 0.4, 0.2 + h)
                        ctx.draw(Text("✦").font(.system(size: 13, weight: .bold)).foregroundColor(colors.1),
                                 at: CGPoint(x: t.x, y: t.y - 9))
                    }
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
