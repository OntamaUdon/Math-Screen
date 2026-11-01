import SwiftUI

/// 30° のアイソメトリック投影で描く棒グラフ。最後の棒（今日）だけコーラル。
struct IsoBarChart: View {
    var values: [Int]
    var labels: [String] = []
    var caption: String
    var height: CGFloat = 190

    private let cos30 = cos(CGFloat.pi / 6)

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Canvas { ctx, size in
                draw(ctx, size: size)
            }
            .frame(height: height)
            .accessibilityElement()
            .accessibilityLabel(Text("\(caption)：" + values.map(String.init).joined(separator: "、")))
            Text(caption).font(Theme.font(12, .bold)).foregroundStyle(Theme.inkSoft)
        }
    }

    private struct Box { var x, y, z, w, d, h: CGFloat; var top, left, right: Color }

    private func draw(_ ctx: GraphicsContext, size: CGSize) {
        let n = CGFloat(max(values.count, 1))
        let gap: CGFloat = 1.15
        let span = n * gap + 0.4                     // 台座の長さ（単位）
        let maxBar: CGFloat = 2.2
        let maxValue = CGFloat(max(values.max() ?? 1, 1))
        // 画面上の範囲：横 = (span + 1.9)·cos30·s、縦 = (span + 1.1)·0.5·s + (maxBar + 0.35)·s + 文字の余白
        let s = min(size.width / ((span + 2.0) * cos30),
                    (size.height - 24) / ((span + 1.1) * 0.5 + maxBar + 0.35))
        let originX = (size.width - (span + 1.9) * cos30 * s) / 2 + 1.5 * cos30 * s
        let originY = size.height - 8 - (span + 1.1) * 0.5 * s

        func p(_ x: CGFloat, _ y: CGFloat, _ z: CGFloat) -> CGPoint {
            CGPoint(x: originX + (x - y) * cos30 * s, y: originY + (x + y) * 0.5 * s - z * s)
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

        // 台座
        box(Box(x: -0.2, y: -0.6, z: 0, w: span, d: 1.6, h: 0.25,
                top: Theme.surface, left: Theme.line, right: Theme.sunkenSide))
        // 棒（手前ほど後に描く）
        for (i, v) in values.enumerated() {
            let isToday = i == values.count - 1
            let h = max(0.12, CGFloat(v) / maxValue * maxBar)
            box(Box(x: CGFloat(i) * gap + 0.1, y: -0.3, z: 0.25, w: 0.8, d: 0.8, h: h,
                    top: isToday ? Theme.coralLight : Theme.tealLight,
                    left: isToday ? Theme.coral : Theme.teal,
                    right: isToday ? Theme.coralDeep : Theme.tealDeep))
            if i < labels.count {
                let at = p(CGFloat(i) * gap + 0.5, 1.3, 0)
                ctx.draw(Text(labels[i]).font(Theme.font(10, .bold)).foregroundColor(Theme.inkSoft), at: at)
            }
        }
        if let last = values.last {
            let top = p(CGFloat(values.count - 1) * gap + 0.5, 0.1, 0.25 + max(0.12, CGFloat(last) / maxValue * maxBar))
            ctx.draw(Text("今日 \(last)").font(Theme.font(11, .heavy)).foregroundColor(Theme.ink),
                     at: CGPoint(x: top.x, y: top.y - 10))
        }
    }
}
