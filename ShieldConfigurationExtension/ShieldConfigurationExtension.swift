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

    private func make(name: String?) -> ShieldConfiguration {
        let ink = UIColor(red: 0.149, green: 0.149, blue: 0.165, alpha: 1)       // #26262A
        let soft = UIColor(red: 0.431, green: 0.431, blue: 0.455, alpha: 1)      // #6E6E74
        let mintDeep = UIColor(red: 0.247, green: 0.561, blue: 0.431, alpha: 1)  // #3F8F6E
        let background = UIColor(red: 0.953, green: 0.953, blue: 0.945, alpha: 1) // #F3F3F1
        let target = name ?? "このアプリ"

        return ShieldConfiguration(
            backgroundBlurStyle: .systemUltraThinMaterialLight,
            backgroundColor: background,
            icon: UIImage(systemName: "function"),
            title: ShieldConfiguration.Label(text: "1問解いて再開", color: ink),
            subtitle: ShieldConfiguration.Label(
                text: "\(target) の利用時間が上限に達しました。\n「問題を解く」→ 届いた通知をタップ → 正解で再開できます。",
                color: soft
            ),
            primaryButtonLabel: ShieldConfiguration.Label(text: "問題を解く", color: .white),
            primaryButtonBackgroundColor: mintDeep,
            secondaryButtonLabel: ShieldConfiguration.Label(text: "閉じる", color: soft)
        )
    }
}
