import Foundation

/// ブロック画面の拡張機能が使う、最小限の共有データ。
/// この拡張機能はメモリの制限が特に厳しいので、重い部品（FamilyControls など）を含む Shared は読み込まず、
/// 必要なものだけをここに置く。キー名は Shared/SharedModels.swift の SharedStore と同じ。
enum ShieldData {
    private static var defaults: UserDefaults { UserDefaults(suiteName: "group.com.ontamaudon.qlock") ?? .standard }

    /// ブロック画面に出す、文字だけの問題文。
    static var pendingBody: String? { defaults.string(forKey: "pendingProblemBody") }

    /// 画面が作られた時刻を残す（設定の「診断」で見る）。
    static func recordDiag(_ key: String) { defaults.set(Date().timeIntervalSince1970, forKey: "diag.\(key)") }
}
