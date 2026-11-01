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
        let ink = UIColor(red: 0.18, green: 0.18, blue: 0.20, alpha: 1)
        let soft = UIColor(red: 0.46, green: 0.45, blue: 0.49, alpha: 1)
        let lavender = UIColor(red: 0.62, green: 0.57, blue: 0.84, alpha: 1)
        let background = UIColor(red: 0.914, green: 0.906, blue: 0.890, alpha: 1)
        let target = name ?? "このアプリ"

        return ShieldConfiguration(
            backgroundBlurStyle: .systemUltraThinMaterialLight,
            backgroundColor: background,
            icon: UIImage(systemName: "function"),
            title: ShieldConfiguration.Label(text: "ひと休み、1問だけ。", color: ink),
            subtitle: ShieldConfiguration.Label(
                text: "\(target) の利用時間が上限に達しました。\n「問題を解く」→ 届いた通知をタップ → 正解で再開できます。",
                color: soft
            ),
            primaryButtonLabel: ShieldConfiguration.Label(text: "問題を解く", color: .white),
            primaryButtonBackgroundColor: lavender,
            secondaryButtonLabel: ShieldConfiguration.Label(text: "閉じる", color: soft)
        )
    }
}
