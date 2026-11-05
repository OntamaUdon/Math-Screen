import Foundation

/// 利用規約とプライバシーポリシーの公開ページ。
/// URL を入れると、設定画面に「規約など」が出る（サブスクの審査で、アプリ内のリンクが必要）。
/// 文面のひな形は docs/TERMS.md と docs/PRIVACY.md。公開したページの URL をここに入れる。
enum LegalLinks {
    // GitHub Pages（docs フォルダ）で公開する。設定の Pages を有効にするまでは、リンクを開いても何も出ない。
    static let terms: URL? = URL(string: "https://ontamaudon.github.io/Math-Screen/terms.html")
    static let privacy: URL? = URL(string: "https://ontamaudon.github.io/Math-Screen/privacy.html")
}
