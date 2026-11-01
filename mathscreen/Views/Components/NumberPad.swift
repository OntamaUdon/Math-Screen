import SwiftUI

/// 整数入力用のテンキー。
struct NumberPad: View {
    @Binding var text: String
    var onSubmit: () -> Void

    private let rows: [[String]] = [["7", "8", "9"], ["4", "5", "6"], ["1", "2", "3"], ["±", "0", "⌫"]]

    var body: some View {
        VStack(spacing: 10) {
            ForEach(rows, id: \.self) { row in
                HStack(spacing: 10) {
                    ForEach(row, id: \.self) { key in
                        Button { tap(key) } label: {
                            if key == "⌫" { Image(systemName: "delete.left") } else { Text(key) }
                        }
                        .buttonStyle(FlatButtonStyle(kind: key == "±" || key == "⌫" ? .quiet : .secondary, large: true))
                    }
                }
            }
            Button("こたえる", action: onSubmit)
                .buttonStyle(.primary)
                .disabled(Int(text) == nil)
                .opacity(Int(text) == nil ? 0.5 : 1)
                .padding(.top, 4)
        }
        .sensoryFeedback(.selection, trigger: text)
    }

    private func tap(_ key: String) {
        switch key {
        case "⌫":
            if !text.isEmpty { text.removeLast() }
        case "±":
            if text.hasPrefix("-") { text.removeFirst() } else { text = "-" + text }
        default:
            let digits = text.filter(\.isNumber)
            guard digits.count < 9 else { return }
            if digits == "0" { text = text.replacingOccurrences(of: "0", with: "") }
            text += key
        }
    }
}
