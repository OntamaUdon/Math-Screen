import SwiftUI

/// ロック解除のための問題画面（通知タップで開く）。
struct ChallengeView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State private var problem: Problem?
    @State private var solvedCount = 0
    @State private var confirmEmergency = false

    var body: some View {
        ZStack {
            ClayBackdrop()
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    header
                    if !model.isLocked {
                        notLockedCard
                    } else if let problem {
                        ProblemSolverView(
                            problem: problem,
                            onCorrect: { _ in solvedCount += 1 },
                            onSkip: { next() },
                            continueLabel: solvedCount >= model.settings.requiredCorrect ? "解除してアプリに戻る" : "次の問題へ",
                            onContinue: {
                                if solvedCount >= model.settings.requiredCorrect {
                                    model.completeChallenge()
                                    dismiss()
                                } else {
                                    next()
                                }
                            }
                        )
                        .id(problem.id)

                        Button("緊急解除") { confirmEmergency = true }
                            .font(Clay.font(13, .semibold))
                            .foregroundStyle(Clay.inkFaint)
                            .frame(maxWidth: .infinity)
                            .padding(.top, 8)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 40)
            }
            .scrollIndicators(.hidden)
        }
        .onAppear { if problem == nil { next() } }
        .confirmationDialog("緊急解除しますか？", isPresented: $confirmEmergency, titleVisibility: .visible) {
            Button("解除する", role: .destructive) {
                model.emergencyUnlock()
                dismiss()
            }
        } message: {
            Text("問題を解かずにすべての制限を外します。記録には「緊急解除」として残ります。")
        }
    }

    private var header: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 4) {
                Text("ひと休み、1問だけ。").font(Clay.font(26, .bold)).foregroundStyle(Clay.ink)
                if model.isLocked {
                    Text(lockedNames + " を再開するには正解してね")
                        .font(Clay.font(14)).foregroundStyle(Clay.inkSoft)
                    Text("正解 \(solvedCount) / \(model.settings.requiredCorrect)")
                        .font(Clay.font(13, .semibold)).foregroundStyle(Clay.lavenderDeep)
                        .padding(.top, 2)
                }
            }
            Spacer()
            Button { dismiss() } label: {
                Image(systemName: "xmark").font(.system(size: 15, weight: .bold)).foregroundStyle(Clay.inkSoft)
                    .frame(width: 40, height: 40)
                    .clay(Clay.surface, radius: 20, depth: 6)
            }
            .buttonStyle(.plain)
        }
        .padding(.top, 20)
    }

    private var lockedNames: String {
        let names = model.lockedRules.map(\.name)
        return names.isEmpty ? "アプリ" : names.joined(separator: "・")
    }

    private var notLockedCard: some View {
        VStack(spacing: 14) {
            Image(systemName: "lock.open.fill").font(.system(size: 34)).foregroundStyle(Clay.mintDeep)
            Text("いまは制限されていません").font(Clay.font(18, .semibold)).foregroundStyle(Clay.ink)
            Button("閉じる") { dismiss() }.buttonStyle(.clay(Clay.mint))
        }
        .padding(26)
        .frame(maxWidth: .infinity)
        .clay()
    }

    private func next() {
        let s = model.settings
        problem = ProblemBank.pick(categories: s.categories, difficulties: s.difficulties, excluding: problem?.id)
    }
}
