import SwiftUI
import FamilyControls

struct RuleEditorView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State var rule: GuardRule
    var isNew: Bool
    @State private var showPicker = false
    @State private var confirmDelete = false
    @State private var sel: Set<String> = []          // 選んだ単元（マップのチェック）
    @State private var showRangeMap = false

    private let questionChoices = [1, 2, 3, 4, 5]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                HStack {
                    Text(isNew ? "ルールを追加" : "ルールを編集").font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
                    Spacer()
                    Button("保存") {
                        model.save(rule)
                        dismiss()
                    }
                    .font(Theme.font(16, .bold)).foregroundStyle(canSave ? Theme.tealDeep : Theme.inkFaint)
                    .disabled(!canSave)
                }
                .padding(.top, 24)

                section("制限するアプリ") {
                    Button {
                        showPicker = true
                    } label: {
                        HStack(spacing: 10) {
                            Image(systemName: rule.itemCount == 0 ? "plus.app.fill" : "checkmark.app.fill")
                                .font(.system(size: 26))
                            VStack(alignment: .leading, spacing: 2) {
                                Text(rule.itemCount == 0 ? "制限するアプリを選ぶ" : "\(rule.itemCount)件を選択中")
                                    .font(Theme.font(20, .heavy))
                                if rule.itemCount > 0 { Text("タップして変更").font(Theme.font(12, .semibold)).opacity(0.85) }
                            }
                            Spacer()
                            Image(systemName: "chevron.right").font(.system(size: 15, weight: .bold))
                        }
                        .padding(.horizontal, 16).padding(.vertical, 8)
                    }
                    .buttonStyle(IsoButtonStyle(kind: rule.itemCount == 0 ? .alert : .primary))
                    if !rule.selection.applicationTokens.isEmpty {
                        ScrollView(.horizontal) {
                            HStack(spacing: 10) {
                                ForEach(Array(rule.selection.applicationTokens), id: \.self) { token in
                                    Label(token).labelStyle(.iconOnly).frame(width: 32, height: 32)
                                }
                            }
                        }
                        .scrollIndicators(.hidden)
                    }
                }

                section("どれだけ使うごとに") {
                    VStack(spacing: 6) {
                        HStack(spacing: 0) {
                            Picker("時間", selection: hoursBinding) {
                                ForEach(0...12, id: \.self) { Text("\($0)時間").tag($0) }
                            }
                            .pickerStyle(.wheel)
                            Picker("分", selection: minutesBinding) {
                                ForEach(0..<60, id: \.self) { Text("\($0)分").tag($0) }
                            }
                            .pickerStyle(.wheel)
                            .disabled(rule.thresholdMinutes >= GuardRule.maxMinutes)
                        }
                        .frame(height: 140)
                        .clipped()
                    }
                    .card(padding: 10)
                }

                section("何問出すか") {
                    chips(questionChoices, selected: rule.questionCount, label: { "\($0)問" }) { rule.questionCount = $0 }
                }

                section("出題する範囲") {
                    VStack(alignment: .leading, spacing: 10) {
                        Button { showRangeMap = true } label: {
                            HStack(spacing: 10) {
                                Image(systemName: "point.3.connected.trianglepath.dotted").font(.system(size: 22)).foregroundStyle(Theme.tealDeep)
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(rangeSummary).font(Theme.font(15, .bold)).foregroundStyle(Theme.ink)
                                        .multilineTextAlignment(.leading)
                                    Text("マップで教科・単元を選ぶ").font(Theme.font(12)).foregroundStyle(Theme.inkSoft)
                                }
                                Spacer()
                                Image(systemName: "chevron.right").font(.system(size: 13, weight: .semibold)).foregroundStyle(Theme.inkFaint)
                            }
                            .card(padding: 14)
                        }
                        .buttonStyle(.plain)
                        Text(rule.units.isEmpty
                             ? "教科ごとにまるごと選ぶと、できていない単元を優先して出します。できてきたら、むずかしい問題や次の単元へ進みます。"
                             : "選んだ単元だけが出ます。")
                            .font(Theme.font(12)).foregroundStyle(Theme.inkSoft)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }

                Text("対象のアプリを合計 \(GuardRule.durationText(rule.thresholdMinutes)) 使うとロックされ、\(rule.questionCount)問に正解すると再開できます。そこから、また \(GuardRule.durationText(rule.thresholdMinutes)) たつとロックされます。同じ条件（時間と問題数）のルールは、自動で1つにまとめます。")
                    .font(Theme.font(13)).foregroundStyle(Theme.inkSoft)
                    .fixedSize(horizontal: false, vertical: true)

                if !isNew {
                    Button("このルールを削除") { confirmDelete = true }
                        .font(Theme.font(15, .semibold)).foregroundStyle(Theme.danger)
                        .frame(maxWidth: .infinity)
                }
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 40)
        }
        .isoBackground()
        .onAppear {
            // いまのルールから、チェックされている単元を求める（単元の指定がなければ、分野に入る単元すべて）
            sel = rule.units.isEmpty
                ? Set(UnitCatalog.available.filter { (UnitCatalog.categories[$0.id] ?? []).isSubset(of: rule.categories) }.map(\.id))
                : rule.units
        }
        .onChange(of: sel) { _, new in apply(new) }
        .fullScreenCover(isPresented: $showRangeMap) { RangeMapSheet(selected: $sel) }
        .familyActivityPicker(
            headerText: "制限するアプリを選んでください。カテゴリを選ぶと、その中のすべてのアプリが対象になります。",
            footerText: nil,
            isPresented: $showPicker,
            selection: $rule.selection
        )
        .confirmationDialog("このルールを削除しますか？", isPresented: $confirmDelete, titleVisibility: .visible) {
            Button("削除", role: .destructive) {
                model.delete(rule)
                dismiss()
            }
        }
    }

    /// ダイアルの「時間」。変えたあと、全体が1分〜12時間に収まるようにする。
    private var hoursBinding: Binding<Int> {
        Binding(get: { rule.thresholdMinutes / 60 },
                set: { setTotal($0 * 60 + rule.thresholdMinutes % 60) })
    }
    private var minutesBinding: Binding<Int> {
        Binding(get: { rule.thresholdMinutes % 60 },
                set: { setTotal(rule.thresholdMinutes / 60 * 60 + $0) })
    }
    private func setTotal(_ total: Int) { rule.thresholdMinutes = min(max(total, 1), GuardRule.maxMinutes) }

    private var canSave: Bool { rule.itemCount > 0 && !sel.isEmpty }

    /// マップで選んだ単元を、ルールの「分野」と「単元」に直す。
    /// 選んだ単元が、その分野の単元すべてなら「おまかせ」（単元は指定しない）。
    private func apply(_ s: Set<String>) {
        guard !s.isEmpty else { return }
        let comm = s.filter(CommunityCache.isCommunity)            // 「みんなの問題」の指定
        let real = s.subtracting(comm)
        var cats = real.reduce(into: Set<String>()) { $0.formUnion(UnitCatalog.categories[$1] ?? []) }
        if cats.isEmpty {                                           // みんなの問題だけのときは、その教科の分野を入れておく
            for id in comm { if let sub = Subject(rawValue: String(id.dropFirst(CommunityCache.prefix.count))) { cats.formUnion(sub.categories.map(\.rawValue)) } }
        }
        let closure = Set(UnitCatalog.available.filter { (UnitCatalog.categories[$0.id] ?? []).isSubset(of: cats) }.map(\.id))
        rule.categories = cats
        rule.units = (comm.isEmpty && real == closure) ? [] : s
    }

    /// 例：「数学（すべて）・英語（3単元）」
    private var rangeSummary: String {
        if sel.isEmpty { return "範囲を選んでください" }
        let parts = Subject.allCases.compactMap { s -> String? in
            let all = UnitCatalog.units(in: s).map(\.id)
            let n = all.filter { sel.contains($0) }.count
            let comm = sel.contains(CommunityCache.prefix + s.rawValue)
            if n == 0 && !comm { return nil }
            let body = all.isEmpty ? "みんなの問題" : (n == all.count ? "すべて" : "\(n)単元")
            return "\(s.label)（\(body)\(comm && !all.isEmpty ? "＋みんなの問題" : "")）"
        }
        return parts.joined(separator: "・")
    }

    private func chips(_ values: [Int], selected: Int, label: @escaping (Int) -> String,
                       action: @escaping (Int) -> Void) -> some View {
        HStack(spacing: 8) {
            ForEach(values, id: \.self) { v in
                Button { action(v) } label: {
                    Tag(text: label(v), isOn: selected == v)
                }
                .buttonStyle(.plain)
            }
        }
    }

    private func section<C: View>(_ title: String, @ViewBuilder content: () -> C) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title)
            content()
        }
    }
}


