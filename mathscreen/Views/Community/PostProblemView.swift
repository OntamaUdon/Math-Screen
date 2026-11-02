import SwiftUI

/// 問題の投稿フォーム。投稿は「審査待ち」で保存され、通ると公開される。
struct PostProblemView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var category: ProblemCategory = .junior
    @State private var difficulty: Difficulty = .easy
    @State private var isChoice = false
    @State private var title = ""
    @State private var bodyText = ""
    @State private var choices = ["", "", "", ""]
    @State private var correct = 0
    @State private var intAnswer = ""
    @State private var explanation = ""
    @State private var hint = ""
    @State private var sending = false
    @State private var error: String?
    @State private var done = false
    @State private var showGuide = false

    private var plain: String { bodyText.replacingOccurrences(of: "$", with: "") }

    private var valid: Bool {
        guard !title.trimmed.isEmpty, title.count <= 60,
              !bodyText.trimmed.isEmpty, bodyText.count <= 1000,
              explanation.count <= 1000, hint.count <= 300 else { return false }
        if isChoice { return choices.allSatisfy { !$0.trimmed.isEmpty && $0.count <= 200 } }
        return Int(intAnswer.trimmed) != nil
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                HStack {
                    Text("問題を投稿").font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
                    Spacer()
                    Button("閉じる") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                .padding(.top, 24)

                Text("投稿した問題は、確認のあとに公開されます。不適切な内容や、答えがまちがっている問題は公開されません。")
                    .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)

                section("分野") {
                    ForEach(Subject.allCases) { s in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(s.label).font(Theme.font(13, .bold)).foregroundStyle(Theme.inkSoft)
                            TagPicker(items: s.categories, selection: $category) { $0.label }
                        }
                    }
                }
                section("難しさ") { TagPicker(items: Difficulty.allCases, selection: $difficulty) { $0.label } }
                section("答え方") { TagPicker(items: [false, true], selection: $isChoice) { $0 ? "4択" : "整数で答える" } }

                section("タイトル（60字まで）") { field("例：分数の足し算", text: $title) }

                section("問題文") {
                    Button { showGuide = true } label: {
                        Label("数式の書き方を見る", systemImage: "questionmark.circle")
                            .font(Theme.font(13, .semibold)).foregroundStyle(Theme.tealDeep)
                    }
                    TextEditor(text: $bodyText)
                        .frame(minHeight: 120).scrollContentBackground(.hidden)
                        .padding(8).well()
                    if !bodyText.trimmed.isEmpty {
                        SectionLabel("プレビュー")
                        MathText(source: bodyText, fontSize: 16, spoken: plain).card(padding: 14)
                    }
                }

                if isChoice {
                    section("選択肢（正解を選んでください）") {
                        ForEach(0..<4, id: \.self) { i in
                            HStack(spacing: 10) {
                                Button { correct = i } label: {
                                    Image(systemName: correct == i ? "checkmark.circle.fill" : "circle")
                                        .font(.system(size: 22)).foregroundStyle(correct == i ? Theme.tealDeep : Theme.inkFaint)
                                }
                                .buttonStyle(.plain)
                                field("\(Problem.choiceMarks[i])", text: $choices[i])
                            }
                        }
                    }
                } else {
                    section("答え（整数）") { field("例：12", text: $intAnswer).keyboardType(.numbersAndPunctuation) }
                }

                section("解説（任意）") { field("答えの理由など", text: $explanation, axis: .vertical) }
                section("ヒント（任意）") { field("答えを直接は言わないヒント", text: $hint, axis: .vertical) }

                if let error {
                    Text(error).font(Theme.font(14)).foregroundStyle(Theme.danger)
                }

                Button(sending ? "送信中…" : "投稿する") { Task { await submit() } }
                    .buttonStyle(.primary)
                    .disabled(!valid || sending)
                    .opacity(valid && !sending ? 1 : 0.5)
            }
            .padding(.horizontal, 20).padding(.bottom, 40)
        }
        .isoBackground()
        .sheet(isPresented: $showGuide) { LaTeXGuideView() }
        .alert("投稿しました", isPresented: $done) {
            Button("OK") { dismiss() }
        } message: {
            Text("確認のあとに公開されます。「みんなの問題」の「自分の投稿」で状況を見られます。")
        }
    }

    private func submit() async {
        sending = true; error = nil
        defer { sending = false }
        let post = NewPost(
            genre: category.rawValue, difficulty: difficulty.rawValue, title: title.trimmed,
            body: bodyText.trimmed, plain: plain.trimmed,
            answer: isChoice ? String(correct) : String(Int(intAnswer.trimmed) ?? 0),
            explanation: explanation.trimmed,
            choices: isChoice ? choices.map(\.trimmed) : nil,
            hint: hint.trimmed.isEmpty ? nil : hint.trimmed)
        do { try await Community.shared.post(post); done = true }
        catch { self.error = error.localizedDescription }
    }

    private func field(_ placeholder: String, text: Binding<String>, axis: Axis = .horizontal) -> some View {
        TextField(placeholder, text: text, axis: axis)
            .font(Theme.font(16))
            .padding(12).well()
    }

    private func section<C: View>(_ title: String, @ViewBuilder content: () -> C) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title)
            content()
        }
    }
}

private extension String {
    var trimmed: String { trimmingCharacters(in: .whitespacesAndNewlines) }
}
