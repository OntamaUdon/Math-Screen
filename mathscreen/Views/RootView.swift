import SwiftUI

struct RootView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        @Bindable var model = model
        @Bindable var lock = ParentLock.shared
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
        .sheet(isPresented: $lock.showEntry) { PasscodeEntryView() }
        .sheet(isPresented: $model.showPlan) { PlanView().roomySheet() }
        .sheet(isPresented: $model.showParentSetup) { ParentSetupIntroView().roomySheet() }
        .onChange(of: model.showPlan) { _, shown in
            if !shown && model.parentSetupPending { model.parentSetupPending = false; model.showParentSetup = true }
        }
        .onChange(of: scenePhase) { _, phase in if phase != .active { ParentLock.shared.lock() } }
        .alert(model.alertTitle, isPresented: Binding(get: { model.lastError != nil }, set: { if !$0 { model.lastError = nil; model.alertTitle = "エラー" } })) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(model.lastError ?? "")
        }
    }
}

struct MainTabView: View {
    @State private var tab: Int
    init(initial: Int = 0) { _tab = State(initialValue: initial) }

    var body: some View {
        TabView(selection: $tab) {
            HomeView().tabItem { Label("ホーム", systemImage: "house") }.tag(0)
            ProblemBookView().tabItem { Label("問題集", systemImage: "books.vertical") }.tag(1)
            StatsView().tabItem { Label("記録", systemImage: "chart.bar") }.tag(2)
            SettingsView().tabItem { Label("設定", systemImage: "gearshape") }.tag(3)
        }
        .tint(Theme.tealDeep)
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
        .isoBackground()
    }
}
