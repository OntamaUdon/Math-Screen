package com.ontamaudon.qlock

import android.app.KeyguardManager
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.ParentLock
import com.ontamaudon.qlock.ui.components.PasscodeEntry
import com.ontamaudon.qlock.ui.components.Sheet
import com.ontamaudon.qlock.ui.screens.ChallengeScreen
import com.ontamaudon.qlock.ui.screens.PlanScreen

/**
 * 問題の画面。制限したアプリの上に出す（ユーザー補助サービスから開く）。端末のロック画面の上にも出せる。
 * 解かずに閉じると、ホーム画面に戻る（制限したアプリは使えないまま）。
 */
class ChallengeActivity : ComponentActivity() {
    private var lockScreen by mutableStateOf(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        if (Build.VERSION.SDK_INT >= 27) setShowWhenLocked(true)
        else @Suppress("DEPRECATION") window.addFlags(WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED)
        updateLockState()
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() = leave()
        })
        setContent {
            ChallengeScreen(onLockScreen = lockScreen, onLeave = ::leave, onUnlocked = ::unlocked)
            if (AppModel.showPlan) Sheet({ AppModel.showPlan = false }) { PlanScreen(onClose = { AppModel.showPlan = false }) }
            if (ParentLock.showEntry) Sheet({ ParentLock.cancelEntry() }) { PasscodeEntry() }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        updateLockState()
    }

    override fun onResume() {
        super.onResume()
        updateLockState()
        AppModel.refresh()
    }

    private fun updateLockState() {
        lockScreen = getSystemService(KeyguardManager::class.java)?.isKeyguardLocked == true
    }

    /** 解かずに閉じる。ロック画面の上なら、ロック画面に戻る。そうでなければ、ホーム画面へ。 */
    private fun leave() {
        if (!lockScreen && AppModel.isLocked) {
            startActivity(Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        }
        finish()
    }

    /** 正解して解除した。ロック画面の上なら、端末のロックを外してもらってから閉じる（もとのアプリに戻る）。 */
    private fun unlocked() {
        val km = getSystemService(KeyguardManager::class.java)
        if (km != null && km.isKeyguardLocked && Build.VERSION.SDK_INT >= 26) {
            km.requestDismissKeyguard(this, object : KeyguardManager.KeyguardDismissCallback() {
                override fun onDismissSucceeded() = finish()
                override fun onDismissCancelled() = finish()
                override fun onDismissError() = finish()
            })
        } else {
            finish()
        }
    }

    companion object {
        const val EXTRA_LOCK_SCREEN = "lockScreen"
    }
}
