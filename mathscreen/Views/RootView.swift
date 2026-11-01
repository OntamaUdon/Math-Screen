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

enum AppTab: String, CaseIterable, Identifiable {
    case home, practice, stats, settings
    var id: String { rawValue }

    var label: String {
        switch self {
        case .home: "ホーム"
        case .practice: "練習"
        case .stats: "記録"
        case .settings: "設定"
        }
    }

    var icon: String {
        switch self {
        case .home: "house.fill"
        case .practice: "pencil.and.outline"
        case .stats: "chart.bar.fill"
        case .settings: "slider.horizontal.3"
        }
    }

    var color: Color {
        switch self {
        case .home: Clay.lavender
        case .practice: Clay.mint
        case .stats: Clay.sky
        case .settings: Clay.peach
        }
    }
}

struct MainTabView: View {
    @State private var tab: AppTab = .home

    var body: some View {
        ZStack(alignment: .bottom) {
            ClayBackdrop()
            Group {
                switch tab {
                case .home: HomeView()
                case .practice: PracticeView()
                case .stats: StatsView()
                case .settings: SettingsView()
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)

            ClayTabBar(selection: $tab)
                .padding(.horizontal, 20)
                .padding(.bottom, 8)
        }
    }
}

struct ClayTabBar: View {
    @Binding var selection: AppTab

    var body: some View {
        HStack(spacing: 6) {
            ForEach(AppTab.allCases) { t in
                Button {
                    withAnimation(.spring(response: 0.35, dampingFraction: 0.7)) { selection = t }
                } label: {
                    VStack(spacing: 3) {
                        Image(systemName: t.icon).font(.system(size: 18, weight: .semibold))
                        Text(t.label).font(Clay.font(11, .semibold))
                    }
                    .foregroundStyle(selection == t ? Clay.ink : Clay.inkFaint)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background {
                        if selection == t {
                            Color.clear.clay(t.color, radius: 20, depth: 6)
                        }
                    }
                }
                .buttonStyle(.plain)
            }
        }
        .padding(8)
        .clay(Clay.surface, radius: 30, depth: 14)
    }
}

/// 画面共通のスクロール + タイトル。
struct ClayScreen<Content: View>: View {
    var title: String
    var subtitle: String? = nil
    @ViewBuilder var content: Content

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(title).font(Clay.font(30, .bold)).foregroundStyle(Clay.ink)
                    if let subtitle {
                        Text(subtitle).font(Clay.font(14)).foregroundStyle(Clay.inkSoft)
                    }
                }
                .padding(.top, 12)
                content
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 120)
        }
        .scrollIndicators(.hidden)
    }
}
