package com.ontamaudon.qlock

import android.content.Intent
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.GuardRule
import com.ontamaudon.qlock.data.Store

/**
 * 自動の動作確認（GitHub Actions のエミュレーター）のための入口。開発用のビルドだけで動く。
 * 例：adb shell am start -n com.ontamaudon.qlock/.MainActivity --es e2e_rule_pkg com.android.settings --ei e2e_minutes 1
 * → はじめの案内を済ませた状態にして、テスト用のプランをオンにし、そのアプリに「1分ごとに1問」のルールを作る。
 */
object DebugHooks {
    fun apply(intent: Intent?) {
        if (!BuildConfig.DEBUG || intent == null) return
        val pkg = intent.getStringExtra("e2e_rule_pkg") ?: return
        val minutes = intent.getIntExtra("e2e_minutes", 1)
        Store.hasOnboarded = true
        Store.testPremium = true
        Store.saveRules(listOf(GuardRule(packages = setOf(pkg), thresholdMinutes = minutes, questionCount = 1)))
        Store.lockedRuleIDs = emptySet()
        Store.saveUsage(emptyMap())
        Store.setDiagNote("e2e", "テスト用のルールを作りました：$pkg、${minutes}分")
        AppModel.refresh()
    }
}
