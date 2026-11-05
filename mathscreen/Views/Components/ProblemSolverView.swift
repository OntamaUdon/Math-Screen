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
    @State private var eliminated: Set<Int> = []      // 4択で、まちがえて消した選択肢
    @State private var picked: Int?                   // 4択で、いま選んでいる選択肢

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
                helpButtons
            }
        }
        .animation(.easeOut(duration: 0.2), value: solved)
        .sensoryFeedback(.success, trigger: solved)
        .sensoryFeedback(.error, trigger: wrongCount)
    }

    // MARK: 問題の変更（Premium）
    @ViewBuilder private var helpButtons: some View {
        if let onSkip {
            Button {
                if model.isPremium {
                    ProblemMarkStore.shared.record(problem.id, .skipped)        // 解かずに変えた印（すでに解いた問題には影響しない）
                    onSkip()
                } else { model.showPlan = true }
            } label: {
                HStack(spacing: 6) {
                    Image(systemName: "arrow.triangle.2.circlepath")
                    Text("別の問題")
                    if !model.isPremium { Image(systemName: "lock.fill").font(.system(size: 11)) }
                }
                .font(Theme.font(15, .semibold))
            }
            .buttonStyle(.quiet)
        }
    }

    private var problemCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("\(problem.categoryInfo.label) ・ \(problem.title)")
                .font(Theme.font(13, .semibold))
                .foregroundStyle(Theme.inkSoft)
            MathText(source: problem.body, fontSize: 19, spoken: problem.plain)
            Text(problem.isChoice ? "正しいものを選んで「こたえる」を押す" : "答えを入力して「こたえる」を押す")
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

    /// 4択：選択肢を選んで、「こたえる」を押す。まちがえた選択肢は薄くなる。
    private func choiceList(_ choices: [String]) -> some View {
        VStack(spacing: 10) {
            ForEach(Array(choices.enumerated()), id: \.offset) { i, c in
                Button { picked = i } label: {
                    HStack(spacing: 12) {
                        if picked == i {
                            Image(systemName: "checkmark.circle.fill").font(.system(size: 20)).foregroundStyle(Theme.tealDeep)
                        } else {
                            Text(Problem.choiceMarks[i]).font(Theme.font(18, .bold)).foregroundStyle(Theme.tealDeep)
                        }
                        MathText(source: c, fontSize: 17)
                        Spacer(minLength: 0)
                    }
                    .padding(.horizontal, 14)
                }
                .buttonStyle(IsoButtonStyle(kind: .secondary))
                .overlay(RoundedRectangle(cornerRadius: 12, style: .continuous).stroke(picked == i ? Theme.tealDeep : .clear, lineWidth: 2.5))
                .disabled(eliminated.contains(i))
                .opacity(eliminated.contains(i) ? 0.4 : 1)
            }
            if showWrong {
                Text("ちがうみたい。もう一度選んでください。")
                    .font(Theme.font(14, .semibold)).foregroundStyle(Theme.danger)
            }
            Button("こたえる") { if let i = picked { submitChoice(i) } }
                .buttonStyle(.primary)
                .disabled(picked == nil)
                .opacity(picked == nil ? 0.5 : 1)
                .padding(.top, 4)
        }
    }

    private func submitChoice(_ i: Int) {
        attempts += 1
        let correct = i == problem.answer
        model.recordAnswer(correct: correct)
        if attempts == 1 { MasteryStore.shared.record(problem, firstTryCorrect: correct); let id = problem.id; Task { await Community.shared.recordFirstAttempt(id, correct: correct) } }
        if correct {
            solved = true
            ProblemMarkStore.shared.record(problem.id, .solved(wrongCount: attempts - 1))
            onCorrect(attempts)
        } else {
            eliminated.insert(i)
            picked = nil
            withAnimation(.default) { wrongCount += 1 }
            showWrong = true
        }
    }

    private func submit() {
        guard let value = Int(input) else { return }
        attempts += 1
        let correct = value == problem.answer
        model.recordAnswer(correct: correct)
        if attempts == 1 { MasteryStore.shared.record(problem, firstTryCorrect: correct); let id = problem.id; Task { await Community.shared.recordFirstAttempt(id, correct: correct) } }
        if correct {
            solved = true
            ProblemMarkStore.shared.record(problem.id, .solved(wrongCount: attempts - 1))
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
