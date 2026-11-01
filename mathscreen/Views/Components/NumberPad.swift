import SwiftUI

/// 整数入力用のクレイ風テンキー。
struct NumberPad: View {
    @Binding var text: String
    var onSubmit: () -> Void

    private let rows: [[String]] = [["7", "8", "9"], ["4", "5", "6"], ["1", "2", "3"], ["±", "0", "⌫"]]

    var body: some View {
        VStack(spacing: 12) {
            ForEach(rows, id: \.self) { row in
                HStack(spacing: 12) {
                    ForEach(row, id: \.self) { key in
                        Button { tap(key) } label: {
                            Group {
                                if key == "⌫" { Image(systemName: "delete.left") } else { Text(key) }
                            }
                            .font(Clay.font(24, .semibold))
                            .frame(maxWidth: .infinity, minHeight: 54)
                        }
                        .buttonStyle(ClayButtonStyle(color: key == "±" || key == "⌫" ? Clay.sunken : Clay.surface,
                                                     radius: 18))
                    }
                }
            }
            Button(action: onSubmit) {
                Label("こたえる", systemImage: "checkmark")
            }
            .buttonStyle(.clay(Clay.lavender))
            .disabled(Int(text) == nil)
            .opacity(Int(text) == nil ? 0.55 : 1)
        }
        .sensoryFeedback(.selection, trigger: text)
    }

    private func tap(_ key: String) {
        switch key {
        case "⌫":
            if !text.isEmpty { text.removeLast() }
        case "±":
            if text.hasPrefix("−") || text.hasPrefix("-") { text.removeFirst() } else { text = "-" + text }
        default:
            let digits = text.filter(\.isNumber)
            guard digits.count < 9 else { return }
            if digits == "0" { text = text.replacingOccurrences(of: "0", with: "") }
            text += key
        }
    }
}
