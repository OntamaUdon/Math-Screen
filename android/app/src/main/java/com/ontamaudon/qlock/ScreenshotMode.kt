package com.ontamaudon.qlock

import com.ontamaudon.qlock.data.DailyStats
import com.ontamaudon.qlock.data.GuardRule
import com.ontamaudon.qlock.data.MasteryStore
import com.ontamaudon.qlock.data.ProblemBank
import com.ontamaudon.qlock.data.ProblemMark
import com.ontamaudon.qlock.data.ProblemMarkStore
import com.ontamaudon.qlock.data.Store
import java.util.Calendar

/**
 * スクリーンショット用（デバッグ版だけ）。起動のときに `--es screenshot home` のように渡す（ほかに book / solve / stats / plan / settings / onboarding / challenge）。
 * 画面はすべて本物。見せるための見本のデータだけを入れる（iPhone 版の ScreenshotMode と同じ内容）。
 */
object ScreenshotMode {
    var scene: String? = null
        private set
    val active: Boolean get() = scene != null

    fun start(s: String?) {
        if (!BuildConfig.DEBUG || s == null || scene == s) return
        scene = s
        seed(s)
    }

    private fun seed(s: String) {
        val pattern = listOf(3, 7, 5, 10, 8, 4, 6, 9, 2, 10, 7, 5, 8, 6, 10, 4, 9, 7, 3, 8, 10, 5, 6)
        val daily = HashMap<String, DailyStats>()
        var n = 0
        for (back in 7 * 8 - 1 downTo 0) {
            val c = Calendar.getInstance().apply { add(Calendar.DAY_OF_MONTH, -back) }
            val v = pattern[n % pattern.size] - if (back > 7 * 4) 2 else 0
            n++
            if (v <= 0) continue
            daily[Store.dayKey(c.time)] = DailyStats(2, 2, v, v + 2, 0)
        }
        Store.saveDaily(daily)
        Store.currentStreak = 8
        Store.hasOnboarded = s != "onboarding"
        if (s == "home" || s == "challenge") {
            val a = GuardRule(packages = setOf("com.android.chrome", "com.google.android.youtube", "com.android.settings"), thresholdMinutes = 30, questionCount = 1)
            val b = GuardRule(packages = setOf("com.google.android.apps.photos"), thresholdMinutes = 60, questionCount = 2)
            Store.saveRules(listOf(a, b))
            Store.lockedRuleIDs = setOf(a.id)
            Store.saveUsage(mapOf(b.id to 23 * 60_000L))
        }
        val plan = listOf("e_calc" to listOf(true, true, true), "e_decfrac" to listOf(true, true, false), "m_signed" to listOf(true, true, true),
            "m_linear" to listOf(true, false, true), "m_sqrt" to listOf(true, false))
        for ((unit, results) in plan) {
            val ps = ProblemBank.all.filter { it.unit == unit }
            results.forEachIndexed { i, r ->
                if (i < ps.size) {
                    MasteryStore.record(ps[i], r)
                    ProblemMarkStore.record(ps[i].id, if (r) ProblemMark.perfect else ProblemMark.once)
                }
            }
        }
    }
}
