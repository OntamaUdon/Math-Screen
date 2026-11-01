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

/// フラットデザイン：グレー基調 + ミント1色。影は使わず、面の濃淡と細い線で区切る。
enum Theme {
    static let background = Color(hex: 0xF3F3F1)
    static let surface    = Color.white
    static let sunken     = Color(hex: 0xEBEBE8)
    static let line       = Color(hex: 0xE2E2DE)
    static let ink        = Color(hex: 0x26262A)
    static let inkSoft    = Color(hex: 0x6E6E74)
    static let inkFaint   = Color(hex: 0xA3A3A8)

    static let mint       = Color(hex: 0xCDEBDD)   // 面（選択中・主ボタン）
    static let mintDeep   = Color(hex: 0x3F8F6E)   // 文字・アイコン・トグル
    static let danger     = Color(hex: 0xC2554A)   // 不正解・削除（意味を表す色）

    static func font(_ size: CGFloat, _ weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .rounded)
    }
}

extension View {
    /// 白いカード（細い線のみ、影なし）。
    func card(padding: CGFloat = 20) -> some View {
        self.padding(padding)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 16, style: .continuous).stroke(Theme.line, lineWidth: 1))
    }

    /// 少し沈んだ面（入力欄・グラフの背景）。
    func well(radius: CGFloat = 12) -> some View {
        background(Theme.sunken, in: RoundedRectangle(cornerRadius: radius, style: .continuous))
    }
}

/// ボタン。primary = ミント、secondary = 白＋線、quiet = 灰色の面。
struct FlatButtonStyle: ButtonStyle {
    enum Kind { case primary, secondary, quiet }
    var kind: Kind = .primary
    var large = false

    func makeBody(configuration: Configuration) -> some View {
        let shape = RoundedRectangle(cornerRadius: 12, style: .continuous)
        return configuration.label
            .font(Theme.font(large ? 22 : 16, .semibold))
            .foregroundStyle(Theme.ink)
            .padding(.vertical, large ? 13 : 15)
            .frame(maxWidth: .infinity)
            .background(fill, in: shape)
            .overlay(shape.stroke(kind == .secondary ? Theme.line : .clear, lineWidth: 1))
            .opacity(configuration.isPressed ? 0.6 : 1)
    }

    private var fill: Color {
        switch kind {
        case .primary: Theme.mint
        case .secondary: Theme.surface
        case .quiet: Theme.sunken
        }
    }
}

extension ButtonStyle where Self == FlatButtonStyle {
    static var primary: FlatButtonStyle { FlatButtonStyle(kind: .primary) }
    static var secondary: FlatButtonStyle { FlatButtonStyle(kind: .secondary) }
    static var quiet: FlatButtonStyle { FlatButtonStyle(kind: .quiet) }
}

/// 小さなラベル。選択中だけミント。
struct Tag: View {
    var text: String
    var isOn: Bool = false

    var body: some View {
        Text(text)
            .font(Theme.font(13, .semibold))
            .foregroundStyle(isOn ? Theme.mintDeep : Theme.inkSoft)
            .padding(.horizontal, 12)
            .padding(.vertical, 7)
            .background(isOn ? Theme.mint : Theme.sunken, in: Capsule())
    }
}

struct SectionLabel: View {
    var text: String
    init(_ text: String) { self.text = text }

    var body: some View {
        Text(text).font(Theme.font(13, .semibold)).foregroundStyle(Theme.inkSoft)
    }
}
