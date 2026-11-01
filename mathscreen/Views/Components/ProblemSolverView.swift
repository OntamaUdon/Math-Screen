import SwiftUI

/// 1問を解く部品。ロック解除・練習の両方で使う。
struct ProblemSolverView: View {
    let problem: Problem
    /// 正解したとき（何回目で正解したか）
    var onCorrect: (_ attempts: Int) -> Void
    /// 「別の問題にする」
    var onSkip: (() -> Void)? = nil
    /// 正解後のボタン
    var continueLabel: String
    var onContinue: () -> Void

    @Environment(AppModel.self) private var model
    @State private var input = ""
    @State private var attempts = 0
    @State private var solved = false
    @State private var wrongCount = 0
    @State private var showWrong = false

    var body: some View {
        VStack(spacing: 16) {
            problemCard
            if solved {
                resultCard.transition(.opacity)
            } else {
                answerField
                NumberPad(text: $input, onSubmit: submit)
                if attempts >= 3, let onSkip {
                    Button("別の問題にする", action: onSkip)
                        .font(Theme.font(14, .semibold))
                        .foregroundStyle(Theme.inkSoft)
                }
            }
        }
        .animation(.easeOut(duration: 0.2), value: solved)
        .sensoryFeedback(.success, trigger: solved)
        .sensoryFeedback(.error, trigger: wrongCount)
    }

    private var problemCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("\(problem.categoryInfo.label) ・ \(problem.difficultyInfo.label) ・ \(problem.title)")
                .font(Theme.font(13, .semibold))
                .foregroundStyle(Theme.inkSoft)
            Text(problem.body)
                .font(Theme.font(19, .medium))
                .foregroundStyle(Theme.ink)
                .lineSpacing(6)
                .fixedSize(horizontal: false, vertical: true)
            Text("答えは整数で入力")
                .font(Theme.font(12))
                .foregroundStyle(Theme.inkFaint)
        }
        .card()
    }

    private var answerField: some View {
        HStack {
            Text(input.isEmpty ? "?" : input.replacingOccurrences(of: "-", with: "−"))
                .font(Theme.font(32, .bold))
                .foregroundStyle(input.isEmpty ? Theme.inkFaint : Theme.ink)
            Spacer()
            if showWrong {
                Text("不正解")
                    .font(Theme.font(14, .semibold))
                    .foregroundStyle(Theme.danger)
            }
        }
        .padding(.horizontal, 20)
        .frame(height: 68)
        .well()
        .overlay(RoundedRectangle(cornerRadius: 12, style: .continuous)
            .stroke(showWrong ? Theme.danger : .clear, lineWidth: 1.5))
        .modifier(Shake(animatableData: CGFloat(wrongCount)))
    }

    private var resultCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("正解　答えは \(problem.answer)", systemImage: "checkmark.circle.fill")
                .font(Theme.font(20, .bold))
                .foregroundStyle(Theme.mintDeep)
            SectionLabel("解説")
            Text(problem.explanation)
                .font(Theme.font(16))
                .foregroundStyle(Theme.ink)
                .lineSpacing(5)
                .fixedSize(horizontal: false, vertical: true)
            Button(continueLabel, action: onContinue)
                .buttonStyle(.primary)
                .padding(.top, 6)
        }
        .card()
    }

    private func submit() {
        guard let value = Int(input) else { return }
        attempts += 1
        let correct = value == problem.answer
        model.recordAnswer(correct: correct)
        if correct {
            solved = true
            onCorrect(attempts)
        } else {
            withAnimation(.default) { wrongCount += 1 }
            showWrong = true
            input = ""
        }
    }
}

struct Shake: GeometryEffect {
    var animatableData: CGFloat
    func effectValue(size: CGSize) -> ProjectionTransform {
        ProjectionTransform(CGAffineTransform(translationX: 8 * sin(animatableData * .pi * 4), y: 0))
    }
}
