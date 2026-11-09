import Foundation

/// 無料で使える範囲。アプリロックと数学は、だれでも使える。数学以外の科目は、解くロックプランで使える。
/// （iOS の機能であるスクリーンタイムには課金しない：App Store 審査ガイドライン 4.10）
enum Access {
    /// 契約中か。AppModel が状態を読み込むたびに書きかえる。
    static var premium = false

    static let freeSubject: Subject = .math

    static func isOpen(_ subject: Subject) -> Bool { premium || subject == freeSubject }

    static func isOpen(category: String) -> Bool {
        isOpen(ProblemCategory(rawValue: category)?.subject ?? .general)
    }

    static func isOpen(_ p: Problem) -> Bool { isOpen(category: p.category) }

    static func isOpen(unit: String) -> Bool {
        guard let s = UnitCatalog.info(unit).flatMap({ Subject(rawValue: $0.subject) }) else { return premium }
        return isOpen(s)
    }

    /// 無料の数学の分野（ノンジャンルの数学＝発展内容も含む）。
    static let freeCategories: Set<String> = Set(ProblemCategory.allCases.filter { $0.subject == .math }.map(\.rawValue))

    /// 出題に使う分野と単元を、使える範囲にしぼる。しぼって何も残らなければ、数学のすべて（おまかせ）。
    static func filter(categories: Set<String>, units: Set<String>) -> (categories: Set<String>, units: Set<String>) {
        if premium { return (categories, units) }
        let cats = categories.filter { isOpen(category: $0) }
        let us = units.filter { isOpen(unit: $0) }
        if cats.isEmpty { return (freeCategories, []) }
        if !units.isEmpty && us.isEmpty { return (cats, []) }
        return (cats, us)
    }
}
