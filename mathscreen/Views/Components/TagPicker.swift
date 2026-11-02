import SwiftUI

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
