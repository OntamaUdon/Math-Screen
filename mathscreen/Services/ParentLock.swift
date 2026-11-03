import SwiftUI
import CryptoKit

/// 保護者用パスコード（Premium の機能）。ルールの変更・設定画面・Premium の管理を守る。
/// パスコードはこの端末の中だけに、ソルト付きのハッシュで保存する（サーバーには送らない）。
/// アプリを入れ直すと消える。
@MainActor
@Observable
final class ParentLock {
    static let shared = ParentLock()

    private let d = UserDefaults.standard
    private enum Key {
        static let hash = "parent.hash", salt = "parent.salt"
        static let failures = "parent.failures", lockedUntil = "parent.lockedUntil"
    }
    /// 解除したあと、この時間が過ぎるか、アプリを閉じると、また閉まる。
    static let openSeconds: TimeInterval = 180

    private(set) var hasPasscode: Bool
    private var openUntil: Date = .distantPast
    var showEntry = false
    private var pending: (() -> Void)?

    private init() { hasPasscode = UserDefaults.standard.string(forKey: Key.hash) != nil }

    /// パスコードが設定されていて、Premium で、いま閉まっている。
    var needsLock: Bool { isActive && Date() >= openUntil }
    /// 保護者モードが有効か（無料に戻ったら効かない）。
    var isActive: Bool { hasPasscode && AppModel.shared.isPremium }

    /// 守られた操作を実行する。閉まっていれば、パスコード入力を出して、通ったら実行する。
    func request(_ action: @escaping () -> Void) {
        if needsLock { pending = action; showEntry = true } else { action() }
    }

    func cancelEntry() { pending = nil; showEntry = false }
    func lock() { openUntil = .distantPast }

    // MARK: 間違えたときの待ち時間
    private var failures: Int { d.integer(forKey: Key.failures) }
    var lockedUntil: Date? {
        let t = d.double(forKey: Key.lockedUntil)
        return t > Date().timeIntervalSince1970 ? Date(timeIntervalSince1970: t) : nil
    }
    /// 3回目の間違いから待たされ、間違えるたびに長くなる。
    private static func wait(afterFailures n: Int) -> TimeInterval? {
        switch n {
        case ..<3: nil
        case 3: 30
        case 4: 60
        case 5: 300
        case 6: 900
        default: 3600
        }
    }

    /// パスコードを確かめる。待ち時間中は常に false。
    func verify(_ code: String) -> Bool {
        if lockedUntil != nil { return false }
        if hash(code) == d.string(forKey: Key.hash) {
            d.set(0, forKey: Key.failures)
            d.removeObject(forKey: Key.lockedUntil)
            openUntil = Date().addingTimeInterval(Self.openSeconds)
            showEntry = false
            let run = pending
            pending = nil
            run?()
            return true
        }
        let n = failures + 1
        d.set(n, forKey: Key.failures)
        if let w = Self.wait(afterFailures: n) {
            d.set(Date().addingTimeInterval(w).timeIntervalSince1970, forKey: Key.lockedUntil)
        }
        return false
    }

    func setPasscode(_ code: String) {
        let salt = (0..<16).map { _ in String(UInt8.random(in: 0...255), radix: 16) }.joined()
        d.set(salt, forKey: Key.salt)
        d.set(hash(code), forKey: Key.hash)
        d.set(0, forKey: Key.failures)
        d.removeObject(forKey: Key.lockedUntil)
        hasPasscode = true
        openUntil = Date().addingTimeInterval(Self.openSeconds)
    }

    func clearPasscode() {
        d.removeObject(forKey: Key.hash)
        d.removeObject(forKey: Key.salt)
        d.set(0, forKey: Key.failures)
        d.removeObject(forKey: Key.lockedUntil)
        hasPasscode = false
    }

    private func hash(_ code: String) -> String {
        let salt = d.string(forKey: Key.salt) ?? ""
        return SHA256.hash(data: Data((salt + code).utf8)).map { String(format: "%02x", $0) }.joined()
    }

    // MARK: スクリーンタイムの許可の確認記録（保護者にだけ見せる）
    static func recordAuthorization(approved: Bool) {
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "auth.checkedAt")
        if approved { UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "auth.approvedAt") }
    }
    static var authorizationCheckedAt: Date? { date("auth.checkedAt") }
    static var authorizationApprovedAt: Date? { date("auth.approvedAt") }
    private static func date(_ key: String) -> Date? {
        let t = UserDefaults.standard.double(forKey: key)
        return t > 0 ? Date(timeIntervalSince1970: t) : nil
    }
}
