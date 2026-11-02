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
    @State private var eliminated: Set<Int> = []      // 4択で、消した選択肢（まちがえた・ヒントで消した）
    @State private var showHint = false
    @State private var showPremiumAlert = false

    var body: some View {
        VStack(spacing: 16) {
            problemCard
            if solved {
                resultCard.transition(.opacity)
            } else {
                if let choices = problem.choices {
                    choiceList(choices)
                } else {
                    answerField
                    NumberPad(text: $input, onSubmit: submit)
                }
                if showHint { hintCard }
                helpButtons
            }
        }
        .animation(.easeOut(duration: 0.2), value: solved)
        .sensoryFeedback(.success, trigger: solved)
        .sensoryFeedback(.error, trigger: wrongCount)
        .alert("Premium の機能です", isPresented: $showPremiumAlert) {
            Button("仮登録する（0円）") { model.setPremium(true) }
            Button("やめる", role: .cancel) {}
        } message: {
            Text("ヒントと問題の変更は、Premium で使えます。いまは、お金のかからない仮登録で試せます。")
        }
    }

    // MARK: ヒントと問題の変更（Premium）
    private var helpButtons: some View {
        HStack(spacing: 10) {
            helpButton("ヒント", icon: "lightbulb") {
                if model.isPremium { revealHint() } else { showPremiumAlert = true }
            }
            if let onSkip {
                helpButton("別の問題", icon: "arrow.triangle.2.circlepath") {
                    if model.isPremium { onSkip() } else { showPremiumAlert = true }
                }
            }
        }
    }

    private func helpButton(_ title: String, icon: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                Text(title)
                if !model.isPremium { Image(systemName: "lock.fill").font(.system(size: 11)) }
            }
            .font(Theme.font(15, .semibold))
        }
        .buttonStyle(.quiet)
    }

    private var hintCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("ヒント", systemImage: "lightbulb.fill")
                .font(Theme.font(13, .bold)).foregroundStyle(Theme.coralDeep)
            MathText(source: problem.hint ?? "問題文の数字や条件を、式に書き出してみましょう。", fontSize: 15)
            if problem.isChoice {
                Text("まちがいの選択肢を、2つ消しました。").font(Theme.font(12)).foregroundStyle(Theme.inkSoft)
            }
        }
        .card(padding: 14)
    }

    /// ヒントを出す。4択なら、まちがいの選択肢を2つ消す。
    private func revealHint() {
        showHint = true
        guard problem.isChoice else { return }
        let wrong = (0..<4).filter { $0 != problem.answer && !eliminated.contains($0) }
        withAnimation { eliminated.formUnion(wrong.prefix(2)) }
    }

    private var problemCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("\(problem.categoryInfo.label) ・ \(problem.difficultyInfo.label) ・ \(problem.title)")
                .font(Theme.font(13, .semibold))
                .foregroundStyle(Theme.inkSoft)
            MathText(source: problem.body, fontSize: 19, spoken: problem.plain)
            Text(problem.isChoice ? "正しいものを1つ選ぶ" : "答えは整数で入力")
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
            Label("正解　答えは \(problem.answerText)", systemImage: "checkmark.circle.fill")
                .font(Theme.font(20, .bold))
                .foregroundStyle(Theme.tealDeep)
            SectionLabel("解説")
            MathText(source: problem.explanation, fontSize: 16)
            Button(continueLabel, action: onContinue)
                .buttonStyle(.primary)
                .padding(.top, 6)
        }
        .card()
    }

    /// 4択：押した選択肢が、そのまま答えになる。まちがえた選択肢は薄くなる。
    private func choiceList(_ choices: [String]) -> some View {
        VStack(spacing: 10) {
            ForEach(Array(choices.enumerated()), id: \.offset) { i, c in
                Button { submitChoice(i) } label: {
                    HStack(spacing: 12) {
                        Text(Problem.choiceMarks[i]).font(Theme.font(18, .bold)).foregroundStyle(Theme.tealDeep)
                        MathText(source: c, fontSize: 17)
                        Spacer(minLength: 0)
                    }
                    .padding(.horizontal, 14)
                }
                .buttonStyle(IsoButtonStyle(kind: .secondary))
                .disabled(eliminated.contains(i))
                .opacity(eliminated.contains(i) ? 0.4 : 1)
            }
            if showWrong {
                Text("ちがうみたい。もう一度選んでください。")
                    .font(Theme.font(14, .semibold)).foregroundStyle(Theme.danger)
            }
        }
    }

    private func submitChoice(_ i: Int) {
        attempts += 1
        let correct = i == problem.answer
        model.recordAnswer(correct: correct)
        if correct {
            solved = true
            onCorrect(attempts)
        } else {
            eliminated.insert(i)
            withAnimation(.default) { wrongCount += 1 }
            showWrong = true
        }
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
