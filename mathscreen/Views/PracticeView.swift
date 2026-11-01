import SwiftUI

/// ロックとは関係なく、自由に問題を解く。
struct PracticeView: View {
    @State private var category: ProblemCategory? = nil
    @State private var difficulty: Difficulty? = nil
    @State private var problem: Problem?

    var body: some View {
        ClayScreen(title: "練習", subtitle: "\(ProblemBank.all.count) 問から自由に挑戦") {
            if let problem {
                ProblemSolverView(
                    problem: problem,
                    onCorrect: { _ in },
                    onSkip: { next() },
                    continueLabel: "次の問題へ",
                    onContinue: { next() }
                )
                .id(problem.id)
                Button("条件を変える") { withAnimation { self.problem = nil } }
                    .font(Clay.font(14, .semibold)).foregroundStyle(Clay.inkSoft)
                    .frame(maxWidth: .infinity)
            } else {
                filters
            }
        }
    }

    private var filters: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text("分野").font(Clay.font(14, .semibold)).foregroundStyle(Clay.inkSoft)
            FlowChips(items: [nil] + ProblemCategory.allCases.map { Optional($0) }, selection: $category,
                      label: { $0?.label ?? "すべて" }, color: { $0?.color ?? Clay.lavender })
            Text("難易度").font(Clay.font(14, .semibold)).foregroundStyle(Clay.inkSoft)
            FlowChips(items: [nil] + Difficulty.allCases.map { Optional($0) }, selection: $difficulty,
                      label: { $0?.label ?? "すべて" }, color: { _ in Clay.butter })
            Button {
                withAnimation { next() }
            } label: {
                Label("はじめる", systemImage: "play.fill")
            }
            .buttonStyle(.clay(Clay.mint))
            .padding(.top, 6)
        }
        .padding(20)
        .clay()
    }

    private func next() {
        let cats = category.map { Set([$0.rawValue]) } ?? Set(ProblemCategory.allCases.map(\.rawValue))
        let diffs = difficulty.map { Set([$0.rawValue]) } ?? Set(Difficulty.allCases.map(\.rawValue))
        problem = ProblemBank.pick(categories: cats, difficulties: diffs, excluding: problem?.id)
    }
}

/// 単一選択のチップ列。
struct FlowChips<T: Hashable>: View {
    var items: [T]
    @Binding var selection: T
    var label: (T) -> String
    var color: (T) -> Color

    var body: some View {
        LazyVGrid(columns: [GridItem(.adaptive(minimum: 92), spacing: 10)], alignment: .leading, spacing: 10) {
            ForEach(items, id: \.self) { item in
                Button {
                    withAnimation(.spring(response: 0.3)) { selection = item }
                } label: {
                    ClayChip(text: label(item), color: color(item), isOn: selection == item)
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.plain)
            }
        }
    }
}
