package com.ontamaudon.qlock.data

import android.content.Context
import android.content.SharedPreferences
import com.ontamaudon.qlock.QlockApp
import kotlinx.serialization.Serializable
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.builtins.MapSerializer
import kotlinx.serialization.builtins.serializer
import kotlinx.serialization.json.Json
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID

/** 見守りのルール。iPhone 版の GuardRule と同じ考え方（アプリの選び方だけ Android 用）。 */
@Serializable
data class GuardRule(
    val id: String = UUID.randomUUID().toString(),
    val packages: Set<String> = emptySet(),      // 制限するアプリ（パッケージ名）
    val appCategories: Set<Int> = emptySet(),    // 制限するアプリの種類（ApplicationInfo.category）
    val thresholdMinutes: Int = 10,              // 何分使うごとに
    val questionCount: Int = 1,                  // 何問出すか
    val categories: Set<String> = ALL_CATEGORIES,// 出題する分野
    val units: Set<String> = emptySet(),         // 出題する単元。空なら「おまかせ」
    val isEnabled: Boolean = true,
) {
    val title: String get() = "${durationText(thresholdMinutes)}ごとに${questionCount}問"
    val itemCount: Int get() = packages.size + appCategories.size

    companion object {
        val MATH_CATEGORIES = setOf("elem", "junior", "math1a", "math2b", "math3c")
        val ALL_CATEGORIES: Set<String> = MATH_CATEGORIES + setOf(
            "eng_word", "eng_sentence", "soc_geo", "soc_hist", "soc_civ", "sci_bio", "sci_chem", "sci_phys", "sci_earth",
            "ja_kanji", "ja_idiom", "ja_classic", "ja_grammar",
            "triv_math", "triv_eng", "triv_soc", "triv_sci", "triv_ja",
        )
        const val MAX_MINUTES = 12 * 60

        /** 例：45 → "45分"、90 → "1時間30分"、120 → "2時間" */
        fun durationText(minutes: Int): String {
            val h = minutes / 60
            val m = minutes % 60
            if (h == 0) return "${m}分"
            return if (m == 0) "${h}時間" else "${h}時間${m}分"
        }
    }
}

/** 1日分の記録。 */
@Serializable
data class DailyStats(
    val triggers: Int = 0,
    val unlocks: Int = 0,
    val correct: Int = 0,
    val attempts: Int = 0,
    val emergencyUnlocks: Int = 0,
)

/** 端末の中に保存するデータ（SharedPreferences）。 */
object Store {
    private val json = Json { ignoreUnknownKeys = true; encodeDefaults = true }
    val prefs: SharedPreferences by lazy { QlockApp.instance.getSharedPreferences("qlock", Context.MODE_PRIVATE) }

    // MARK: ルール
    fun loadRules(): List<GuardRule> = prefs.getString("rules", null)
        ?.let { runCatching { json.decodeFromString(ListSerializer(GuardRule.serializer()), it) }.getOrNull() } ?: emptyList()

    fun saveRules(rules: List<GuardRule>) {
        prefs.edit().putString("rules", json.encodeToString(ListSerializer(GuardRule.serializer()), rules)).apply()
    }

    // MARK: ロック状態
    var lockedRuleIDs: Set<String>
        get() = prefs.getStringSet("locked", emptySet())!!.toSet()
        set(v) { prefs.edit().putStringSet("locked", v).apply() }

    fun markLocked(id: String) { lockedRuleIDs = lockedRuleIDs + id }
    fun markUnlocked(id: String) { lockedRuleIDs = lockedRuleIDs - id }

    // MARK: 使った時間（ミリ秒。ルールごと。正解するか、日付が変わると 0 に戻る）
    private val longMap = MapSerializer(String.serializer(), Long.serializer())

    fun loadUsage(): Map<String, Long> {
        if (prefs.getString("usage.day", null) != dayKey()) return emptyMap()
        return prefs.getString("usage", null)?.let { runCatching { json.decodeFromString(longMap, it) }.getOrNull() } ?: emptyMap()
    }

