import SwiftUI

/// ロックとは関係なく、自由に問題を解く。
struct PracticeView: View {
    @State private var category: ProblemCategory? = nil
    @State private var difficulty: Difficulty? = nil
    @State private var problem: Problem?

    var body: some View {
        Screen(title: "練習", subtitle: "\(ProblemBank.all.count) 問から自由に挑戦") {
            if let problem {
                ProblemSolverView(
                    problem: problem,
                    onCorrect: { _ in },
                    onSkip: { next() },
                    continueLabel: "次の問題へ",
                    onContinue: { next() }
                )
                .id(problem.id)
                Button("条件を変える") { self.problem = nil }
                    .font(Theme.font(14, .semibold)).foregroundStyle(Theme.inkSoft)
                    .frame(maxWidth: .infinity)
            } else {
                filters
            }
        }
    }

    private var filters: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionLabel("分野")
            TagPicker(items: [nil] + ProblemCategory.allCases.map { Optional($0) }, selection: $category) { $0?.label ?? "すべて" }
            SectionLabel("難易度")
            TagPicker(items: [nil] + Difficulty.allCases.map { Optional($0) }, selection: $difficulty) { $0?.label ?? "すべて" }
            Button("はじめる") { next() }
                .buttonStyle(.primary)
                .padding(.top, 4)
        }
        .card()
    }

    private func next() {
        let cats = category.map { Set([$0.rawValue]) } ?? Set(ProblemCategory.allCases.map(\.rawValue))
        let diffs = difficulty.map { Set([$0.rawValue]) } ?? Set(Difficulty.allCases.map(\.rawValue))
        problem = ProblemBank.pick(categories: cats, difficulties: diffs, excluding: problem?.id)
    }
}

/// 単一選択のタグ列。
struct TagPicker<T: Hashable>: View {
    var items: [T]
    @Binding var selection: T
    var label: (T) -> String

    var body: some View {
        LazyVGrid(columns: [GridItem(.adaptive(minimum: 88), spacing: 8)], alignment: .leading, spacing: 8) {
            ForEach(items, id: \.self) { item in
                Button { selection = item } label: {
                    Tag(text: label(item), isOn: selection == item).frame(maxWidth: .infinity)
                }
                .buttonStyle(.plain)
            }
        }
    }
}
