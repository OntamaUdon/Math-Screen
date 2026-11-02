import UIKit
import WebKit

/// 問題文（LaTeX 混じり）を KaTeX で描いて、白い背景・角丸の PNG にする。
/// 問題を追加しても自動で画像になる。ブロック画面は文字しか出せないため、アイコン欄にこの画像を入れる。
@MainActor
final class ProblemImageRenderer: NSObject, WKNavigationDelegate {
    static let shared = ProblemImageRenderer()

    private let width: CGFloat = 520
    private let fontSize: CGFloat = 26
    private var busy = false
    private var loadContinuation: CheckedContinuation<Void, Never>?

    /// 画像がまだなければ作って保存する。作れたら（または既にあれば）true。
    @discardableResult
    func ensureImage(for problem: Problem) async -> Bool {
        if ProblemImageStore.exists(forID: problem.id) { return true }
        guard !busy, let window = Self.keyWindow else { return false }   // 起動直後で画面がまだなければ、次の機会に作る
        busy = true
        defer { busy = false }

        guard let dir = Bundle.main.url(forResource: "katex", withExtension: nil) else { return false }

        let config = WKWebViewConfiguration()
        let web = WKWebView(frame: CGRect(x: -5000, y: 0, width: width, height: 400), configuration: config)
        web.isOpaque = true
        web.backgroundColor = .white
        web.scrollView.backgroundColor = .white
        web.navigationDelegate = self
        window.addSubview(web)                       // 画面の外に置く（描画のためウィンドウに載せる必要がある）
        defer { web.removeFromSuperview() }

        // 1. KaTeX のページを読み込む
        await withCheckedContinuation { (c: CheckedContinuation<Void, Never>) in
            loadContinuation = c
            web.loadFileURL(dir.appendingPathComponent("index.html"), allowingReadAccessTo: dir)
        }

        // 2. 描画して、フォントの読み込みを待ち、高さを測る
        let script = """
        document.body.style.background = '#FFFFFF';       // 数式の背景は白
        document.getElementById('m').style.padding = '16px 18px';
        render(src, size, color);
        await document.fonts.ready;
        return Math.ceil(document.getElementById('m').getBoundingClientRect().height);
        """
        guard let result = try? await web.callAsyncJavaScript(
                script,
                arguments: ["src": Self.imageSource(problem), "size": Double(fontSize), "color": "#23263A"],
                contentWorld: .page),
              let height = (result as? NSNumber)?.doubleValue, height > 0 else { return false }

        web.frame = CGRect(x: -5000, y: 0, width: width, height: CGFloat(height))
        try? await Task.sleep(nanoseconds: 150_000_000)   // レイアウトが落ち着くのを待つ

        // 3. 画像にして保存
        let snap = WKSnapshotConfiguration()
        snap.rect = web.bounds
        snap.snapshotWidth = NSNumber(value: Double(width) * 2)
        guard let shot = try? await web.takeSnapshot(configuration: snap),
              let png = Self.roundedCorners(shot, radius: 20).pngData() else { return false }
        ProblemImageStore.save(png, forID: problem.id)
        return true
    }

    nonisolated func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        Task { @MainActor in
            loadContinuation?.resume()
            loadContinuation = nil
        }
    }

    nonisolated func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        Task { @MainActor in
            loadContinuation?.resume()
            loadContinuation = nil
        }
    }

    /// 画像にする文。4択は、選択肢（① … ④）も続けて入れる。
    private static func imageSource(_ p: Problem) -> String {
        guard let choices = p.choices else { return p.body }
        return p.body + "\n" + choices.enumerated().map { "\(Problem.choiceMarks[$0.offset]) \($0.element)" }.joined(separator: "\n")
    }

    /// 白いカードに見えるよう、角を丸くする（角の外側は透明）。
    private static func roundedCorners(_ image: UIImage, radius: CGFloat) -> UIImage {
        let format = UIGraphicsImageRendererFormat()
        format.scale = image.scale
        format.opaque = false
        return UIGraphicsImageRenderer(size: image.size, format: format).image { _ in
            UIBezierPath(roundedRect: CGRect(origin: .zero, size: image.size), cornerRadius: radius).addClip()
            image.draw(at: .zero)
        }
    }

    private static var keyWindow: UIWindow? {
        UIApplication.shared.connectedScenes
            .compactMap { $0 as? UIWindowScene }
            .flatMap(\.windows)
            .first(where: \.isKeyWindow)
    }
}
