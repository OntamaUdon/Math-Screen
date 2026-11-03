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
        // ライトでもダークでも読めるように、外観に合わせて色を切りかえる。
        func dyn(light: UIColor, dark: UIColor) -> UIColor {
            UIColor { $0.userInterfaceStyle == .dark ? dark : light }
        }
        func rgb(_ r: CGFloat, _ g: CGFloat, _ b: CGFloat) -> UIColor { UIColor(red: r, green: g, blue: b, alpha: 1) }
        let ink = dyn(light: rgb(0.137, 0.149, 0.227), dark: rgb(0.96, 0.97, 0.99))        // 文字：#23263A ／ ほぼ白
        let mint = dyn(light: rgb(0.498, 0.878, 0.827), dark: rgb(0.10, 0.17, 0.20))       // 背景：ミント ／ 濃い紺
        let gray = dyn(light: rgb(0.890, 0.906, 0.949), dark: rgb(0.22, 0.30, 0.34))        // ボタン：薄いグレー ／ 暗いグレー

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

    private static func durationText(_ minutes: Int) -> String {
        let h = minutes / 60, m = minutes % 60
        if h == 0 { return "\(m)分" }
        return m == 0 ? "\(h)時間" : "\(h)時間\(m)分"
    }
}
