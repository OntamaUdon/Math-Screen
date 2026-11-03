import Foundation
import UIKit
import ImageIO

/// ブロック画面の拡張機能が使う、最小限の共有データ。
/// この拡張機能はメモリの制限が特に厳しいので、重い部品（FamilyControls など）を含む Shared は読み込まず、
/// 必要なものだけをここに置く。キー名は Shared/SharedModels.swift の SharedStore と同じ。
enum ShieldData {
    private static let group = "group.com.ontamaudon.qlock"
    private static var defaults: UserDefaults { UserDefaults(suiteName: group) ?? .standard }

    /// ブロック画面に出す、文字だけの問題文。
    static var pendingBody: String? { defaults.string(forKey: "pendingProblemBody") }
    static var pendingID: String? { defaults.string(forKey: "pendingProblemID") }
    /// ロックがかかった時の「何分使ったか」。
    static var pendingMinutes: Int { defaults.integer(forKey: "pendingMinutes") }

    /// 画面が作られた時刻を残す（設定の「診断」で見る）。
    static func recordDiag(_ key: String) { defaults.set(Date().timeIntervalSince1970, forKey: "diag.\(key)") }

    /// 診断用の一言メモ（外観など）を残す。
    static func recordNote(_ key: String, _ value: String) { defaults.set(value, forKey: "diagNote.\(key)") }

    /// アプリが LaTeX で描いた問題の画像。メモリを使いすぎないよう、縮小しながら読む。
    static func problemImage() -> UIImage? {
        guard let id = pendingID,
              let dir = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: group)?
                .appendingPathComponent("problem-images", isDirectory: true),
              let src = CGImageSourceCreateWithURL(dir.appendingPathComponent("\(id).png") as CFURL, nil) else { return nil }
        let options: [CFString: Any] = [
            kCGImageSourceCreateThumbnailFromImageAlways: true,
            kCGImageSourceCreateThumbnailWithTransform: true,
            kCGImageSourceThumbnailMaxPixelSize: 720,
        ]
        guard let cg = CGImageSourceCreateThumbnailAtIndex(src, 0, options as CFDictionary) else { return nil }
        return UIImage(cgImage: cg)
    }
}
