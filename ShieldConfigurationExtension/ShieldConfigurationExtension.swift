import ManagedSettings
import ManagedSettingsUI
import UIKit

/// ブロック画面（シールド）の見た目。入力欄は置けないため、ボタンで本体アプリへ誘導する。
final class ShieldConfigurationExtension: ShieldConfigurationDataSource {
    override func configuration(shielding application: Application) -> ShieldConfiguration {
        make(name: application.localizedDisplayName)
    }

    override func configuration(shielding application: Application, in category: ActivityCategory) -> ShieldConfiguration {
        make(name: application.localizedDisplayName)
    }

    override func configuration(shielding webDomain: WebDomain) -> ShieldConfiguration {
        make(name: webDomain.domain)
    }

    override func configuration(shielding webDomain: WebDomain, in category: ActivityCategory) -> ShieldConfiguration {
        make(name: webDomain.domain)
    }

    /// ライトグリーンの背景に、タイトル・説明1行・問題文だけを出す（アイコンと「閉じる」は出さない）。
    private func make(name: String?) -> ShieldConfiguration {
        let ink = UIColor(red: 0.137, green: 0.149, blue: 0.227, alpha: 1)        // #23263A
        let teal = UIColor(red: 0.235, green: 0.773, blue: 0.710, alpha: 1)       // #3CC5B5（アプリのボタンと同じ色）
        let gray = UIColor(red: 0.890, green: 0.906, blue: 0.949, alpha: 1)       // #E3E7F2
        let target = name ?? "このアプリ"

        var subtitle = "\(target) の時間になりました"
        if let problem = SharedStore.pendingProblemBody {
            subtitle += "\n\n" + problem
        }

        return ShieldConfiguration(
            backgroundBlurStyle: nil,
            backgroundColor: teal,
            icon: Self.blankIcon,
            title: ShieldConfiguration.Label(text: "1問解いて再開", color: ink),
            subtitle: ShieldConfiguration.Label(text: subtitle, color: ink),
            primaryButtonLabel: ShieldConfiguration.Label(text: "問題を解く", color: ink),
            primaryButtonBackgroundColor: gray,
            secondaryButtonLabel: nil
        )
    }

    /// アイコンを出さないための透明な画像（nil だと iOS 既定のアイコンが出る場合があるため）。
    private static let blankIcon: UIImage = UIGraphicsImageRenderer(size: CGSize(width: 1, height: 1)).image { _ in }
}
