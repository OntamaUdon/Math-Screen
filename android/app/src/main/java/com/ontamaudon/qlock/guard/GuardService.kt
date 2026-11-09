package com.ontamaudon.qlock.guard

import android.accessibilityservice.AccessibilityService
import android.app.KeyguardManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Handler
import android.os.Looper
import android.view.accessibility.AccessibilityEvent
import android.view.inputmethod.InputMethodManager
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.Store

/**
 * ユーザー補助サービス。前に出ているアプリの名前（パッケージ名）だけを受け取る。
 * 画面の文字や、入力した内容は読まない（設定の xml で、受け取る情報を絞っている）。
 */
class GuardService : AccessibilityService() {
    private val handler = Handler(Looper.getMainLooper())
    private var ignored: Set<String> = emptySet()

    private val ticker = object : Runnable {
        override fun run() {
            GuardEngine.tick(this@GuardService)
            if (GuardEngine.isWatching(this@GuardService)) handler.postDelayed(this, TICK_MS)
        }
    }

    private val screenReceiver = object : BroadcastReceiver() {
        override fun onReceive(c: Context, intent: Intent) {
            when (intent.action) {
                Intent.ACTION_SCREEN_OFF -> GuardEngine.onScreen(c, false)
                Intent.ACTION_SCREEN_ON -> {
                    // ロック中に画面をつけたら、ロック画面の上に問題を出す（設定でオフにできる）
                    val km = getSystemService(KeyguardManager::class.java)
                    if (km?.isKeyguardLocked == true && AppModel.isPremium && Store.lockedRuleIDs.isNotEmpty() && Store.lockScreenChallenge) {
                        GuardEngine.launchChallenge(c, fromLockScreen = true)
                    }
                }
                // 端末のロックが外れた：最後に前にいたアプリから、また数え始める
                Intent.ACTION_USER_PRESENT -> {
                    GuardEngine.onScreen(c, true)
                    restartTicker()
                }
            }
        }
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        ignored = ignoredPackages()
        val f = IntentFilter().apply {
            addAction(Intent.ACTION_SCREEN_ON)
            addAction(Intent.ACTION_SCREEN_OFF)
            addAction(Intent.ACTION_USER_PRESENT)
        }
        registerReceiver(screenReceiver, f)
        Store.setDiagNote("service", "見守りを始めました")
        AppModel.refresh()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event?.eventType != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) return
        val pkg = event.packageName?.toString() ?: return
        onPackage(pkg)
    }

    private fun onPackage(pkg: String) {
        if (pkg in ignored) return
        GuardEngine.onForeground(this, pkg)
        restartTicker()
    }

    private fun restartTicker() {
        handler.removeCallbacks(ticker)
        if (GuardEngine.isWatching(this)) handler.postDelayed(ticker, TICK_MS)
    }

    /** キーボードと、通知のパネルなどのシステムの画面は、前のアプリが変わったと見なさない。 */
    private fun ignoredPackages(): Set<String> {
        val imes = runCatching {
            getSystemService(InputMethodManager::class.java).enabledInputMethodList.map { it.packageName }
        }.getOrDefault(emptyList())
        return (imes + listOf("com.android.systemui", "android")).toSet()
    }

    override fun onInterrupt() {}

    override fun onDestroy() {
        handler.removeCallbacks(ticker)
        runCatching { unregisterReceiver(screenReceiver) }
        GuardEngine.onScreen(this, false)
        Store.setDiagNote("service", "見守りが止まりました")
        super.onDestroy()
    }

    companion object {
        private const val TICK_MS = 10_000L
    }
}
