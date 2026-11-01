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
        let ink = UIColor(red: 0.137, green: 0.149, blue: 0.227, alpha: 1)        // #23263A
        let soft = UIColor(red: 0.420, green: 0.439, blue: 0.533, alpha: 1)       // #6B7088
        let teal = UIColor(red: 0.235, green: 0.773, blue: 0.710, alpha: 1)       // #3CC5B5
        let background = UIColor(red: 0.933, green: 0.945, blue: 0.969, alpha: 1) // #EEF1F7
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
            primaryButtonBackgroundColor: teal,
            secondaryButtonLabel: ShieldConfiguration.Label(text: "閉じる", color: soft)
        )
    }
}