/// 出題範囲を、マインドマップで選ぶ画面。チェックを付けた単元が出題される。
struct RangeMapSheet: View {
    @Binding var selected: Set<String>
    @Environment(\.dismiss) private var dismiss
    @State private var initial: Set<String> = []       // 開いたときの選択（空のまま閉じたときに戻す）

    private let root = BookMap.selector()

    private func leaves(_ n: MapNode) -> [String] {
        n.children.isEmpty ? (n.id.hasPrefix("u:") ? [String(n.id.dropFirst(2))] : []) : n.children.flatMap(leaves)
    }

    private func state(_ n: MapNode) -> MindMapView.CheckState {
        let ids = leaves(n)
        guard !ids.isEmpty else { return .off }
        let k = ids.filter { selected.contains($0) }.count
        return k == 0 ? .off : (k == ids.count ? .on : .partial)
    }

    private func toggle(_ n: MapNode) {
        let ids = Set(leaves(n))
        if state(n) == .on { selected.subtract(ids) } else { selected.formUnion(ids) }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("出題する範囲").font(Theme.font(22, .bold)).foregroundStyle(Theme.ink)
                Spacer()
                Button(selected.isEmpty ? "もとに戻す" : "完了") {
                    if selected.isEmpty { selected = initial }          // 何も選ばずに閉じたら、開いたときの選択に戻す
                    dismiss()
                }
                .font(Theme.font(16, .bold)).foregroundStyle(Theme.tealDeep)
                .frame(minHeight: 44)
            }
            .padding(.horizontal, 20).padding(.top, 24)
            Text(selected.isEmpty ? "チェックを付けて、出したい教科・単元を選んでください。" : "選んだ単元：\(selected.count)")
                .font(Theme.font(13, .semibold)).foregroundStyle(selected.isEmpty ? Theme.danger : Theme.tealDeep)
                .padding(.horizontal, 20)
            MindMapView(root: root, openPath: ["root"],
                        checkState: { state($0) }, onCheck: { toggle($0) }) { node in toggle(node) }
        }
        .isoBackground()
        .onAppear { initial = selected }
    }
}
