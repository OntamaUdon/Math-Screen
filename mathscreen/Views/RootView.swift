import SwiftUI

struct RootView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        @Bindable var model = model
        Group {
            if model.hasOnboarded {
                MainTabView()
            } else {
                OnboardingView()
            }
        }
        .fullScreenCover(isPresented: $model.showChallenge) {
            ChallengeView()
        }
        .alert("エラー", isPresented: Binding(get: { model.lastError != nil }, set: { if !$0 { model.lastError = nil } })) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(model.lastError ?? "")
        }
    }
}

struct MainTabView: View {
    var body: some View {
        TabView {
            HomeView().tabItem { Label("ホーム", systemImage: "house") }
            PracticeView().tabItem { Label("練習", systemImage: "pencil") }
            StatsView().tabItem { Label("記録", systemImage: "chart.bar") }
            SettingsView().tabItem { Label("設定", systemImage: "gearshape") }
        }
        .tint(Theme.mintDeep)
    }
}

/// 画面共通のスクロール + タイトル。
struct Screen<Content: View>: View {
    var title: String
    var subtitle: String? = nil
    @ViewBuilder var content: Content

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(title).font(Theme.font(28, .bold)).foregroundStyle(Theme.ink)
                    if let subtitle {
                        Text(subtitle).font(Theme.font(14)).foregroundStyle(Theme.inkSoft)
                    }
                }
                .padding(.top, 12)
                content
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 32)
        }
        .scrollIndicators(.hidden)
        .background(Theme.background)
    }
}
