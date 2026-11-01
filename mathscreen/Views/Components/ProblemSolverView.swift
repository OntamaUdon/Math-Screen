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
    @State private var wrongShake = 0
    @State private var showWrong = false

    var body: some View {
        VStack(spacing: 20) {
            problemCard
            if solved {
                resultCard.transition(.scale(scale: 0.9).combined(with: .opacity))
            } else {
                answerField
                NumberPad(text: $input, onSubmit: submit)
                if attempts >= 3, let onSkip {
                    Button("別の問題にする", action: onSkip)
                        .font(Clay.font(14, .semibold))
                        .foregroundStyle(Clay.inkSoft)
                }
            }
        }
        .animation(.spring(response: 0.4, dampingFraction: 0.75), value: solved)
        .sensoryFeedback(.success, trigger: solved)
        .sensoryFeedback(.error, trigger: wrongShake)
    }

    private var problemCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(spacing: 8) {
                ClayChip(text: problem.categoryInfo.label, color: problem.categoryInfo.color)
                ClayChip(text: "\(problem.difficultyInfo.label) \(problem.difficultyInfo.dots)", color: Clay.butter)
                Spacer()
            }
            Text(problem.title)
                .font(Clay.font(15, .semibold))
                .foregroundStyle(Clay.inkSoft)
            Text(problem.body)
                .font(Clay.font(20, .medium))
                .foregroundStyle(Clay.ink)
                .lineSpacing(6)
                .fixedSize(horizontal: false, vertical: true)
            Text("答えは整数で入力してください")
                .font(Clay.font(12))
                .foregroundStyle(Clay.inkFaint)
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .clay()
    }

    private var answerField: some View {
        HStack {
            Text(input.isEmpty ? "?" : input.replacingOccurrences(of: "-", with: "−"))
                .font(Clay.font(34, .bold))
                .foregroundStyle(input.isEmpty ? Clay.inkFaint : Clay.ink)
                .contentTransition(.numericText())
            Spacer()
            if showWrong {
                Label("ちがうみたい", systemImage: "xmark")
                    .font(Clay.font(14, .semibold))
                    .foregroundStyle(Clay.peachDeep)
                    .transition(.opacity)
            }
        }
        .padding(.horizontal, 22)
        .frame(height: 72)
        .clayWell(radius: 22)
        .modifier(Shake(animatableData: CGFloat(wrongShake)))
    }

    private var resultCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(spacing: 10) {
                Image(systemName: "checkmark.seal.fill").font(.system(size: 28)).foregroundStyle(Clay.mintDeep)
                Text("正解！ 答えは \(problem.answer)")
                    .font(Clay.font(22, .bold)).foregroundStyle(Clay.ink)
            }
            Text("解説").font(Clay.font(13, .semibold)).foregroundStyle(Clay.inkSoft)
            Text(problem.explanation)
                .font(Clay.font(16))
                .foregroundStyle(Clay.ink)
                .lineSpacing(5)
                .fixedSize(horizontal: false, vertical: true)
            Button(continueLabel, action: onContinue)
                .buttonStyle(.clay(Clay.mint))
                .padding(.top, 6)
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .clay(Clay.surface)
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
            withAnimation(.default) { wrongShake += 1; showWrong = true }
            input = ""
        }
    }
}

struct Shake: GeometryEffect {
    var animatableData: CGFloat
    func effectValue(size: CGSize) -> ProjectionTransform {
        ProjectionTransform(CGAffineTransform(translationX: 10 * sin(animatableData * .pi * 4), y: 0))
    }
}
