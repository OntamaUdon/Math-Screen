package com.ontamaudon.qlock.data

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import com.ontamaudon.qlock.BuildConfig
import com.ontamaudon.qlock.QlockApp
import com.ontamaudon.qlock.ScreenshotMode
import com.ontamaudon.qlock.billing.Billing
import com.ontamaudon.qlock.guard.ChallengeNotification
import com.ontamaudon.qlock.guard.GuardEngine
import com.ontamaudon.qlock.guard.Permissions
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import java.util.Calendar

/** アプリ全体の状態（iPhone 版の AppModel と同じ役目）。画面は、ここの値を見て描く。 */
object AppModel {
    val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    var rules by mutableStateOf<List<GuardRule>>(emptyList())
        private set
    var lockedRuleIDs by mutableStateOf<Set<String>>(emptySet())
        private set
    var daily by mutableStateOf<Map<String, DailyStats>>(emptyMap())
        private set
    var currentStreak by mutableIntStateOf(0)
        private set
    var bestStreak by mutableIntStateOf(0)
        private set
    var hasOnboarded by mutableStateOf(false)
        private set
    var usage by mutableStateOf<Map<String, Long>>(emptyMap())
        private set
    var isPremium by mutableStateOf(false)
        private set
    var guardEnabled by mutableStateOf(false)
        private set       // ユーザー補助サービスがオンか
    var notificationsAllowed by mutableStateOf(false)
        private set
    var showPlan by mutableStateOf(false)
    var showParentSetup by mutableStateOf(false)
    var parentSetupPending = false
    var lastError by mutableStateOf<String?>(null)
    var alertTitle by mutableStateOf("エラー")
    /** 画面の読み直し用（記録や印が変わったとき）。 */
    var tick by mutableIntStateOf(0)
        private set

    fun refresh() {
        scope.launch(Dispatchers.IO) { runCatching { DifficultyStore.refreshIfNeeded() } }
        rules = Store.loadRules()
        lockedRuleIDs = Store.lockedRuleIDs
        daily = Store.loadDaily()
        currentStreak = Store.currentStreak
        bestStreak = Store.bestStreak
        hasOnboarded = Store.hasOnboarded
        usage = Store.loadUsage()
        isPremium = Billing.isSubscribed || (BuildConfig.DEBUG && Store.testPremium) || ScreenshotMode.active
        guardEnabled = Permissions.isGuardServiceEnabled(QlockApp.instance)
        notificationsAllowed = Permissions.notificationsAllowed(QlockApp.instance)
        if (guardEnabled) ParentLockAuth.record(true) else ParentLockAuth.record(false)
        ensurePendingProblem()
        enforcePlan()
        offerParentSetup()
        tick++
    }

    private fun offerParentSetup() {
        val key = "parent.offered"
        if (!isPremium || !hasOnboarded || ScreenshotMode.active || ParentLock.hasPasscode || Store.prefs.getBoolean(key, false)) return
        Store.prefs.edit().putBoolean(key, true).apply()
        if (showPlan) parentSetupPending = true else showParentSetup = true
    }

    /** 契約が切れていたら、すべてのロックを外す（ルールは残す）。契約の状態をまだ確かめていない間は、何もしない。 */
    private fun enforcePlan() {
        if (Billing.state == Billing.State.unknown && !(BuildConfig.DEBUG && Store.testPremium)) return
        if (!isPremium && lockedRuleIDs.isNotEmpty()) {
            for (id in lockedRuleIDs) release(id)
        }
    }

    // MARK: 次に出す問題
    fun ensurePendingProblem() {
        for (rule in rules) ensureRulePending(rule)
        if (pendingProblem != null) return
        val first = rules.firstOrNull()
        val p = first?.let { Store.rulePending(it.id) }?.let { ProblemBank.find(it) }
        setPendingProblem(p ?: Adaptive.pick(Store.defaultCategories, emptySet()))
    }

    private fun ensureRulePending(rule: GuardRule) {
        val p = Store.rulePending(rule.id)?.let { ProblemBank.find(it) }
        if (p != null && p.category in rule.categories && (rule.units.isEmpty() || (p.unit ?: "") in rule.units)) return
        refreshRulePending(rule)
    }

    private fun refreshRulePending(rule: GuardRule, excluding: String? = null) {
        val p = Adaptive.pick(rule.categories, rule.units, excluding) ?: return
        Store.setRulePending(rule.id, p.id)
    }

    val lockedRules: List<GuardRule> get() = rules.filter { it.id in lockedRuleIDs }
    val isLocked: Boolean get() = lockedRuleIDs.isNotEmpty()
    val requiredCorrect: Int get() = maxOf(1, lockedRules.maxOfOrNull { it.questionCount } ?: 1)
    val today: DailyStats get() = daily[Store.dayKey()] ?: DailyStats()

    val challengeUnits: Set<String>
        get() = if (lockedRules.any { it.units.isEmpty() }) emptySet() else lockedRules.flatMap { it.units }.toSet()

    val challengeCategories: Set<String>
        get() = lockedRules.flatMap { it.categories }.toSet().ifEmpty { Store.defaultCategories }

    val pendingProblem: Problem? get() = Store.pendingProblemID?.let { ProblemBank.find(it) }

    fun setPendingProblem(p: Problem?) { Store.pendingProblemID = p?.id }

    fun finishOnboarding() {
        Store.hasOnboarded = true
        hasOnboarded = true
    }

