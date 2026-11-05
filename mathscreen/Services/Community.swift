import Foundation

/// 正答率の集計（Supabase）への接続設定。公開前提の値（publishable key）なのでアプリに入れてよい。
enum CommunityConfig {
    static let baseURL = URL(string: "https://htimtxhdxbzmohgwqtyj.supabase.co")!
    static let key = "sb_publishable_hioC3yo3fUazs_5rG6ORZw_w0jmXNWd"
}

struct CommunityError: LocalizedError {
    let message: String
    var errorDescription: String? { message }
}

/// 匿名ログインで始める、正答率の集計用の Supabase REST クライアント。
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
        catch { throw CommunityError(message: "通信できませんでした。電波のいい場所で、もう一度試してください。") }

        let code = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(code) else {
            let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
            let detail = (obj?["message"] as? String) ?? (obj?["msg"] as? String) ?? ""
            throw CommunityError(message: "うまくいきませんでした（コード \(code)）\(detail.isEmpty ? "" : "：" + detail)")
        }
        return data
    }

    // MARK: 正答率の集計（問題ごと。1回目の解答だけを数える）
    /// 1回目の解答を集計に送る。同じ問題は、この端末から1回だけ。
    func recordFirstAttempt(_ id: String, correct: Bool) async {
        let key = "stats.recorded"
        var done = Set(UserDefaults.standard.stringArray(forKey: key) ?? [])
        guard !done.contains(id) else { return }
        guard let body = try? JSONSerialization.data(withJSONObject: ["p_key": id, "p_correct": correct]) else { return }
        if (try? await send("POST", "rest/v1/rpc/record_attempt", body: body)) != nil {
            done.insert(id)
            UserDefaults.standard.set(Array(done), forKey: key)
        }
    }

    /// すべての問題の集計をまとめて取る（難しさの評価に使う）。
    func allStats() async -> [String: [Int]]? {
        guard let data = try? await send("GET", "rest/v1/problem_stats", query: [
            URLQueryItem(name: "select", value: "problem_key,shown,correct"),
            URLQueryItem(name: "limit", value: "20000"),
        ]) else { return nil }
        let rows = (try? JSONSerialization.jsonObject(with: data) as? [[String: Any]]) ?? []
        var out: [String: [Int]] = [:]
        for r in rows {
            if let k = r["problem_key"] as? String, let s = r["shown"] as? Int, let c = r["correct"] as? Int { out[k] = [s, c] }
        }
        return out
    }

    func stats(for id: String) async -> (shown: Int, correct: Int)? {
        guard let data = try? await send("GET", "rest/v1/problem_stats", query: [
            URLQueryItem(name: "select", value: "shown,correct"),
            URLQueryItem(name: "problem_key", value: "eq.\(id)"),
        ]) else { return nil }
        let rows = (try? JSONSerialization.jsonObject(with: data) as? [[String: Int]]) ?? []
        guard let r = rows.first, let s = r["shown"], let c = r["correct"] else { return nil }
        return (s, c)
    }
}
