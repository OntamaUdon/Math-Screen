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
        // 「暗くて読めない」原因を調べるため、この画面が作られたときの外観（ライト／ダーク）を残す。設定の「診断」で見られる。
        ShieldData.recordNote("shieldStyle", Self.styleName(UITraitCollection.current.userInterfaceStyle))

        let app = name ?? "アプリ"
        let minutes = ShieldData.pendingMinutes
        let intro = minutes > 0
            ? "\(app)を\(Self.durationText(minutes))使いました。\n「問題を解く」を押すと通知が届きます。通知をタップしてアプリを開いてください！\n（通知がオフのときは、解くロックのアプリを直接開いてください）"
            : "\(app)の使用時間になりました。\n「問題を解く」を押すと通知が届きます。通知をタップしてアプリを開いてください！\n（通知がオフのときは、解くロックのアプリを直接開いてください）"

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

    private static func styleName(_ s: UIUserInterfaceStyle) -> String {
        switch s {
        case .dark: "ダーク"
        case .light: "ライト"
        default: "不明"
        }
    }

    private static func durationText(_ minutes: Int) -> String {
        let h = minutes / 60, m = minutes % 60
        if h == 0 { return "\(m)分" }
        return m == 0 ? "\(h)時間" : "\(h)時間\(m)分"
    }
}
