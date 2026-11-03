import SwiftUI

/// 4桁のテンキー。
struct PasscodeKeypad: View {
    @Binding var code: String
    var disabled = false
    private let rows: [[String]] = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["", "0", "⌫"]]

    var body: some View {
        VStack(spacing: 10) {
            HStack(spacing: 16) {
                ForEach(0..<4, id: \.self) { i in
                    Circle().fill(i < code.count ? Theme.tealDeep : Theme.sunken)
                        .frame(width: 16, height: 16)
                }
            }
            .padding(.bottom, 12)
            ForEach(rows, id: \.self) { row in
                HStack(spacing: 10) {
                    ForEach(row, id: \.self) { key in
                        if key.isEmpty {
                            Color.clear.frame(maxWidth: .infinity)
                        } else {
                            Button { tap(key) } label: {
                                if key == "⌫" { Image(systemName: "delete.left") } else { Text(key) }
                            }
                            .buttonStyle(IsoButtonStyle(kind: key == "⌫" ? .quiet : .secondary, large: true))
                        }
                    }
                }
            }
        }
        .disabled(disabled)
        .opacity(disabled ? 0.5 : 1)
        .sensoryFeedback(.selection, trigger: code)
    }

    private func tap(_ key: String) {
        if key == "⌫" { if !code.isEmpty { code.removeLast() } }
        else if code.count < 4 { code += key }
    }
}

/// 保護者のパスコードを入れる画面。
struct PasscodeEntryView: View {
    @State private var code = ""
    @State private var message: String?
    private let lock = ParentLock.shared

    var body: some View {
        TimelineView(.periodic(from: .now, by: 1)) { _ in
            let until = lock.lockedUntil
            VStack(spacing: 18) {
                Text("保護者のパスコード").font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
                Text(until.map { "しばらく入力できません。あと\(remaining($0))" } ?? (message ?? "4桁のパスコードを入れてください。"))
                    .font(Theme.font(14)).foregroundStyle(until != nil || message != nil ? Theme.danger : Theme.inkSoft)
                    .multilineTextAlignment(.center)
                PasscodeKeypad(code: $code, disabled: until != nil)
                    .padding(.horizontal, 24)
                Button("やめる") { lock.cancelEntry() }.buttonStyle(.quiet)
            }
            .padding(24)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .isoBackground()
            .onChange(of: code) { _, new in
                guard new.count == 4 else { return }
                if !lock.verify(new) {
                    code = ""
                    message = lock.lockedUntil == nil ? "パスコードが違います。" : nil
                }
            }
        }
        .presentationDetents([.large])
        .interactiveDismissDisabled()
    }

    private func remaining(_ date: Date) -> String {
        let s = max(Int(date.timeIntervalSinceNow.rounded(.up)), 0)
        return s >= 60 ? "\((s + 59) / 60)分" : "\(s)秒"
    }
}

/// パスコードを新しく決める画面（2回入れて確認）。
struct PasscodeSetupView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var first: String?
    @State private var code = ""
    @State private var message: String?

    var body: some View {
        VStack(spacing: 18) {
            Text(first == nil ? "新しいパスコード" : "もう一度入れてください")
                .font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
            Text(message ?? "子どもが知らない4桁の数字にしてください。忘れたときは、アプリを入れ直すしかありません（ルールも消えます）。")
                .font(Theme.font(14)).foregroundStyle(message == nil ? Theme.inkSoft : Theme.danger)
                .multilineTextAlignment(.center)
            PasscodeKeypad(code: $code).padding(.horizontal, 24)
            Button("やめる") { dismiss() }.buttonStyle(.quiet)
        }
        .padding(24)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .isoBackground()
        .onChange(of: code) { _, new in
            guard new.count == 4 else { return }
            if let f = first {
                if f == new { ParentLock.shared.setPasscode(new); dismiss() }
                else { first = nil; message = "一致しませんでした。もう一度はじめから入れてください。" }
            } else {
                first = new; message = nil
            }
            code = ""
        }
    }
}
