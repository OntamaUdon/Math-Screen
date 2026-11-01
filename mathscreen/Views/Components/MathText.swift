import SwiftUI
import WebKit

/// LaTeX 混じりの文（`$...$` が数式）を KaTeX で表示する。
/// KaTeX 一式は Resources/katex（アプリ内蔵・オフラインで動く）。
struct MathText: View {
    var source: String
    var fontSize: CGFloat = 19
    var color: Color = Theme.ink
    /// VoiceOver 用の読み上げ文（なければ LaTeX をそのまま読む）
    var spoken: String? = nil

    @State private var height: CGFloat = 48   // 読み込み前の仮の高さ。KaTeX が測った高さに差し替わる

    var body: some View {
        MathWebView(source: source, fontSize: fontSize, cssColor: color.cssHex, height: $height)
            .frame(height: height)
            .accessibilityElement()
            .accessibilityLabel(Text(spoken ?? source.replacingOccurrences(of: "$", with: "")))
    }
}

private struct MathWebView: UIViewRepresentable {
    var source: String
    var fontSize: CGFloat
    var cssColor: String
    @Binding var height: CGFloat

    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeUIView(context: Context) -> WKWebView {
        let controller = WKUserContentController()
        controller.add(context.coordinator, name: "height")
        let config = WKWebViewConfiguration()
        config.userContentController = controller

        let web = WKWebView(frame: .zero, configuration: config)
        web.isOpaque = false
        web.backgroundColor = .clear
        web.scrollView.backgroundColor = .clear
        web.scrollView.isScrollEnabled = false
        web.scrollView.bounces = false
        web.isUserInteractionEnabled = false
        web.navigationDelegate = context.coordinator
        context.coordinator.web = web

        if let dir = Bundle.main.url(forResource: "katex", withExtension: nil) {
            web.loadFileURL(dir.appendingPathComponent("index.html"), allowingReadAccessTo: dir)
        }
        return web
    }

    func updateUIView(_ web: WKWebView, context: Context) {
        let c = context.coordinator
        c.height = $height
        c.pending = (source, fontSize, cssColor)
        c.applyIfReady()
    }

    static func dismantleUIView(_ web: WKWebView, coordinator: Coordinator) {
        web.configuration.userContentController.removeScriptMessageHandler(forName: "height")
    }

    final class Coordinator: NSObject, WKScriptMessageHandler, WKNavigationDelegate {
        weak var web: WKWebView?
        var height: Binding<CGFloat>?
        var pending: (String, CGFloat, String)?
        private var loaded = false
        private var applied: String?

        func userContentController(_ c: WKUserContentController, didReceive message: WKScriptMessage) {
            guard let h = (message.body as? NSNumber)?.doubleValue, h > 0 else { return }
            DispatchQueue.main.async { [weak self] in
                if self?.height?.wrappedValue != CGFloat(h) { self?.height?.wrappedValue = CGFloat(h) }
            }
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            loaded = true
            applyIfReady()
        }

        func applyIfReady() {
            guard loaded, let web, let (src, size, color) = pending else { return }
            let key = "\(src)|\(size)|\(color)"
            guard key != applied else { return }
            applied = key
            // 文字列は JSON にして JavaScript に渡す（バックスラッシュや引用符をそのまま安全に運ぶ）
            guard let data = try? JSONEncoder().encode(src), let literal = String(data: data, encoding: .utf8) else { return }
            web.evaluateJavaScript("render(\(literal), \(size), '\(color)')")
        }
    }
}

private extension Color {
    /// CSS の #RRGGBB。
    var cssHex: String {
        let ui = UIColor(self)
        var r: CGFloat = 0, g: CGFloat = 0, b: CGFloat = 0, a: CGFloat = 0
        ui.getRed(&r, green: &g, blue: &b, alpha: &a)
        return String(format: "#%02X%02X%02X", Int(r * 255 + 0.5), Int(g * 255 + 0.5), Int(b * 255 + 0.5))
    }
}
