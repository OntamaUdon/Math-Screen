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
        // iPhone がダークのときは、ブロック画面の背景が暗くなる。そのとき文字も白くなるように、ライト用とダーク用を持たせる。
        func pair(light: UInt32, dark: UInt32) -> UIColor {
            UIColor { $0.userInterfaceStyle == .dark ? Self.color(dark) : Self.color(light) }
        }
        let ink = pair(light: 0x23263A, dark: 0xFFFFFF)          // 文字
        let mint = pair(light: 0x7FE0D3, dark: 0x1B2B28)         // 背景
        let gray = pair(light: 0xE3E7F2, dark: 0x3C4F4B)         // ボタンの背景
        // 「暗くて読めない」原因を調べるため、この画面が作られたときの外観（ライト／ダーク）を残す。設定の「診断」で見られる。
        ShieldData.recordNote("shieldStyle", Self.styleName(UITraitCollection.current.userInterfaceStyle))

        let app = name ?? "アプリ"
        let minutes = ShieldData.pendingMinutes
        let intro = minutes > 0
            ? "\(app)を\(Self.durationText(minutes))使いました。\nアプリに表示された問題を解いて制限を解除しましょう"
            : "\(app)の使用時間になりました。\nアプリに表示された問題を解いて制限を解除しましょう"

        return ShieldConfiguration(
            backgroundBlurStyle: nil,
            backgroundColor: mint,
            icon: ShieldArt.lockIcon,
            title: ShieldConfiguration.Label(text: "ロック中", color: ink),
            subtitle: ShieldConfiguration.Label(text: intro, color: ink),
            primaryButtonLabel: ShieldConfiguration.Label(text: "通知を送る", color: ink),
            primaryButtonBackgroundColor: gray,
            secondaryButtonLabel: nil
        )
    }

    private static func color(_ hex: UInt32) -> UIColor {
        UIColor(red: CGFloat((hex >> 16) & 0xFF) / 255, green: CGFloat((hex >> 8) & 0xFF) / 255,
                blue: CGFloat(hex & 0xFF) / 255, alpha: 1)
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
