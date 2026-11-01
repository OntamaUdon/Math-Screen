import SwiftUI

struct OnboardingView: View {
    @Environment(AppModel.self) private var model
    @State private var page = 0

    private let steps: [(icon: String, title: String, text: String)] = [
        ("function", "数学で、使いすぎを止める",
         "指定したアプリを使いすぎると、数学の問題が出ます。正解するまでそのアプリはお休みです。"),
        ("bell", "ブロック画面 → 通知 → 1問",
         "ブロック画面の「問題を解く」を押すと通知が届きます。タップして問題に正解すると再開できます。"),
        ("hourglass", "スクリーンタイムの許可",
         "利用時間を見守るために、スクリーンタイムと通知へのアクセスを許可してください。"),
    ]

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Spacer()
            let s = steps[page]
            Image(systemName: s.icon)
                .font(.system(size: 34, weight: .medium))
                .foregroundStyle(.white)
                .frame(width: 72, height: 72)
                .background(Slab(top: Theme.teal, side: Theme.tealDeep, depth: 7, radius: 14))
            Text(s.title).font(Theme.font(26, .bold)).foregroundStyle(Theme.ink)
            Text(s.text).font(Theme.font(16)).foregroundStyle(Theme.inkSoft)
                .lineSpacing(4)
                .fixedSize(horizontal: false, vertical: true)
            HStack(spacing: 6) {
                ForEach(0..<steps.count, id: \.self) { i in
                    Capsule().fill(i == page ? Theme.tealDeep : Theme.line)
                        .frame(width: i == page ? 20 : 8, height: 6)
                }
            }
            Spacer()

            if page < steps.count - 1 {
                Button("つぎへ") { withAnimation(.easeOut(duration: 0.2)) { page += 1 } }
                    .buttonStyle(.primary)
            } else {
                Button("許可してはじめる") {
                    Task {
                        await model.requestAuthorization()
                        model.finishOnboarding()
                    }
                }
                .buttonStyle(.primary)
                Button("あとで") { model.finishOnboarding() }
                    .font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
                    .frame(maxWidth: .infinity)
            }
        }
        .padding(.horizontal, 28)
        .padding(.bottom, 24)
        .isoBackground()
    }
}
