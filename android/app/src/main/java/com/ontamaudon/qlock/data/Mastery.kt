package com.ontamaudon.qlock.data

import kotlinx.serialization.Serializable
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.builtins.MapSerializer
import kotlinx.serialization.builtins.serializer
import kotlinx.serialization.json.Json
import kotlin.math.exp
import kotlin.math.min
import kotlin.random.Random

/** 単元のできぐあい。 */
enum class MasteryLevel(val label: String) {
    none("未学習"), learning("練習中"), good("得意"), complete("完成")
}

data class UnitProgress(val count: Int, val score: Double, val level: MasteryLevel)

/** 問題ごと・単元ごとの「1回目の解答」の記録（iPhone 版の MasteryStore と同じ）。 */
object MasteryStore {
    @Serializable
    data class Schedule(var streak: Int, var due: Double, var last: Double)

    @Serializable
    private data class Stored(
        val unit: MutableMap<String, List<Boolean>> = mutableMapOf(),
        val problem: MutableMap<String, List<Boolean>> = mutableMapOf(),
        val sched: MutableMap<String, Schedule> = mutableMapOf(),
        val fam: MutableMap<String, Double> = mutableMapOf(),
    )

    private val intervalDays = listOf(1.0, 3.0, 7.0, 14.0, 30.0, 60.0, 120.0)
    private const val RELEARN_DELAY = 3600.0
    const val WINDOW = 3
    private val json = Json { ignoreUnknownKeys = true }
    private var data: Stored = Store.prefs.getString("mastery.v1", null)
        ?.let { runCatching { json.decodeFromString(Stored.serializer(), it) }.getOrNull() } ?: Stored()

    /** 変わるたびに増える（画面の読み直し用）。 */
    var version = 0
        private set

    private fun now() = System.currentTimeMillis() / 1000.0

    @Synchronized
    fun record(problem: Problem, firstTryCorrect: Boolean) {
        problem.unit?.let { u -> data.unit[u] = ((data.unit[u] ?: emptyList()) + firstTryCorrect).takeLast(WINDOW) }
        data.problem[problem.id] = ((data.problem[problem.id] ?: emptyList()) + firstTryCorrect).takeLast(5)
        val n = now()
        val s = data.sched[problem.id] ?: Schedule(0, n, n)
        if (firstTryCorrect) {
            s.streak += 1
            s.due = n + intervalDays[min(s.streak - 1, intervalDays.size - 1)] * 86400
        } else {
            s.streak = 0
            s.due = n + RELEARN_DELAY
        }
        s.last = n
        problem.family?.let { data.fam[it] = n }
        data.sched[problem.id] = s
        Store.prefs.edit().putString("mastery.v1", json.encodeToString(Stored.serializer(), data)).apply()
        version++
    }

    fun progress(unit: String): UnitProgress {
        val r = (data.unit[unit] ?: emptyList()).takeLast(WINDOW)
        if (r.isEmpty()) return UnitProgress(0, 0.0, MasteryLevel.none)
        val score = r.count { it }.toDouble() / r.size
        val level = when {
            r.size < WINDOW -> MasteryLevel.learning
            score >= 1 -> MasteryLevel.complete
            score >= 0.6 -> MasteryLevel.good
            else -> MasteryLevel.learning
        }
        return UnitProgress(r.size, score, level)
    }

    fun familyAge(p: Problem): Double? {
        val f = p.family ?: return null
        val t = data.fam[f] ?: return null
        return now() - t
    }

    fun schedule(id: String): Schedule? = data.sched[id]
}

