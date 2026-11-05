import SwiftUI
import UserNotifications

@main
struct MathScreenApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @Environment(\.scenePhase) private var scenePhase
    @State private var model = AppModel.shared

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(model)
                .preferredColorScheme(.light)
                .task { Purchases.shared.start() }
                .onOpenURL { url in
                    if url.absoluteString.hasPrefix("mathscreen://challenge") { model.showChallenge = true }
                }
        }
        .onChange(of: scenePhase) { _, phase in
            if phase == .active { model.refresh() }
        }
    }
}

final class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate {
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        UNUserNotificationCenter.current().delegate = self
        // 問題データ（約7MB）の読み込みを、画面を出しながら裏で始める
        Task.detached(priority: .utility) {
            _ = ProblemBank.all
            _ = UnitCatalog.problemCount
            _ = UnitCatalog.categories
        }
        return true
    }

    /// 通知をタップ → 問題画面を開く。
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                didReceive response: UNNotificationResponse) async {
        await MainActor.run {
            AppModel.shared.refresh()
            AppModel.shared.showChallenge = true
        }
    }

    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                willPresent notification: UNNotification) async -> UNNotificationPresentationOptions {
        [.banner, .sound]
    }
}
