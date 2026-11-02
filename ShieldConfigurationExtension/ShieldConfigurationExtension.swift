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

    /// ミントの背景に、「◯◯を◯分使いました。…」、問題文、問題の画像（白い背景）を出す。
    /// ボタンの位置は iOS が決めるので、変えられない。
    private func make(name: String?) -> ShieldConfiguration {
        ShieldData.recordDiag("shieldConfig")
        let ink = UIColor(red: 0.137, green: 0.149, blue: 0.227, alpha: 1)        // #23263A
        let mint = UIColor(red: 0.498, green: 0.878, blue: 0.827, alpha: 1)       // #7FE0D3
        let gray = UIColor(red: 0.890, green: 0.906, blue: 0.949, alpha: 1)       // #E3E7F2

        let app = name ?? "アプリ"
        let minutes = ShieldData.pendingMinutes
        let intro = minutes > 0
            ? "\(app)を\(minutes)分使いました。問題を解いてロックを解除しましょう！"
            : "\(app)の使用時間になりました。問題を解いてロックを解除しましょう！"
        let problem = ShieldData.pendingBody ?? "解くロックを開いて問題を解いてください。"

        return ShieldConfiguration(
            backgroundBlurStyle: nil,
            backgroundColor: mint,
            icon: ShieldData.problemImage() ?? Self.blankIcon,      // LaTeX で描いた問題の画像（白い背景）
            title: ShieldConfiguration.Label(text: "問題", color: ink),
            subtitle: ShieldConfiguration.Label(text: "\(intro)\n\n\(problem)", color: ink),
            primaryButtonLabel: ShieldConfiguration.Label(text: "問題を解く", color: ink),
            primaryButtonBackgroundColor: gray,
            secondaryButtonLabel: nil
        )
    }

    /// 問題の画像がまだないときの、透明な画像（nil だと iOS 既定のアイコンが出る場合があるため）。
    private static let blankIcon: UIImage = UIGraphicsImageRenderer(size: CGSize(width: 1, height: 1)).image { _ in }
}
