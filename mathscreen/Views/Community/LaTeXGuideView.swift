import SwiftUI

/// 数式の書き方（LaTeX）の案内。LaTeX を知らなくても書けるように。
struct LaTeXGuideView: View {
    @Environment(\.dismiss) private var dismiss

    private let examples: [(label: String, code: String)] = [
        ("分数", "\\frac{1}{2}"),
        ("累乗", "x^2,  2^{10}"),
        ("添え字", "a_n,  x_{12}"),
        ("平方根", "\\sqrt{3},  \\sqrt[3]{8}"),
        ("かけ算・わり算", "3 \\times 4,  8 \\div 2"),
        ("角度", "30^\\circ"),
        ("円周率", "\\pi"),
        ("不等号", "x \\le 3,  x \\ge 1,  x \\ne 0"),
        ("絶対値", "|x - 2|"),
        ("三角関数", "\\sin 30^\\circ,  \\cos x"),
        ("対数", "\\log_2 8"),
        ("総和", "\\sum_{k=1}^{n} k"),
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                HStack {
                    Text("数式の書き方").font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
                    Spacer()
                    Button("閉じる") { dismiss() }.font(Theme.font(15, .semibold)).foregroundStyle(Theme.inkSoft)
                }
                .padding(.top, 24)

                VStack(alignment: .leading, spacing: 8) {
                    Text("基本").font(Theme.font(15, .bold)).foregroundStyle(Theme.ink)
                    Text("数式の部分を、ドル記号 $ ではさみます。それ以外は、ふつうの文章のまま書けます。")
                        .font(Theme.font(14)).foregroundStyle(Theme.inkSoft)
                    Text("例：次の値を求めよ。 $\\frac{1}{2} + \\frac{1}{3}$")
                        .font(Theme.font(13, .semibold)).foregroundStyle(Theme.tealDeep)
                    MathText(source: "次の値を求めよ。 $\\frac{1}{2} + \\frac{1}{3}$", fontSize: 16, spoken: "")
                }
                .card()

                Text("よく使う書き方").font(Theme.font(15, .bold)).foregroundStyle(Theme.ink)
                VStack(spacing: 0) {
                    ForEach(Array(examples.enumerated()), id: \.offset) { i, e in
                        if i > 0 { Divider().padding(.leading, 16) }
                        VStack(alignment: .leading, spacing: 6) {
                            Text(e.label).font(Theme.font(13, .bold)).foregroundStyle(Theme.inkSoft)
                            Text("$" + e.code + "$").font(.system(size: 14, design: .monospaced)).foregroundStyle(Theme.ink)
                            MathText(source: "$" + e.code + "$", fontSize: 16, spoken: "")
                        }
                        .padding(.horizontal, 16).padding(.vertical, 12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
                .card(padding: 0)

                VStack(alignment: .leading, spacing: 8) {
                    Text("コツ").font(Theme.font(15, .bold)).foregroundStyle(Theme.ink)
                    Text("・かっこ { } は、閉じ忘れに注意してください。\n・2文字以上の累乗や添え字は x^{10} のように { } で囲みます。\n・「プレビュー」に正しく出ているか、投稿の前に確認しましょう。\n・答えは整数、または4択だけです。")
                        .font(Theme.font(14)).foregroundStyle(Theme.inkSoft).lineSpacing(4)
                }
                .card()
            }
            .padding(.horizontal, 20).padding(.bottom, 40)
        }
        .isoBackground()
    }
}
