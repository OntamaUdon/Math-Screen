import UIKit

/// LaTeX で描いた問題の画像（PNG）の置き場所。アプリが書き、ブロック画面の拡張機能が読む。
/// App Group の共有フォルダに `<問題ID>.png` として保存する。
enum ProblemImageStore {
    private static var directory: URL? {
        FileManager.default
            .containerURL(forSecurityApplicationGroupIdentifier: AppGroup.identifier)?
            .appendingPathComponent("problem-images", isDirectory: true)
    }

    static func url(forID id: String) -> URL? {
        directory?.appendingPathComponent("\(id).png")
    }

    static func exists(forID id: String) -> Bool {
        url(forID: id).map { FileManager.default.fileExists(atPath: $0.path) } ?? false
    }

    static func image(forID id: String?) -> UIImage? {
        guard let id, let url = url(forID: id) else { return nil }
        return UIImage(contentsOfFile: url.path)
    }

    static func save(_ png: Data, forID id: String) {
        guard let dir = directory, let url = url(forID: id) else { return }
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        try? png.write(to: url, options: .atomic)
    }

    /// 使う問題（ルールごとの問題と、いまの問題）以外の画像を消して、保存先が増え続けないようにする。
    static func prune(keeping ids: Set<String>) {
        guard let dir = directory,
              let files = try? FileManager.default.contentsOfDirectory(at: dir, includingPropertiesForKeys: nil) else { return }
        for f in files where !ids.contains(f.deletingPathExtension().lastPathComponent) {
            try? FileManager.default.removeItem(at: f)
        }
    }
}
