package com.ontamaudon.qlock.guard

import android.content.Context
import android.content.Intent
import android.os.SystemClock
import com.ontamaudon.qlock.ChallengeActivity
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.GuardRule
import com.ontamaudon.qlock.data.Store

/**
 * 使った時間を数えて、ロックをかける（iPhone 版の Monitor 拡張とシールドの役目）。
 * ユーザー補助サービスから、前に出ているアプリが変わるたびに呼ばれる。すべてメインスレッドで動く。
 */
object GuardEngine {
    private var current: String? = null       // いま前に出ているアプリ
    private var since = 0L                     // current を数え始めた時刻（elapsedRealtime）
    private var screenOn = true
    private var lastLaunch = 0L

    /** 前に出ているアプリが変わった。 */
    private fun log(msg: String) { if (com.ontamaudon.qlock.BuildConfig.DEBUG) android.util.Log.d("Qlock", msg) }

    fun onForeground(ctx: Context, pkg: String) {
        log("前のアプリ：$pkg（画面 ${if (screenOn) "オン" else "オフ"}）")
        if (pkg == current) { flush(ctx); return }
        flush(ctx)
        current = pkg
        Store.lastForeground = pkg
        since = SystemClock.elapsedRealtime()
        if (isBlocked(ctx, pkg)) launchChallenge(ctx, fromLockScreen = false)
    }

    /** 画面が消えた（off）／ロックが外れて使える状態になった（on）。前にいたアプリは覚えておく。 */
    fun onScreen(ctx: Context, on: Boolean) {
        flush(ctx)
        screenOn = on
        log("画面：${if (on) "オン" else "オフ"}")
        since = SystemClock.elapsedRealtime()
        val pkg = current
        if (on && pkg != null && isBlocked(ctx, pkg)) launchChallenge(ctx, fromLockScreen = false)
    }

    /**
     * 見守りのサービスが動き出した（オンにした直後や、端末が止めたあとに動き出し直したとき）。
     * 前に出ているアプリは、次に画面が変わるまで分からないので、最後に前にいたアプリから数え始める。
     */
    fun restore(ctx: Context) {
        val pm = ctx.getSystemService(android.os.PowerManager::class.java)
        // 画面がついていれば数える（ロック画面が出ているかどうかは、ここでは確かめない。
        // 確かめると、端末によっては、アプリが前に出ていても「ロック中」と返り、数えなくなるため）
        screenOn = pm?.isInteractive != false
        current = Store.lastForeground
        since = SystemClock.elapsedRealtime()
        val pkg = current
        if (screenOn && pkg != null && isBlocked(ctx, pkg)) launchChallenge(ctx, fromLockScreen = false)
    }

    /** 見守りのサービスが止まる。それまでの時間を足しておく（画面の状態は変えない）。 */
    fun pause(ctx: Context) {
        flush(ctx)
    }

    /** 数え始めの時刻を、いまにする（正解してロックが外れたとき）。 */
    fun resetClock() { since = SystemClock.elapsedRealtime() }

    /** 見守りの対象のアプリが前にいる間、定期的に呼ぶ。 */
    fun tick(ctx: Context) = flush(ctx)

    /** いま前にいるアプリが、どれかのルールの対象か（数えるべきか）。 */
    fun isWatching(ctx: Context): Boolean {
        if (!screenOn) return false
        val pkg = current ?: return false
        return AppModel.isPremium && Store.loadRules().any { it.isEnabled && matches(ctx, it, pkg) }
    }

    fun matches(ctx: Context, rule: GuardRule, pkg: String): Boolean =
        pkg != ctx.packageName && (pkg in rule.packages || (rule.appCategories.isNotEmpty() && AppCatalog.category(ctx, pkg) in rule.appCategories))

    fun isBlocked(ctx: Context, pkg: String): Boolean {
        if (!AppModel.isPremium || pkg == ctx.packageName) return false
        val locked = Store.lockedRuleIDs
        if (locked.isEmpty()) return false
        return Store.loadRules().any { it.id in locked && it.isEnabled && matches(ctx, it, pkg) }
    }

    /** 使った時間を足して、決めた時間に達したルールにロックをかける。 */
    private fun flush(ctx: Context) {
        val pkg = current
        val now = SystemClock.elapsedRealtime()
        val dt = now - since
        since = now
        if (pkg == null || !screenOn || dt <= 0 || !AppModel.isPremium) return
        val rules = Store.loadRules()
        val locked = Store.lockedRuleIDs
        val usage = Store.loadUsage().toMutableMap()
        var changed = false
        var newlyLocked: GuardRule? = null
        for (rule in rules) {
            if (!rule.isEnabled || rule.id in locked || !matches(ctx, rule, pkg)) continue
            val used = (usage[rule.id] ?: 0L) + dt.coerceAtMost(10 * 60_000L)
            usage[rule.id] = used
            changed = true
            if (used >= rule.thresholdMinutes * 60_000L) {
                lock(rule)
                newlyLocked = rule
            }
        }
        if (changed) { Store.saveUsage(usage); log("数えた：$pkg +${dt}ms → ${usage}") }
        AppModel.refresh()
        if (newlyLocked != null) {
            ChallengeNotification.send(ctx,
                title = "${GuardRule.durationText(newlyLocked.thresholdMinutes)}たちました",
                body = "ひと休み。${newlyLocked.questionCount}問解くと再開できます。")
            launchChallenge(ctx, fromLockScreen = false)
        }
    }

    private fun lock(rule: GuardRule) {
        Store.markLocked(rule.id)
        Store.rulePending(rule.id)?.let { Store.pendingProblemID = it }
        Store.updateToday { it.copy(triggers = it.triggers + 1) }
        Store.setDiagNote("lock", "ロックしました：${rule.title}")
    }

    /** 問題の画面を、いちばん前に出す。 */
    fun launchChallenge(ctx: Context, fromLockScreen: Boolean) {
        val now = SystemClock.elapsedRealtime()
        if (now - lastLaunch < 1200) return
        lastLaunch = now
        val i = Intent(ctx, ChallengeActivity::class.java)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NO_ANIMATION)
            .putExtra(ChallengeActivity.EXTRA_LOCK_SCREEN, fromLockScreen)
        runCatching { ctx.startActivity(i) }.onFailure { Store.setDiagNote("launch", "問題の画面を出せませんでした：${it.message}") }
        Store.setDiagNote("launch", if (fromLockScreen) "ロック画面の上に問題を出しました" else "問題の画面を出しました")
    }
}
