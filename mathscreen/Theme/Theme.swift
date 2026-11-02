import SwiftUI

extension Color {
    init(hex: UInt32, opacity: Double = 1) {
        self.init(.sRGB,
                  red: Double((hex >> 16) & 0xFF) / 255,
                  green: Double((hex >> 8) & 0xFF) / 255,
                  blue: Double(hex & 0xFF) / 255,
                  opacity: opacity)
    }
}

/// アイソメトリック：白とグレーのブロックに、ティール（主）とコーラル（警告・今日）の2色。
/// 面（top）と、斜めに見える側面（side）の2トーンで立体感を出す。
enum Theme {
    static let background = Color(hex: 0xEEF1F7)
    static let surface    = Color.white
    static let surfaceSide = Color(hex: 0xCBD1E1)
    static let sunken     = Color(hex: 0xE3E7F2)
    static let sunkenSide = Color(hex: 0xC7CCDA)
    static let line       = Color(hex: 0xDDE1EC)
    static let ink        = Color(hex: 0x23263A)
    static let inkSoft    = Color(hex: 0x6B7088)
    static let inkFaint   = Color(hex: 0x9AA0B5)

    static let tealLight  = Color(hex: 0x7FE0D3)
    static let teal       = Color(hex: 0x3CC5B5)
    static let tealDeep   = Color(hex: 0x26968A)
    static let coralLight = Color(hex: 0xFFB29D)
    static let coral      = Color(hex: 0xFF7A59)
    static let coralDeep  = Color(hex: 0xD2553A)
    static let danger     = coralDeep

    // 金・紫（グラフでは10問ごとの色を IsoBarChart で定義）
    static let goldLight   = Color(hex: 0xFFE08A)
    static let gold        = Color(hex: 0xF2B632)
    static let goldDeep    = Color(hex: 0xC48A12)
    static let violetLight = Color(hex: 0xCDB6FF)
    static let violet      = Color(hex: 0x9B7BF0)
    static let violetDeep  = Color(hex: 0x6B4FC0)

    static let radius: CGFloat = 8

    static func font(_ size: CGFloat, _ weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .rounded)
    }
}

/// 右下方向に厚みのある板。側面は 1pt ずつずらした同じ形を重ねて描く。
struct Slab: View {
    var top: Color
    var side: Color
    var depth: CGFloat
    var radius: CGFloat = Theme.radius

    var body: some View {
        let shape = RoundedRectangle(cornerRadius: radius, style: .continuous)
        ZStack {
            ForEach(Array(stride(from: depth, through: 1, by: -1)), id: \.self) { d in
                shape.fill(side).offset(x: d, y: d)
            }
            shape.fill(top)
        }
    }
}

extension View {
    /// 白いブロックのカード。
    func card(padding: CGFloat = 18, top: Color = Theme.surface, side: Color = Theme.surfaceSide, depth: CGFloat = 6) -> some View {
        self.padding(padding)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Slab(top: top, side: side, depth: depth))
            .padding(.trailing, depth)
            .padding(.bottom, depth)
    }

    /// 掘り込まれた面（入力欄など）。
    func well(radius: CGFloat = Theme.radius) -> some View {
        background(
            RoundedRectangle(cornerRadius: radius, style: .continuous)
                .fill(Theme.surface.shadow(.inner(color: Theme.line, radius: 0, x: 3, y: 3)))
        )
    }

    /// アイソメトリックの方眼を背景に敷く。
    func isoBackground() -> some View {
        background(IsoGrid().ignoresSafeArea())
    }
}

/// 30°/150° の細い線の方眼。
struct IsoGrid: View {
    var body: some View {
        Canvas { ctx, size in
            ctx.fill(Path(CGRect(origin: .zero, size: size)), with: .color(Theme.background))
            let step: CGFloat = 26
            let slope = tan(CGFloat.pi / 6)
            var path = Path()
            var x: CGFloat = -size.height / slope
            while x < size.width + size.height / slope {
                path.move(to: CGPoint(x: x, y: 0))
                path.addLine(to: CGPoint(x: x + size.height / slope, y: size.height))
                path.move(to: CGPoint(x: x, y: 0))
                path.addLine(to: CGPoint(x: x - size.height / slope, y: size.height))
                x += step
            }
            ctx.stroke(path, with: .color(Theme.ink.opacity(0.045)), lineWidth: 1)
        }
    }
}

/// 押すと沈む立体ボタン。
struct IsoButtonStyle: ButtonStyle {
    enum Kind { case primary, secondary, quiet, alert }
    var kind: Kind = .primary
    var large = false
    private let depth: CGFloat = 4

    func makeBody(configuration: Configuration) -> some View {
        let pressed = configuration.isPressed
        let d: CGFloat = pressed ? 1 : depth
        return configuration.label
            .font(Theme.font(large ? 22 : 16, .bold))
            .foregroundStyle(foreground)
            .padding(.vertical, large ? 11 : 14)
            .frame(maxWidth: .infinity)
            .background(Slab(top: colors.top, side: colors.side, depth: d))
            .offset(x: depth - d, y: depth - d)
            .padding(.trailing, depth)
            .padding(.bottom, depth)
            .animation(.easeOut(duration: 0.08), value: pressed)
    }

    private var colors: (top: Color, side: Color) {
        switch kind {
        case .primary: (Theme.teal, Theme.tealDeep)
        case .secondary: (Theme.surface, Theme.sunkenSide)
        case .quiet: (Theme.sunken, Theme.sunkenSide)
        case .alert: (Theme.coral, Theme.coralDeep)
        }
    }

    private var foreground: Color {
        switch kind {
        case .primary, .alert: .white
        case .secondary, .quiet: Theme.ink
        }
    }
}

extension ButtonStyle where Self == IsoButtonStyle {
    static var primary: IsoButtonStyle { IsoButtonStyle(kind: .primary) }
    static var secondary: IsoButtonStyle { IsoButtonStyle(kind: .secondary) }
    static var quiet: IsoButtonStyle { IsoButtonStyle(kind: .quiet) }
    static var alert: IsoButtonStyle { IsoButtonStyle(kind: .alert) }
}

/// 小さなラベル。選択中はティールのブロック。
struct Tag: View {
    var text: String
    var isOn: Bool = false

    var body: some View {
        Text(text)
            .font(Theme.font(13, .bold))
            .foregroundStyle(isOn ? .white : Theme.inkSoft)
            .padding(.horizontal, 12)
            .padding(.vertical, 7)
            .frame(maxWidth: .infinity)
            .background(Slab(top: isOn ? Theme.teal : Theme.sunken,
                             side: isOn ? Theme.tealDeep : Theme.sunkenSide,
                             depth: isOn ? 3 : 2, radius: 6))
            .padding(.trailing, 3)
            .padding(.bottom, 3)
    }
}

struct SectionLabel: View {
    var text: String
    init(_ text: String) { self.text = text }

    var body: some View {
        Text(text).font(Theme.font(13, .bold)).foregroundStyle(Theme.inkSoft)
    }
}
