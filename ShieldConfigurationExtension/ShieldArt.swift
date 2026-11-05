import UIKit

/// ブロック画面のアイコン欄に出す、アイソメトリック（斜め上から見た立体）の南京錠のイラスト。
/// 画像ファイルは使わず、コードで描く（拡張機能のメモリを小さく保つため）。
enum ShieldArt {
    static let lockIcon: UIImage = draw()

    private static func color(_ hex: UInt32) -> UIColor {
        UIColor(red: CGFloat((hex >> 16) & 0xFF) / 255, green: CGFloat((hex >> 8) & 0xFF) / 255,
                blue: CGFloat(hex & 0xFF) / 255, alpha: 1)
    }

    private static func draw() -> UIImage {
        let side: CGFloat = 300
        let renderer = UIGraphicsImageRenderer(size: CGSize(width: side, height: side))
        return renderer.image { ctx in
            let g = ctx.cgContext
            // 立体の座標 (x, y, z) を画面の点に直す（30°の等角投影）。
            func P(_ x: CGFloat, _ y: CGFloat, _ z: CGFloat) -> CGPoint {
                CGPoint(x: side / 2 + (x - y) * 0.866, y: side * 0.62 + (x + y) * 0.5 - z)
            }
            func poly(_ pts: [CGPoint], _ c: UIColor) {
                g.setFillColor(c.cgColor)
                g.addLines(between: pts)
                g.closePath()
                g.fillPath()
            }
            // 直方体。上面・左の面・右の面の3面だけが見える。
            func box(_ x0: CGFloat, _ y0: CGFloat, _ z0: CGFloat, _ w: CGFloat, _ d: CGFloat, _ h: CGFloat,
                     top: UIColor, left: UIColor, right: UIColor) {
                let x1 = x0 + w, y1 = y0 + d, z1 = z0 + h
                poly([P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)], left)
                poly([P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)], right)
                poly([P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], top)
            }

            // 土台（白とグレーの板）
            box(-84, -62, 0, 168, 124, 14, top: .white, left: color(0xC7CCDA), right: color(0xDDE1EC))
            // 奥のティールの小さなブロック
            box(34, -54, 14, 30, 30, 28, top: color(0x7FE0D3), left: color(0x26968A), right: color(0x3CC5B5))
            // 錠の本体（コーラル。横長で、大きい面を手前に）
            let bx: CGFloat = -42, by: CGFloat = -22, bz: CGFloat = 14, bw: CGFloat = 84, bd: CGFloat = 44, bh: CGFloat = 62
            box(bx, by, bz, bw, bd, bh, top: color(0xFFB29D), left: color(0xD2553A), right: color(0xFF7A59))
            let top = bz + bh

            // つる：x-z 平面の U 字を、厚みのある管として描く（奥行き→手前の順に重ねる）
            let ym = by + bd / 2, r: CGFloat = 25
            var path: [(CGFloat, CGFloat)] = [(-r, top), (-r, top + 22)]
            for i in 0...36 {
                let a = CGFloat.pi - CGFloat.pi * CGFloat(i) / 36
                path.append((r * cos(a), top + 22 + r * sin(a)))
            }
            path += [(r, top + 22), (r, top)]
            func stroke(_ offsetY: CGFloat, _ c: UIColor, _ width: CGFloat) {
                let b = UIBezierPath()
                for (n, q) in path.enumerated() {
                    let pt = P(q.0, ym + offsetY, q.1)
                    if n == 0 { b.move(to: pt) } else { b.addLine(to: pt) }
                }
                b.lineWidth = width
                b.lineCapStyle = .round
                b.lineJoinStyle = .round
                c.setStroke()
                b.stroke()
            }
            for off in [6, 4.5, 3, 1.5] as [CGFloat] { stroke(off, color(0x4E5370), 13) }
            stroke(0, color(0x8E94AD), 13)
            stroke(-1.5, color(0xB8BED3), 7)

            // 鍵穴（大きい面＝左の面に、面の傾きに合わせて描く）
            let c = P(0, by + bd, bz + bh * 0.52)
            func face(_ px: CGFloat, _ py: CGFloat) -> CGPoint {
                CGPoint(x: c.x + px * 0.866, y: c.y + px * 0.5 - py)
            }
            g.setFillColor(color(0x23263A).cgColor)
            let ring = (0...36).map { i -> CGPoint in
                let t = CGFloat(i) * .pi / 18
                return face(8 * cos(t), 8 * sin(t) + 5)
            }
            g.addLines(between: ring); g.closePath(); g.fillPath()
            g.addLines(between: [face(-3.6, 6), face(3.6, 6), face(5, -14), face(-5, -14)]); g.closePath(); g.fillPath()
        }
    }
}
