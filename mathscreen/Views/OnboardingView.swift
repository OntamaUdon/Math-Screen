import SwiftUI

/// はじめの説明（3画面）。設定の「使い方を見る」から、あとで見直せる（replay = true）。
struct OnboardingView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    var replay = false
    @State private var page = 0

    private let lastPage = 2
    private let exampleIDs = ["j06", "b07"]     // 例題として見せる問題（中学・高校）

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            header
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    switch page {
                    case 0: intro
                    case 1: howToSolve
                    default: permission
                    }
                }
                .padding(.bottom, 12)
            }
            .scrollIndicators(.hidden)
            dots
            buttons
        }
        .padding(.horizontal, 24)
        .padding(.bottom, 20)
        .isoBackground()
        .gesture(DragGesture(minimumDistance: 30).onEnded { v in      // 左右にスワイプしても進める・戻れる
            if v.translation.width < -50, page < lastPage { go(page + 1) }
            if v.translation.width > 50, page > 0 { go(page - 1) }
        })
    }

    // MARK: 上の行（もどる・とじる）
    private var header: some View {
        HStack {
            if page > 0 {
                Button { go(page - 1) } label: {
                    Label("もどる", systemImage: "chevron.left")
                        .font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
                }
            }
            Spacer()
            if replay {
                Button("とじる") { dismiss() }
                    .font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
            }
        }
        .frame(height: 32)
        .padding(.top, 8)
    }

    // MARK: 1. はじめに（例題つき）
    private var intro: some View {
        VStack(alignment: .leading, spacing: 16) {
            icon("questionmark")
            Text("考えて、使いすぎを止める。").font(Theme.font(26, .bold)).foregroundStyle(Theme.ink)
            Text("決めた時間だけアプリを使うと、問題が出ます。正解するまで、そのアプリはお休みです。")
                .font(Theme.font(16)).foregroundStyle(Theme.inkSoft).lineSpacing(4)
                .fixedSize(horizontal: false, vertical: true)

            SectionLabel("例題")
            ForEach(exampleIDs, id: \.self) { id in
                if let p = ProblemBank.all.first(where: { $0.id == id }) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("\(p.categoryInfo.label) ・ \(p.difficultyInfo.label)")
                            .font(Theme.font(12, .semibold)).foregroundStyle(Theme.inkSoft)
                        MathText(source: p.body, fontSize: 16, spoken: p.plain)
                        Text("答え：\(p.answer)").font(Theme.font(13, .semibold)).foregroundStyle(Theme.tealDeep)
                    }
                    .card(padding: 14)
                }
            }
            Text("数学のほか、英語・社会・理科の問題も出せます。出題する問題は、ルールごとに選べます。")
                .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
        }
    }

    // MARK: 2. 解くときの手順（図）
    private var howToSolve: some View {
        VStack(alignment: .leading, spacing: 16) {
            icon("bell")
            Text("問題を解く手順").font(Theme.font(26, .bold)).foregroundStyle(Theme.ink)
            SolveFlowDiagram()
            Text("iOS の仕組みで、ブロック画面からアプリを直接開けないため、通知を使います。")
                .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    // MARK: 3. 許可
    private var permission: some View {
        VStack(alignment: .leading, spacing: 16) {
            icon("hourglass")
            Text("スクリーンタイムの許可").font(Theme.font(26, .bold)).foregroundStyle(Theme.ink)
            Text("使用時間を見守るために、スクリーンタイムと通知へのアクセスを許可してください。")
                .font(Theme.font(16)).foregroundStyle(Theme.inkSoft).lineSpacing(4)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private func icon(_ name: String) -> some View {
        Image(systemName: name)
            .font(.system(size: 30, weight: .medium))
            .foregroundStyle(.white)
            .frame(width: 64, height: 64)
            .background(Slab(top: Theme.teal, side: Theme.tealDeep, depth: 6, radius: 12))
            .padding(.bottom, 6)
    }

    private var dots: some View {
        HStack(spacing: 6) {
            ForEach(0...lastPage, id: \.self) { i in
                Capsule().fill(i == page ? Theme.tealDeep : Theme.line)
                    .frame(width: i == page ? 20 : 8, height: 6)
            }
        }
        .frame(maxWidth: .infinity)
    }

    // MARK: 下のボタン
    @ViewBuilder private var buttons: some View {
        if page < lastPage {
            Button("つぎへ") { go(page + 1) }.buttonStyle(.primary)
        } else if replay {
            Button("とじる") { dismiss() }.buttonStyle(.primary)
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

    private func go(_ p: Int) { withAnimation(.easeOut(duration: 0.2)) { page = p } }
}

/// 解くときの手順：ブロック画面 → 通知 → 問題 → 再開。
struct SolveFlowDiagram: View {
    private let steps: [(icon: String, title: String, detail: String)] = [
        ("lock.fill", "ブロック画面が出る", "「問題を解く」ボタンを押す"),
        ("bell.fill", "通知が届く", "通知をタップして、解くロックを開く"),
        ("pencil", "問題に答える", "整数を入力して「こたえる」"),
        ("checkmark", "正解すると再開", "アプリがまた使えるようになる"),
    ]

    var body: some View {
        VStack(spacing: 0) {
            ForEach(Array(steps.enumerated()), id: \.offset) { i, s in
                HStack(spacing: 14) {
                    ZStack {
                        Slab(top: i == steps.count - 1 ? Theme.coral : Theme.teal,
                             side: i == steps.count - 1 ? Theme.coralDeep : Theme.tealDeep, depth: 5, radius: 10)
                        Image(systemName: s.icon).font(.system(size: 20, weight: .semibold)).foregroundStyle(.white)
                    }
                    .frame(width: 52, height: 52)
                    .padding(.trailing, 5).padding(.bottom, 5)
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\(i + 1)　\(s.title)").font(Theme.font(16, .bold)).foregroundStyle(Theme.ink)
                        Text(s.detail).font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                    }
                    Spacer(minLength: 0)
                }
                if i < steps.count - 1 {
                    Image(systemName: "arrow.down")
                        .font(.system(size: 14, weight: .bold)).foregroundStyle(Theme.inkFaint)
                        .frame(width: 52).padding(.vertical, 4)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
        }
        .card(padding: 16)
    }
}
