import SwiftUI
import UIKit

/// 問題の共有（X や LINE など）。保護者用設定がオンの家庭では、初期状態ではオフ。
@MainActor enum ShareSetting {
    private static let key = "share.allowed"
    /// 共有を使えるか。保護者が決めていなければ、保護者用設定がオフのときだけ使える。
    static var isAllowed: Bool {
        if let v = UserDefaults.standard.object(forKey: key) as? Bool { return v }
        return !(ParentLock.shared.isEnabled && ParentLock.shared.hasPasscode)
    }
    static func set(_ on: Bool) { UserDefaults.standard.set(on, forKey: key) }

    /// 共有する文に入れるアプリの URL。App Store の URL が決まったら、ここに入れる。空なら入れない。
    nonisolated static let appURL = ""
}

enum ShareKind {
    case ask, solved

    var message: String {
        let head = self == .ask ? "この問題、どう考えればいいか、ヒントをください。" : "この問題、解けた！みんなは解けるかな？"
        var s = head + "\n（解くまでアプリが開かなくなる「解くロック」の問題です）\n#解くロック"
        if !ShareSetting.appURL.isEmpty { s += "\n" + ShareSetting.appURL }
        return s
    }
}

/// 問題のカードを画面から切り取り、アプリの名前を付けた画像にする。
@MainActor enum ShareImage {
    static func make(cardFrame: CGRect, kind: ShareKind) -> UIImage? {
        guard let window = UIApplication.shared.connectedScenes.compactMap({ ($0 as? UIWindowScene)?.keyWindow }).first,
              cardFrame.width > 10, cardFrame.height > 10 else { return nil }
        let crop = UIGraphicsImageRenderer(size: cardFrame.size).image { _ in
            window.drawHierarchy(in: CGRect(x: -cardFrame.minX, y: -cardFrame.minY,
                                            width: window.bounds.width, height: window.bounds.height), afterScreenUpdates: true)
        }
        let view = VStack(spacing: 0) {
            Image(uiImage: crop)
            HStack(spacing: 8) {
                if kind == .solved {
                    Label("正解", systemImage: "checkmark.circle.fill").font(Theme.font(16, .heavy)).foregroundStyle(Theme.tealDeep)
                }
                Spacer()
                Text("解くロック").font(Theme.font(16, .heavy)).foregroundStyle(Theme.ink)
            }
            .padding(.horizontal, 16).padding(.vertical, 12)
            .frame(width: cardFrame.width)
            .background(Color.white)
        }
        let r = ImageRenderer(content: view)
        r.scale = 3
        return r.uiImage
    }
}

struct ShareItem: Identifiable {
    let id = UUID()
    let image: UIImage
    let text: String
}

struct ActivityView: UIViewControllerRepresentable {
    let item: ShareItem
    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: [item.image, item.text], applicationActivities: nil)
    }
    func updateUIViewController(_ vc: UIActivityViewController, context: Context) {}
}

/// 画面上の位置を知るための印。
struct FrameReader: ViewModifier {
    @Binding var frame: CGRect
    func body(content: Content) -> some View {
        content.background(GeometryReader { g in
            Color.clear.onAppear { frame = g.frame(in: .global) }
                .onChange(of: g.frame(in: .global)) { _, f in frame = f }
        })
    }
}
