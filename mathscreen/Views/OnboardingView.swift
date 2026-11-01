import SwiftUI

struct OnboardingView: View {
    @Environment(AppModel.self) private var model
    @State private var page = 0

    private let steps: [(icon: String, color: Color, title: String, text: String)] = [
        ("function", Clay.lavender, "数学で、使いすぎを止める。",
         "指定したアプリを使いすぎると、数学の問題が出ます。正解するまでそのアプリはお休みです。"),
        ("bell.badge.fill", Clay.mint, "ブロック画面 → 通知 → 1問",
         "ブロック画面の「問題を解く」を押すと通知が届きます。タップして問題に正解すると再開できます。"),
        ("hourglass", Clay.peach, "スクリーンタイムの許可",
         "利用時間を見守るために、スクリーンタイムと通知へのアクセスを許可してください。"),
    ]

    var body: some View {
        ZStack {
            ClayBackdrop()
            VStack(spacing: 28) {
                Spacer()
                let s = steps[page]
                ZStack {
                    Circle().fill(s.color).frame(width: 150, height: 150)
                    Image(systemName: s.icon).font(.system(size: 58, weight: .semibold)).foregroundStyle(Clay.ink)
                }
                .clay(s.color, radius: 75, depth: 18)
                .id(page)
                .transition(.scale.combined(with: .opacity))

                VStack(spacing: 12) {
                    Text(s.title).font(Clay.font(26, .bold)).foregroundStyle(Clay.ink).multilineTextAlignment(.center)
                    Text(s.text).font(Clay.font(16)).foregroundStyle(Clay.inkSoft).multilineTextAlignment(.center)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(.horizontal, 12)

                HStack(spacing: 8) {
                    ForEach(0..<steps.count, id: \.self) { i in
                        Capsule().fill(i == page ? Clay.ink : Clay.inkFaint.opacity(0.5))
                            .frame(width: i == page ? 22 : 8, height: 8)
                    }
                }
                Spacer()

                if page < steps.count - 1 {
                    Button("つぎへ") { withAnimation(.spring) { page += 1 } }
                        .buttonStyle(.clay(Clay.lavender))
                } else {
                    Button("許可してはじめる") {
                        Task {
                            await model.requestAuthorization()
                            model.finishOnboarding()
                        }
                    }
                    .buttonStyle(.clay(Clay.mint))
                    Button("あとで") { model.finishOnboarding() }
                        .font(Clay.font(15, .semibold)).foregroundStyle(Clay.inkSoft)
                }
            }
            .padding(.horizontal, 28)
            .padding(.bottom, 30)
        }
    }
}