    // MARK: ルール
    fun save(input: GuardRule) {
        var rule = input.copy(packages = input.packages - QlockApp.instance.packageName)
        val current = rules.toMutableList()
        // 同じ条件のルールがすでにあれば、アプリを足して1つにまとめる
        val i = current.indexOfFirst {
            it.id != rule.id && it.thresholdMinutes == rule.thresholdMinutes && it.questionCount == rule.questionCount &&
                it.categories == rule.categories && it.units == rule.units
        }
        if (i >= 0) {
            val target = current[i]
            val merged = target.copy(packages = target.packages + rule.packages, appCategories = target.appCategories + rule.appCategories)
            if (current.any { it.id == rule.id }) {
                release(rule.id)
                Store.setRulePending(rule.id, null)
                current.removeAll { it.id == rule.id }
            }
            rule = merged
        }
        val j = current.indexOfFirst { it.id == rule.id }
        if (j >= 0) current[j] = rule else current.add(rule)
        rules = current
        Store.saveRules(current)
        ensureRulePending(rule)
        if (!rule.isEnabled) release(rule.id)
        Store.clearUsage(rule.id)
        refresh()
    }

    fun delete(rule: GuardRule) {
        release(rule.id)
        Store.setRulePending(rule.id, null)
        rules = rules.filter { it.id != rule.id }
        Store.saveRules(rules)
        Store.clearUsage(rule.id)
        refresh()
    }

    fun setEnabled(rule: GuardRule, enabled: Boolean) = save(rule.copy(isEnabled = enabled))

    private fun release(id: String) {
        Store.markUnlocked(id)
        lockedRuleIDs = Store.lockedRuleIDs
    }

    // MARK: 解答の記録
    fun recordAnswer(correct: Boolean) {
        Store.updateToday { it.copy(attempts = it.attempts + 1, correct = it.correct + if (correct) 1 else 0) }
        Store.currentStreak = if (correct) Store.currentStreak + 1 else 0
        refresh()
    }

    /** 規定数に正解した：すべてのロックを外し、カウントを 0 に戻す。 */
    fun completeChallenge() {
        unlockAll()
        Store.updateToday { it.copy(unlocks = it.unlocks + 1) }
        refresh()
    }

    /** 緊急解除（記録には残る）。 */
    fun emergencyUnlock() {
        unlockAll()
        Store.updateToday { it.copy(emergencyUnlocks = it.emergencyUnlocks + 1) }
        refresh()
    }

    private fun unlockAll() {
        for (id in lockedRuleIDs) {
            release(id)
            Store.clearUsage(id)
            rules.firstOrNull { it.id == id }?.let { refreshRulePending(it, Store.rulePending(it.id)) }
        }
        GuardEngine.resetClock()
        ChallengeNotification.cancel(QlockApp.instance)
        Store.pendingProblemID = null
        ensurePendingProblem()
    }

    // MARK: テスト用（デバッグ版だけ）
    fun setTestPremium(on: Boolean) {
        Store.testPremium = on
        refresh()
    }

    // MARK: 集計
    /** 月曜はじまりの週ごとの正解数。[0] が今週。まだ来ていない日は null。 */
    fun weeklyCorrect(weeks: Int): List<List<Int?>> {
        val cal = Calendar.getInstance()
        val now = cal.time
        cal.firstDayOfWeek = Calendar.MONDAY
        val dow = (cal.get(Calendar.DAY_OF_WEEK) + 5) % 7          // 月曜=0
        cal.add(Calendar.DAY_OF_MONTH, -dow)
        val weekStart = cal.time
        return (0 until maxOf(weeks, 1)).map { k ->
            (0 until 7).map { d ->
                val c = Calendar.getInstance().apply { time = weekStart; add(Calendar.DAY_OF_MONTH, d - 7 * k) }
                val date = c.time
                if (date.after(now) && Store.dayKey(date) != Store.dayKey(now)) null
                else daily[Store.dayKey(date)]?.correct ?: 0
            }
        }
    }

    const val PREMIUM_WEEKS = 8

    val totals: DailyStats
        get() = daily.values.fold(DailyStats()) { t, d ->
            DailyStats(t.triggers + d.triggers, t.unlocks + d.unlocks, t.correct + d.correct, t.attempts + d.attempts,
                t.emergencyUnlocks + d.emergencyUnlocks)
        }

    /** 1問以上正解した日が今日（または昨日）まで何日続いているか。 */
    val dayStreak: Int
        get() {
            val c = Calendar.getInstance()
            if ((daily[Store.dayKey(c.time)]?.correct ?: 0) == 0) c.add(Calendar.DAY_OF_MONTH, -1)
            var n = 0
            while ((daily[Store.dayKey(c.time)]?.correct ?: 0) > 0) {
                n++
                c.add(Calendar.DAY_OF_MONTH, -1)
            }
            return n
        }

    /** ルールの使った時間（分）。 */
    fun usedMinutes(rule: GuardRule): Int = ((usage[rule.id] ?: 0L) / 60_000L).toInt()
}

/** 見守り（ユーザー補助サービス）がオンだったことを、最後に確かめた時刻の記録（保護者にだけ見せる）。 */
object ParentLockAuth {
    fun record(approved: Boolean) {
        val now = System.currentTimeMillis()
        Store.prefs.edit().putLong("auth.checkedAt", now).apply {
            if (approved) putLong("auth.approvedAt", now)
        }.apply()
    }
    val checkedAt: Long? get() = Store.prefs.getLong("auth.checkedAt", 0).takeIf { it > 0 }
    val approvedAt: Long? get() = Store.prefs.getLong("auth.approvedAt", 0).takeIf { it > 0 }
}
