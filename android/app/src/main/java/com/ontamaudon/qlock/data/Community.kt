package com.ontamaudon.qlock.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

/**
 * 正答率の集計（Supabase）。iPhone 版と同じプロジェクト・同じ表を使う（公開前提のキーなので、アプリに入れてよい）。
 * 匿名ログインで始める。送るのは「問題の番号」と「1回目の答えが正解か」だけ。
 */
object Community {
    private const val BASE = "https://htimtxhdxbzmohgwqtyj.supabase.co"
    private const val KEY = "sb_publishable_hioC3yo3fUazs_5rG6ORZw_w0jmXNWd"
    private val mutex = Mutex()

    private data class Session(val access: String, val refresh: String, val expires: Long)

    private var session: Session? = Store.prefs.getString("community.session", null)?.let {
        runCatching { JSONObject(it).let { o -> Session(o.getString("a"), o.getString("r"), o.getLong("e")) } }.getOrNull()
    }

    private fun store(s: Session?) {
        session = s
        Store.prefs.edit().apply {
            if (s == null) remove("community.session")
            else putString("community.session", JSONObject().put("a", s.access).put("r", s.refresh).put("e", s.expires).toString())
        }.apply()
    }

    private fun apply(text: String): Session {
        val o = JSONObject(text)
        val s = Session(o.getString("access_token"), o.getString("refresh_token"),
            System.currentTimeMillis() + o.getLong("expires_in") * 1000)
        store(s)
        return s
    }

    private suspend fun validSession(): Session = mutex.withLock {
        session?.let { if (it.expires > System.currentTimeMillis() + 60_000) return it }
        session?.let { s ->
            runCatching { apply(send("POST", "auth/v1/token?grant_type=refresh_token", JSONObject().put("refresh_token", s.refresh).toString(), auth = false)) }
                .getOrNull()?.let { return it }
        }
        apply(send("POST", "auth/v1/signup", "{}", auth = false))
    }

    private suspend fun send(method: String, path: String, body: String? = null, auth: Boolean = true): String {
        val token = if (auth) validSession().access else null
        return withContext(Dispatchers.IO) {
            val c = URL("$BASE/$path").openConnection() as HttpURLConnection
            c.requestMethod = method
            c.connectTimeout = 20_000
            c.readTimeout = 20_000
            c.setRequestProperty("apikey", KEY)
            c.setRequestProperty("Content-Type", "application/json")
            if (token != null) c.setRequestProperty("Authorization", "Bearer $token")
            if (body != null) {
                c.doOutput = true
                c.outputStream.use { it.write(body.toByteArray()) }
            }
            val code = c.responseCode
            val text = (if (code in 200..299) c.inputStream else c.errorStream)?.bufferedReader()?.use { it.readText() } ?: ""
            c.disconnect()
            if (code !in 200..299) error("HTTP $code")
            text
        }
    }

    /** 1回目の解答を集計に送る。同じ問題は、この端末から1回だけ。 */
    suspend fun recordFirstAttempt(id: String, correct: Boolean) {
        val done = Store.prefs.getStringSet("stats.recorded", emptySet())!!.toMutableSet()
        if (id in done) return
        val body = JSONObject().put("p_key", id).put("p_correct", correct).toString()
        if (runCatching { send("POST", "rest/v1/rpc/record_attempt", body) }.isSuccess) {
            done += id
            Store.prefs.edit().putStringSet("stats.recorded", done).apply()
        }
    }

    /** すべての問題の集計をまとめて取る（難しさの評価に使う）。 */
    suspend fun allStats(): Map<String, List<Int>>? = runCatching {
        val arr = JSONArray(send("GET", "rest/v1/problem_stats?select=problem_key,shown,correct&limit=20000"))
        (0 until arr.length()).associate { i ->
            val o = arr.getJSONObject(i)
            o.getString("problem_key") to listOf(o.getInt("shown"), o.getInt("correct"))
        }
    }.getOrNull()

    suspend fun stats(id: String): Pair<Int, Int>? = runCatching {
        val q = URLEncoder.encode("eq.$id", "UTF-8")
        val arr = JSONArray(send("GET", "rest/v1/problem_stats?select=shown,correct&problem_key=$q"))
        if (arr.length() == 0) null else arr.getJSONObject(0).let { it.getInt("shown") to it.getInt("correct") }
    }.getOrNull()
}