    fun saveUsage(m: Map<String, Long>) {
        prefs.edit().putString("usage", json.encodeToString(longMap, m)).putString("usage.day", dayKey()).apply()
    }

    fun clearUsage(ruleID: String) { saveUsage(loadUsage() - ruleID) }

    // MARK: ルールごとに用意した「次に出す問題」
    private val strMap = MapSerializer(String.serializer(), String.serializer())

    fun rulePending(ruleID: String): String? =
        prefs.getString("rulePending", null)?.let { runCatching { json.decodeFromString(strMap, it) }.getOrNull() }?.get(ruleID)

    fun setRulePending(ruleID: String, problemID: String?) {
        val m = (prefs.getString("rulePending", null)?.let { runCatching { json.decodeFromString(strMap, it) }.getOrNull() } ?: emptyMap()).toMutableMap()
        if (problemID == null) m.remove(ruleID) else m[ruleID] = problemID
        prefs.edit().putString("rulePending", json.encodeToString(strMap, m)).apply()
    }

    var pendingProblemID: String?
        get() = prefs.getString("pendingProblemID", null)
        set(v) { prefs.edit().putString("pendingProblemID", v).apply() }

    // MARK: 記録
    fun dayKey(date: Date = Date()): String = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(date)

    private val dailyMap = MapSerializer(String.serializer(), DailyStats.serializer())

    fun loadDaily(): Map<String, DailyStats> = prefs.getString("daily", null)
        ?.let { runCatching { json.decodeFromString(dailyMap, it) }.getOrNull() } ?: emptyMap()

    fun saveDaily(all: Map<String, DailyStats>) { prefs.edit().putString("daily", json.encodeToString(dailyMap, all)).apply() }

    fun updateToday(change: (DailyStats) -> DailyStats) {
        val all = loadDaily().toMutableMap()
        val key = dayKey()
        all[key] = change(all[key] ?: DailyStats())
        saveDaily(all)
    }

    var currentStreak: Int
        get() = prefs.getInt("currentStreak", 0)
        set(v) {
            prefs.edit().putInt("currentStreak", v).apply()
            if (v > bestStreak) prefs.edit().putInt("bestStreak", v).apply()
        }
    val bestStreak: Int get() = prefs.getInt("bestStreak", 0)

    /** テスト用（デバッグ版だけ）：お金をかけずにプランを試す。 */
    var testPremium: Boolean
        get() = prefs.getBoolean("testPremium", false)
        set(v) { prefs.edit().putBoolean("testPremium", v).apply() }

    var hasOnboarded: Boolean
        get() = prefs.getBoolean("hasOnboarded", false)
        set(v) { prefs.edit().putBoolean("hasOnboarded", v).apply() }

    /** ロック中に画面をつけたとき、ロック画面の上に問題を出すか。 */
    var lockScreenChallenge: Boolean
        get() = prefs.getBoolean("lockScreenChallenge", true)
        set(v) { prefs.edit().putBoolean("lockScreenChallenge", v).apply() }

    /** 最後に前に出ていたアプリ（見守りのサービスが動き出し直したとき、そこから数え直すため）。 */
    var lastForeground: String?
        get() = prefs.getString("lastForeground", null)
        set(v) { prefs.edit().putString("lastForeground", v).apply() }

    /** 出題の初期設定（ルールがないときに使う分野）。 */
    val defaultCategories: Set<String> get() = GuardRule.MATH_CATEGORIES

    val recentProblemIDs: List<String>
        get() = prefs.getString("recent", null)?.split(",")?.filter { it.isNotEmpty() } ?: emptyList()

    fun appendRecent(id: String) {
        val list = (recentProblemIDs + id).takeLast(500)
        prefs.edit().putString("recent", list.joinToString(",")).apply()
    }

    // MARK: 診断
    fun setDiagNote(key: String, text: String) {
        val t = SimpleDateFormat("M/d HH:mm:ss", Locale.JAPAN).format(Date())
        prefs.edit().putString("diagNote.$key", "$t　$text").apply()
    }
    fun diagNote(key: String): String? = prefs.getString("diagNote.$key", null)
}
