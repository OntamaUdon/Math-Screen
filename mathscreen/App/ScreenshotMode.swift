import Foundation

/// App Store 審査用のスクリーンショットを、シミュレータで撮るための起動引数。
/// 例：`-screenshot plan` で、購入の画面だけを開く（本物の画面。価格などは見本）。普段の起動では何も起きない。
enum ScreenshotMode {
    static var scene: String? {
        let a = CommandLine.arguments
        guard let i = a.firstIndex(of: "-screenshot"), i + 1 < a.count else { return nil }
        return a[i + 1]
    }
}
