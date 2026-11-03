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

    /// ミントの背景に「◯◯を◯分使いました。…」だけを出す。問題は本体アプリで表示する（ボタン → 通知 → アプリ）。
    /// ボタンの位置は iOS が決めるので、変えられない。
    private func make(name: String?) -> ShieldConfiguration {
        ShieldData.recordDiag("shieldConfig")
        let ink = UIColor(red: 0.137, green: 0.149, blue: 0.227, alpha: 1)        // #23263A
        let mint = UIColor(red: 0.498, green: 0.878, blue: 0.827, alpha: 1)       // #7FE0D3
        let gray = UIColor(red: 0.890, green: 0.906, blue: 0.949, alpha: 1)       // #E3E7F2

        let app = name ?? "アプリ"
        let minutes = ShieldData.pendingMinutes
        let intro = minutes > 0
            ? "\(app)を\(Self.durationText(minutes))使いました。\n下の「問題を解く」を押すと通知が届きます。その通知をタップして、問題に答えてください！"
            : "\(app)の使用時間になりました。\n下の「問題を解く」を押すと通知が届きます。その通知をタップして、問題に答えてください！"

        return ShieldConfiguration(
            backgroundBlurStyle: nil,
            backgroundColor: mint,
            icon: ShieldArt.lockIcon,
            title: ShieldConfiguration.Label(text: "ロック中", color: ink),
            subtitle: ShieldConfiguration.Label(text: intro, color: ink),
            primaryButtonLabel: ShieldConfiguration.Label(text: "問題を解く", color: ink),
            primaryButtonBackgroundColor: gray,
            secondaryButtonLabel: nil
        )
    }

    private static func durationText(_ minutes: Int) -> String {
        let h = minutes / 60, m = minutes % 60
        if h == 0 { return "\(m)分" }
        return m == 0 ? "\(h)時間" : "\(h)時間\(m)分"
    }
}
