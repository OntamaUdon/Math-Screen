import SwiftUI

/// プランを始めたあとに、1回だけ出す、保護者用設定の案内。パスコードを決めると、オンになる。
struct ParentSetupIntroView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var showSetup = false

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack {
                Text("保護者用設定").font(Theme.font(24, .bold)).foregroundStyle(Theme.ink)
                Spacer()
                Button("あとで") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
            }
            .padding(.top, 24)

            VStack(alignment: .leading, spacing: 12) {
                Label("お子さんが、勝手に変えられないようにします", systemImage: "lock.fill")
                    .font(Theme.font(16, .bold)).foregroundStyle(Theme.ink)
                Text("ルールの変更、設定、プランの管理に、パスコードが必要になります。お子さんが知らない4桁の数字を、決めてください。")
                    .font(Theme.font(14)).foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
                Text("あとから、設定の「保護者用設定」で、オン・オフを切りかえられます（オフにするにも、パスコードが必要です）。")
                    .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .card()

            Button("パスコードを決める") { showSetup = true }.buttonStyle(.primary)
            Button("あとで、設定でやる") { dismiss() }.buttonStyle(.quiet)
            Spacer()
        }
        .padding(.horizontal, 20)
        .isoBackground()
        .sheet(isPresented: $showSetup, onDismiss: { if ParentLock.shared.hasPasscode { dismiss() } }) {
            PasscodeSetupView().roomySheet()
        }
    }
}
