import Foundation

/// 利用規約とプライバシーポリシーの公開ページ。
/// URL を入れると、設定画面に「規約など」が出る（サブスクの審査で、アプリ内のリンクが必要）。
/// 文面のひな形は docs/TERMS.md と docs/PRIVACY.md。公開したページの URL をここに入れる。
enum LegalLinks {
    static let terms: URL? = nil
    static let privacy: URL? = nil
}
