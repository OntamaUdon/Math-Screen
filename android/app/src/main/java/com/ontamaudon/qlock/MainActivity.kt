package com.ontamaudon.qlock

import android.Manifest
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.billing.Billing
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.ParentLock
import com.ontamaudon.qlock.data.ProblemBank
import com.ontamaudon.qlock.guard.Permissions
import com.ontamaudon.qlock.ui.IsoBackground
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.components.ProblemSolver
import com.ontamaudon.qlock.ui.screens.ChallengeScreen
import com.ontamaudon.qlock.ui.screens.PlanScreen
import com.ontamaudon.qlock.ui.screens.QlockRoot

class MainActivity : ComponentActivity() {
    private val notificationPermission = registerForActivityResult(ActivityResultContracts.RequestPermission()) { AppModel.refresh() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        ScreenshotMode.start(intent.getStringExtra("screenshot"))
        AppModel.refresh()
        setContent {
            when (ScreenshotMode.scene) {
                "plan" -> IsoBackground { Column(Modifier.statusBarsPadding()) { PlanScreen(onClose = {}) } }
                "solve" -> ScreenshotSolve()
                "challenge" -> ChallengeScreen(onLockScreen = false, onLeave = {}, onUnlocked = {})
                "book" -> QlockRoot(initialTab = 1)
                "stats" -> QlockRoot(initialTab = 2)
                "settings" -> QlockRoot(initialTab = 3)
                else -> QlockRoot()
            }
        }
    }

    override fun onResume() {
        super.onResume()
        AppModel.refresh()
        Billing.refresh()
    }

    override fun onStop() {
        super.onStop()
        ParentLock.lock()
    }

    /** 通知の許可を求める（Android 13 以降）。それより前の Android や、一度断られたときは、通知の設定を開く。 */
    fun requestNotifications() {
        if (Build.VERSION.SDK_INT >= 33 && !shouldShowRequestPermissionRationale(Manifest.permission.POST_NOTIFICATIONS) &&
            !Permissions.notificationsAllowed(this) && !getSharedPreferences("qlock", MODE_PRIVATE).getBoolean("notif.asked", false)) {
            getSharedPreferences("qlock", MODE_PRIVATE).edit().putBoolean("notif.asked", true).apply()
            notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
        } else if (Build.VERSION.SDK_INT >= 33 && shouldShowRequestPermissionRationale(Manifest.permission.POST_NOTIFICATIONS)) {
            notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
        } else if (!Permissions.notificationsAllowed(this)) {
            Permissions.openNotificationSettings(this)
        }
    }
}

/** 問題を解く画面（スクリーンショット用）。 */
@Composable
private fun ScreenshotSolve() {
    IsoBackground {
        Column(Modifier.fillMaxSize().statusBarsPadding().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)) {
            T("問題を解く", 24, W.bold, modifier = Modifier.padding(top = 12.dp))
            ProblemBank.find("g01-1")?.let { ProblemSolver(it, onCorrect = {}, continueLabel = "つぎへ", onContinue = {}) }
        }
    }
}
