import SwiftUI

/// ロック解除のための問題画面（通知タップで開く）。
struct ChallengeView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State private var problem: Problem?
    @State private var solvedCount = 0
    @State private var confirmEmergency = false

    var body: some View {
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
                        continueLabel: solvedCount >= model.requiredCorrect ? "解除してアプリに戻る" : "次の問題へ",
                        onContinue: {
                            if solvedCount >= model.requiredCorrect {
                                model.completeChallenge()
                                dismiss()
                            } else {
                                next()
                            }
                        }
                    )
                    .id(problem.id)

                    Button("緊急解除") { confirmEmergency = true }
                        .font(Theme.font(13, .semibold))
                        .foregroundStyle(Theme.inkFaint)
                        .frame(maxWidth: .infinity)
                        .padding(.top, 4)
                }
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 32)
        }
        .scrollIndicators(.hidden)
        .isoBackground()
        .onAppear { if problem == nil { next() } }
        .alert("緊急解除しますか？", isPresented: $confirmEmergency) {
            Button("緊急解除する", role: .destructive) {
                model.emergencyUnlock()
                dismiss()
            }
            Button("緊急解除しない", role: .cancel) {}
        } message: {
            Text("問題を解かずにすべての制限を外します。記録には「緊急解除」として残ります。")
        }
    }

    private var header: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 4) {
                Text("\(model.requiredCorrect)問解いて再開").font(Theme.font(24, .bold)).foregroundStyle(Theme.ink)
                if model.isLocked {
                    Text("正解 \(solvedCount) / \(model.requiredCorrect)")
                        .font(Theme.font(14)).foregroundStyle(Theme.inkSoft)
                }
            }
            Spacer()
            Button { dismiss() } label: {
                Image(systemName: "xmark").font(.system(size: 14, weight: .semibold)).foregroundStyle(Theme.inkSoft)
                    .frame(width: 36, height: 36)
                    .background(Theme.sunken, in: Circle())
            }
            .accessibilityLabel("閉じる")
        }
        .padding(.top, 20)
    }

    private var notLockedCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("いまは制限されていません").font(Theme.font(17, .semibold)).foregroundStyle(Theme.ink)
            Button("閉じる") { dismiss() }.buttonStyle(.secondary)
        }
        .card()
    }

    private func next() {
        // 最初の1問は、ブロック画面に表示していた問題
        if problem == nil, solvedCount == 0, let pending = model.pendingProblem {
            problem = pending
            return
        }
        problem = Adaptive.pick(categories: model.challengeCategories, units: model.challengeUnits, community: model.challengeCommunity, excluding: problem?.id)
    }
}
