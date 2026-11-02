import SwiftUI

/// 単元の完成度を示す棒。色は、未学習=グレー、練習中=コーラル、得意=ティール、完成=金。
struct MasteryMeter: View {
    var progress: UnitProgress

    private var fraction: Double {
        switch progress.level {
        case .none: 0
        case .complete: 1
        default: max(0.08, progress.score)
        }
    }

    private var color: Color {
        switch progress.level {
        case .none: Theme.inkFaint
        case .learning: Theme.coral
        case .good: Theme.teal
        case .complete: Theme.gold
        }
    }

    var body: some View {
        GeometryReader { geo in
            ZStack(alignment: .leading) {
                Capsule().fill(Theme.sunken)
                Capsule().fill(color).frame(width: geo.size.width * fraction)
            }
        }
        .frame(height: 6)
    }
}

/// 単元の一覧。教科 → 段階（小学・中学・高校）の順に並ぶ。
/// `selection` を渡すとチェックで選べる（ルール用）。渡さなければ、完成度を見るだけ（記録用）。
struct UnitListView: View {
    var subjects: [Subject]
    var selection: Binding<Set<String>>? = nil

    private let stages = ["小学", "中学", "高校"]

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            ForEach(subjects) { subject in
                let units = UnitCatalog.units(in: subject)
                if !units.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(subject.label).font(Theme.font(16, .bold)).foregroundStyle(Theme.ink)
                            Spacer()
                            if let selection {
                                let ids = Set(units.map(\.id))
                                let all = ids.isSubset(of: selection.wrappedValue)
                                Button(all ? "すべて外す" : "すべて選ぶ") {
                                    if all { selection.wrappedValue.subtract(ids) } else { selection.wrappedValue.formUnion(ids) }
                                }
                                .font(Theme.font(13, .semibold)).foregroundStyle(Theme.tealDeep)
                            }
                        }
                        VStack(spacing: 0) {
                            ForEach(stages, id: \.self) { stage in
                                let list = units.filter { $0.stage == stage }
                                if !list.isEmpty {
                                    Text(stage).font(Theme.font(11, .bold)).foregroundStyle(Theme.inkSoft)
                                        .padding(.horizontal, 16).padding(.top, 10).padding(.bottom, 2)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                    ForEach(list) { unit in row(unit) }
                                }
                            }
                        }
                        .padding(.bottom, 6)
                        .card(padding: 0)
                    }
                }
            }
        }
    }

    private func row(_ unit: UnitInfo) -> some View {
        let progress = MasteryStore.shared.progress(unit: unit.id)
        let isOn = selection?.wrappedValue.contains(unit.id) ?? false
        return Button {
            guard let selection else { return }
            if isOn { selection.wrappedValue.remove(unit.id) } else { selection.wrappedValue.insert(unit.id) }
        } label: {
            HStack(spacing: 12) {
                if selection != nil {
                    Image(systemName: isOn ? "checkmark.circle.fill" : "circle")
                        .font(.system(size: 24)).foregroundStyle(isOn ? Theme.tealDeep : Theme.inkFaint)
                }
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        Text(unit.name).font(Theme.font(15, .semibold)).foregroundStyle(Theme.ink)
                        Spacer()
                        Text(progress.level.label).font(Theme.font(12, .bold))
                            .foregroundStyle(progress.level == .none ? Theme.inkFaint : Theme.inkSoft)
                    }
                    MasteryMeter(progress: progress)
                }
            }
            .padding(.horizontal, 16).padding(.vertical, 10)
            .background(isOn ? Theme.teal.opacity(0.12) : Color.clear)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .disabled(selection == nil)
    }
}
