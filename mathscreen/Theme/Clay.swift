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

/// モノトーン基調 + パステルのアクセント。
enum Clay {
    static let background = Color(hex: 0xE9E7E3)
    static let surface    = Color(hex: 0xF3F1EE)
    static let sunken     = Color(hex: 0xE2DFDA)
    static let ink        = Color(hex: 0x2E2D33)
    static let inkSoft    = Color(hex: 0x75737B)
    static let inkFaint   = Color(hex: 0xA6A3A9)
    static let shadow     = Color(hex: 0xB9B4AC)

    static let lavender = Color(hex: 0xCFC8EC)
    static let mint     = Color(hex: 0xC3E6D6)
    static let peach    = Color(hex: 0xF4D2C3)
    static let sky      = Color(hex: 0xC7DCF0)
    static let butter   = Color(hex: 0xF1E4B5)

    static let lavenderDeep = Color(hex: 0x8E84C6)
    static let mintDeep     = Color(hex: 0x5FA387)
    static let peachDeep    = Color(hex: 0xD27E62)

    static func font(_ size: CGFloat, _ weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .rounded)
    }
}

/// 膨らんだ粘土のような面：外側に柔らかい影、内側に上からのハイライトと下の陰。
struct ClaySurface: ViewModifier {
    var color: Color = Clay.surface
    var radius: CGFloat = 28
    var depth: CGFloat = 14

    func body(content: Content) -> some View {
        content.background(
            RoundedRectangle(cornerRadius: radius, style: .continuous)
                .fill(color
                    .shadow(.inner(color: .white.opacity(0.75), radius: depth * 0.35, x: depth * 0.3, y: depth * 0.35))
                    .shadow(.inner(color: .black.opacity(0.09), radius: depth * 0.45, x: -depth * 0.3, y: -depth * 0.4)))
                .shadow(color: Clay.shadow.opacity(0.55), radius: depth, x: depth * 0.5, y: depth * 0.7)
                .shadow(color: .white.opacity(0.85), radius: depth * 0.8, x: -depth * 0.4, y: -depth * 0.4)
        )
    }
}

/// へこんだ面（入力欄など）。
struct ClayWell: ViewModifier {
    var radius: CGFloat = 20

    func body(content: Content) -> some View {
        content.background(
            RoundedRectangle(cornerRadius: radius, style: .continuous)
                .fill(Clay.sunken
                    .shadow(.inner(color: Clay.shadow.opacity(0.8), radius: 6, x: 4, y: 5))
                    .shadow(.inner(color: .white.opacity(0.9), radius: 5, x: -4, y: -4)))
        )
    }
}

extension View {
    func clay(_ color: Color = Clay.surface, radius: CGFloat = 28, depth: CGFloat = 14) -> some View {
        modifier(ClaySurface(color: color, radius: radius, depth: depth))
    }

    func clayWell(radius: CGFloat = 20) -> some View {
        modifier(ClayWell(radius: radius))
    }
}

/// 押すと沈み込むボタン。
struct ClayButtonStyle: ButtonStyle {
    var color: Color = Clay.surface
    var radius: CGFloat = 22
    var foreground: Color = Clay.ink

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(Clay.font(17, .semibold))
            .foregroundStyle(foreground)
            .padding(.vertical, 16)
            .padding(.horizontal, 20)
            .frame(maxWidth: .infinity)
            .clay(color, radius: radius, depth: configuration.isPressed ? 4 : 10)
            .scaleEffect(configuration.isPressed ? 0.97 : 1)
            .animation(.spring(response: 0.25, dampingFraction: 0.6), value: configuration.isPressed)
    }
}

extension ButtonStyle where Self == ClayButtonStyle {
    static var clay: ClayButtonStyle { ClayButtonStyle() }
    static func clay(_ color: Color, foreground: Color = Clay.ink, radius: CGFloat = 22) -> ClayButtonStyle {
        ClayButtonStyle(color: color, radius: radius, foreground: foreground)
    }
}

/// 小さな丸いラベル。
struct ClayChip: View {
    var text: String
    var color: Color = Clay.lavender
    var isOn: Bool = true

    var body: some View {
        Text(text)
            .font(Clay.font(13, .semibold))
            .foregroundStyle(isOn ? Clay.ink : Clay.inkSoft)
            .padding(.horizontal, 12)
            .padding(.vertical, 7)
            .clay(isOn ? color : Clay.surface, radius: 14, depth: isOn ? 6 : 3)
    }
}

/// 背景（ほんのりパステルのにじみ）。
struct ClayBackdrop: View {
    var body: some View {
        ZStack {
            Clay.background
            Circle().fill(Clay.lavender.opacity(0.55)).frame(width: 320).blur(radius: 90).offset(x: -150, y: -320)
            Circle().fill(Clay.mint.opacity(0.5)).frame(width: 280).blur(radius: 90).offset(x: 170, y: 120)
            Circle().fill(Clay.peach.opacity(0.45)).frame(width: 260).blur(radius: 100).offset(x: -120, y: 420)
        }
        .ignoresSafeArea()
    }
}
