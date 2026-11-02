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
                CGPoint(x: side / 2 + (x - y) * 0.866, y: side * 0.64 + (x + y) * 0.5 - z)
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
            box(-70, -70, 0, 140, 140, 14, top: .white, left: color(0xC7CCDA), right: color(0xDDE1EC))
            // 奥のティールの小さなブロック
            box(32, -62, 14, 28, 28, 26, top: color(0x7FE0D3), left: color(0x26968A), right: color(0x3CC5B5))
            // 錠の本体（コーラル）
            box(-32, -32, 14, 64, 64, 52, top: color(0xFFB29D), left: color(0xD2553A), right: color(0xFF7A59))

            // つる（U字）
            let c = P(0, 0, 66)
            let shackle = UIBezierPath()
            shackle.move(to: CGPoint(x: c.x - 24, y: c.y))
            shackle.addLine(to: CGPoint(x: c.x - 24, y: c.y - 38))
            shackle.addArc(withCenter: CGPoint(x: c.x, y: c.y - 38), radius: 24,
                           startAngle: .pi, endAngle: 0, clockwise: true)
            shackle.addLine(to: CGPoint(x: c.x + 24, y: c.y))
            shackle.lineWidth = 12
            shackle.lineCapStyle = .round
            color(0x6B7088).setStroke()
            shackle.stroke()

            // 鍵穴（左の面に、面の傾きに合わせて描く）
            g.saveGState()
            let k = P(0, 32, 40)
            g.translateBy(x: k.x, y: k.y)
            g.concatenate(CGAffineTransform(a: 0.866, b: 0.5, c: 0, d: 1, tx: 0, ty: 0))
            g.setFillColor(color(0x23263A).cgColor)
            g.fillEllipse(in: CGRect(x: -8, y: -12, width: 16, height: 16))
            g.fill(CGRect(x: -4, y: -2, width: 8, height: 18))
            g.restoreGState()
        }
    }
}