/** 出す問題の選び方（iPhone 版の Adaptive と同じ）。 */
object Adaptive {
    fun pick(categories: Set<String>, units: Set<String>, excluding: String? = null): Problem? {
        val store = MasteryStore
        var pool = ProblemBank.all.filter { it.category in categories && (units.isEmpty() || (it.unit ?: "") in units) }
        if (pool.isEmpty()) pool = ProblemBank.all.filter { it.category in categories }
        if (pool.isEmpty()) return ProblemBank.pick(categories, excluding)

        val now = System.currentTimeMillis() / 1000.0
        val lastUnitKey = "adaptive.lastUnit"

        // 0) 復習の時期がきた問題を、一定の確率で先に出す
        val due = pool.filter { p -> p.id != excluding && (store.schedule(p.id)?.let { it.due <= now } ?: false) }
        if (due.isNotEmpty() && Random.nextDouble() < min(0.5, 0.2 + 0.05 * min(due.size, 6))) {
            val weighted = due.map { p ->
                val s = store.schedule(p.id)!!
                val overdueDays = min((now - s.due) / 86400, 14.0)
                p to (1 + overdueDays / 7 + if (s.streak == 0) 1 else 0)
            }
            choose(weighted)?.let { c ->
                Store.appendRecent(c.id)
                c.unit?.let { Store.prefs.edit().putString(lastUnitKey, it).apply() }
                return c
            }
        }

        val byUnit = pool.groupBy { it.unit ?: "" }
        val auto = units.isEmpty()
        val lastUnit = Store.prefs.getString(lastUnitKey, null)

        // 1) 単元を選ぶ
        val unitWeights = byUnit.keys.map { uid ->
            var w = when (store.progress(uid).level) {
                MasteryLevel.none -> 1.0
                MasteryLevel.learning -> 1.6
                MasteryLevel.good -> 0.6
                MasteryLevel.complete -> 0.15
            }
            val info = UnitCatalog.info(uid)
            if (auto && info != null && info.prereqs.any { byUnit[it] != null && store.progress(it).level.ordinal < MasteryLevel.good.ordinal }) w *= 0.1
            if (auto && info?.stage == "ノンジャンル") w *= 0.25
            if (byUnit.size > 1 && uid == lastUnit) w *= 0.5
            uid to w
        }
        val unit = choose(unitWeights) ?: return null
        val list = byUnit[unit] ?: return null
        Store.prefs.edit().putString(lastUnitKey, unit).apply()

        // 2) その単元の中で、いまの力に合う難しさの問題を選ぶ
        val pr = store.progress(unit)
        val ability = if (pr.count < 3) 0.0 else pr.score
        val targetRate = 0.9 - 0.35 * ability
        val cands = list.filter { it.id != excluding }.ifEmpty { list }
        val recent = Store.recentProblemIDs.toSet()
        val weighted = cands.map { p ->
            val gap = (DifficultyStore.correctRate(p) - targetRate) / 0.15
            var w = exp(-gap * gap) + 0.02
            val s = store.schedule(p.id)
            w *= if (s != null) (if (s.due <= now) 2.0 else 0.03) else 1.5
            if (p.id in recent) w *= 0.05
            store.familyAge(p)?.let { age ->
                w *= when {
                    age < 86400 -> 0.08
                    age < 3 * 86400 -> 0.3
                    age < 7 * 86400 -> 0.6
                    else -> 1.0
                }
            }
            p to w
        }
        val chosen = choose(weighted)
        chosen?.let { Store.appendRecent(it.id) }
        return chosen
    }

    private fun <T> choose(items: List<Pair<T, Double>>): T? {
        val total = items.sumOf { it.second }
        if (total <= 0) return items.randomOrNull()?.first
        var r = Random.nextDouble() * total
        for ((item, w) in items) {
            r -= w
            if (r < 0) return item
        }
        return items.lastOrNull()?.first
    }
}

/** 問題の難しさ：全員の1発正解率（サーバーの problem_stats）。 */
object DifficultyStore {
    private val mapSer = MapSerializer(String.serializer(), ListSerializer(Int.serializer()))
    private var stats: Map<String, List<Int>> = Store.prefs.getString("difficulty.stats.v1", null)
        ?.let { runCatching { Json.decodeFromString(mapSer, it) }.getOrNull() } ?: emptyMap()

    fun correctRate(p: Problem): Double {
        val prior = p.rate?.let { it / 10 } ?: 0.6
        val s = stats[p.id] ?: listOf(0, 0)
        return (s[1] + 5 * prior) / (s[0] + 5)
    }

    /** 1日に1回、サーバーから集計を取り直す。 */
    suspend fun refreshIfNeeded() {
        val last = Store.prefs.getLong("difficulty.stats.at", 0)
        if (System.currentTimeMillis() - last < 24 * 3600 * 1000L) return
        val all = Community.allStats() ?: return
        stats = all
        Store.prefs.edit()
            .putString("difficulty.stats.v1", Json.encodeToString(mapSer, all))
            .putLong("difficulty.stats.at", System.currentTimeMillis()).apply()
    }
}

/** 問題集に出す、解いた結果の印。 */
enum class ProblemMark(val raw: Int, val symbol: String, val label: String) {
    skipped(1, "△", "解かずに変更"),
    many(2, "〇", "2回以上まちがえて正解"),
    once(3, "◎", "1回まちがえて正解"),
    perfect(4, "☆", "1発正解");

    companion object {
        fun solved(wrongCount: Int) = if (wrongCount == 0) perfect else if (wrongCount == 1) once else many
        fun from(raw: Int) = entries.firstOrNull { it.raw == raw }
    }
}

object ProblemMarkStore {
    private val mapSer = MapSerializer(String.serializer(), Int.serializer())
    private val marks: MutableMap<String, Int> = (Store.prefs.getString("problem.marks.v1", null)
        ?.let { runCatching { Json.decodeFromString(mapSer, it) }.getOrNull() } ?: emptyMap()).toMutableMap()

    fun mark(id: String): ProblemMark? = marks[id]?.let { ProblemMark.from(it) }

    /** いままでより良い結果のときだけ、残す。 */
    @Synchronized
    fun record(id: String, mark: ProblemMark) {
        if ((marks[id] ?: 0) >= mark.raw) return
        marks[id] = mark.raw
        Store.prefs.edit().putString("problem.marks.v1", Json.encodeToString(mapSer, marks)).apply()
    }
}
