import Foundation

/// コミュニティ投稿（Supabase）への接続設定。公開前提の値（publishable key）なのでアプリに入れてよい。
enum CommunityConfig {
    static let baseURL = URL(string: "https://htimtxhdxbzmohgwqtyj.supabase.co")!
    static let key = "sb_publishable_hioC3yo3fUazs_5rG6ORZw_w0jmXNWd"
}

struct CommunityError: LocalizedError {
    let message: String
    var errorDescription: String? { message }
}

/// サーバーに保存された投稿1件。
struct CommunityRow: Codable, Identifiable, Hashable {
    let id: String
    let author: String
    let genre: String
    let difficulty: Int
    let title: String
    let body: String
    let plain: String
    let answer: String
    let explanation: String
    let choices: [String]?
    let hint: String?
    let status: String
    let reviewNote: String?

    /// アプリ内の問題として解くための形に変換。
    var problem: Problem? {
        guard let a = Int(answer) else { return nil }
        return Problem(id: "c-" + id, category: genre, difficulty: difficulty, title: title, body: body,
                       plain: plain, answer: a, explanation: explanation, choices: choices, hint: hint)
    }

    var statusLabel: String {
        switch status {
        case "approved": "公開中"
        case "rejected": "却下"
        case "flagged": "非公開（通報）"
        default: "審査待ち"
        }
    }
}

struct NewPost: Encodable {
    var genre: String
    var difficulty: Int
    var title: String
    var body: String
    var plain: String
    var answer: String
    var explanation: String
    var choices: [String]?
    var hint: String?
}

/// 匿名ログインで始める、Supabase の REST への小さなクライアント。
actor Community {
    static let shared = Community()

    private struct Session: Codable {
        var access: String
        var refresh: String
        var expires: Date
        var userID: String
    }

    private struct AuthResponse: Decodable {
        struct User: Decodable { let id: String }
        let accessToken: String
        let refreshToken: String
        let expiresIn: Int
        let user: User
    }

    private static let sessionKey = "community.session"
    private var session: Session? = Community.loadSession()

    private static func loadSession() -> Session? {
        guard let data = UserDefaults.standard.data(forKey: sessionKey) else { return nil }
        return try? JSONDecoder().decode(Session.self, from: data)
    }

    private func store(_ s: Session?) {
        session = s
        if let s, let data = try? JSONEncoder().encode(s) {
            UserDefaults.standard.set(data, forKey: Community.sessionKey)
        } else {
            UserDefaults.standard.removeObject(forKey: Community.sessionKey)
        }
    }

    // MARK: 認証
    private func apply(_ data: Data) throws -> Session {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        let r = try d.decode(AuthResponse.self, from: data)
        let s = Session(access: r.accessToken, refresh: r.refreshToken,
                        expires: Date().addingTimeInterval(TimeInterval(r.expiresIn)), userID: r.user.id)
        store(s)
        return s
    }

    private func signUp() async throws -> Session {
        let data = try await send("POST", "auth/v1/signup", body: Data("{}".utf8), auth: false)
        return try apply(data)
    }

    private func refresh(_ token: String) async throws -> Session {
        let body = try JSONSerialization.data(withJSONObject: ["refresh_token": token])
        let data = try await send("POST", "auth/v1/token", query: [URLQueryItem(name: "grant_type", value: "refresh_token")],
                                  body: body, auth: false)
        return try apply(data)
    }

    private func validSession() async throws -> Session {
        if let s = session, s.expires > Date().addingTimeInterval(60) { return s }
        if let s = session, let r = try? await refresh(s.refresh) { return r }
        return try await signUp()
    }

    func userID() async throws -> String { try await validSession().userID }

    // MARK: 通信
    private func send(_ method: String, _ path: String, query: [URLQueryItem] = [], body: Data? = nil,
                      auth: Bool = true, prefer: String? = nil) async throws -> Data {
        var comps = URLComponents(url: CommunityConfig.baseURL.appendingPathComponent(path), resolvingAgainstBaseURL: false)!
        if !query.isEmpty { comps.queryItems = query }
        var req = URLRequest(url: comps.url!)
        req.httpMethod = method
        req.timeoutInterval = 20
        req.setValue(CommunityConfig.key, forHTTPHeaderField: "apikey")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if auth { req.setValue("Bearer " + (try await validSession().access), forHTTPHeaderField: "Authorization") }
        if let prefer { req.setValue(prefer, forHTTPHeaderField: "Prefer") }
        req.httpBody = body

        let data: Data, resp: URLResponse
        do { (data, resp) = try await URLSession.shared.data(for: req) }
        catch { throw CommunityError(message: "通信できませんでした。電波の良いところで、もう一度お試しください。") }

        let code = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(code) else {
            let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
            let detail = (obj?["message"] as? String) ?? (obj?["msg"] as? String) ?? ""
            throw CommunityError(message: "うまくいきませんでした（コード \(code)）\(detail.isEmpty ? "" : "：" + detail)")
        }
        return data
    }

    private func decodeRows(_ data: Data) throws -> [CommunityRow] {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        return try d.decode([CommunityRow].self, from: data)
    }

    // MARK: 機能
    /// 公開済みの問題。ブロックした人の投稿は除く。
    func approved() async throws -> [CommunityRow] {
        let data = try await send("GET", "rest/v1/community_problems", query: [
            URLQueryItem(name: "select", value: "*"),
            URLQueryItem(name: "status", value: "eq.approved"),
            URLQueryItem(name: "order", value: "created_at.desc"),
            URLQueryItem(name: "limit", value: "100"),
        ])
        let blocked = Set(try await blockedAuthors())
        return try decodeRows(data).filter { !blocked.contains($0.author) }
    }

    func mine() async throws -> [CommunityRow] {
        let uid = try await userID()
        let data = try await send("GET", "rest/v1/community_problems", query: [
            URLQueryItem(name: "select", value: "*"),
            URLQueryItem(name: "author", value: "eq.\(uid)"),
            URLQueryItem(name: "order", value: "created_at.desc"),
        ])
        return try decodeRows(data)
    }

    func post(_ p: NewPost) async throws {
        let e = JSONEncoder()
        e.keyEncodingStrategy = .convertToSnakeCase
        _ = try await send("POST", "rest/v1/community_problems", body: try e.encode(p), prefer: "return=minimal")
    }

    func deletePost(_ id: String) async throws {
        _ = try await send("DELETE", "rest/v1/community_problems", query: [URLQueryItem(name: "id", value: "eq.\(id)")])
    }

    func report(_ problemID: String, reason: String) async throws {
        let body = try JSONSerialization.data(withJSONObject: ["problem_id": problemID, "reason": reason])
        _ = try await send("POST", "rest/v1/problem_reports", body: body, prefer: "return=minimal")
    }

    func block(_ author: String) async throws {
        let body = try JSONSerialization.data(withJSONObject: ["blocked": author])
        _ = try await send("POST", "rest/v1/user_blocks", body: body, prefer: "return=minimal")
    }

    private func blockedAuthors() async throws -> [String] {
        let data = try await send("GET", "rest/v1/user_blocks", query: [URLQueryItem(name: "select", value: "blocked")])
        let rows = (try? JSONSerialization.jsonObject(with: data) as? [[String: String]]) ?? []
        return rows.compactMap { $0["blocked"] }
    }

    /// 自分の投稿・通報・ブロックをサーバーから消し、この端末の匿名アカウントも手放す。
    func deleteMyData() async throws {
        _ = try await send("POST", "rest/v1/rpc/delete_my_data", body: Data("{}".utf8))
        store(nil)
    }
}
