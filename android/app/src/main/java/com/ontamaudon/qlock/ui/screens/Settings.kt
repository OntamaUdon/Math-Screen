package com.ontamaudon.qlock.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.BuildConfig
import com.ontamaudon.qlock.MainActivity
import com.ontamaudon.qlock.billing.Billing
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.ParentLock
import com.ontamaudon.qlock.data.ParentLockAuth
import com.ontamaudon.qlock.data.Store
import com.ontamaudon.qlock.guard.Permissions
import com.ontamaudon.qlock.ui.Card
import com.ontamaudon.qlock.ui.Divider
import com.ontamaudon.qlock.ui.IsoTextButton
import com.ontamaudon.qlock.ui.SectionLabel
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.components.Confirm
import com.ontamaudon.qlock.ui.components.PasscodeSetup
import com.ontamaudon.qlock.ui.components.ShareSetting
import com.ontamaudon.qlock.ui.components.Sheet
import com.ontamaudon.qlock.ui.components.Toggle
import com.ontamaudon.qlock.ui.components.findActivity
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/** 利用規約とプライバシーポリシー（Android 版のページ。GitHub Pages で公開する）。 */
object LegalLinks {
    const val TERMS = "https://ontamaudon.github.io/Math-Screen/android/terms.html"
    const val PRIVACY = "https://ontamaudon.github.io/Math-Screen/android/privacy.html"
}

@Composable
fun SettingsScreen() {
    val ctx = LocalContext.current
    var confirmEmergency by remember { mutableStateOf(false) }
    var showGuide by remember { mutableStateOf(false) }
    var showDiagnostics by remember { mutableStateOf(false) }
    var showPasscodeSetup by remember { mutableStateOf(false) }
    var showDisclosure by remember { mutableStateOf(false) }
    var showLicense by remember { mutableStateOf(false) }
    var confirmClear by remember { mutableStateOf(false) }
    var tick by remember { mutableIntStateOf(0) }
    val m = AppModel
    DisposableEffect(Unit) { onDispose { ParentLock.lock() } }
    fun open(url: String) = runCatching { ctx.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }

    Screen("設定") {
        if (ParentLock.needsLock) {
            Card {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Icon(Icons.Filled.Lock, null, tint = Theme.ink, modifier = Modifier.size(18.dp))
                        T("保護者用", 17, W.heavy)
                    }
                    T("設定は、パスコードを知っている人だけが開けます。", 14, color = Theme.inkSoft)
                    IsoTextButton("パスコードを入れる", { ParentLock.request { tick++ } })
                }
            }
            return@Screen
        }
        @Suppress("UNUSED_VARIABLE") val t = tick

        Group("解くロックプラン", "問題を見る・解くことと、記録は無料です。アプリロックなどは、解くロックプランで使えます。初めての方は、7日間無料です。") {
            Value("いまのプラン", if (m.isPremium) "解くロックプラン" else "無料", if (m.isPremium) Theme.tealDeep else Theme.inkSoft)
            Divider(Modifier.padding(start = 18.dp))
            Action(if (Billing.isSubscribed) "プランの管理（解約など）" else "プランを見る", Theme.tealDeep) {
                if (Billing.isSubscribed) Billing.openManage(ctx) else m.showPlan = true
            }
            Divider(Modifier.padding(start = 18.dp))
            Action("購入を復元", Theme.tealDeep) { Billing.restore() }
            if (BuildConfig.DEBUG) {      // 開発用のビルドだけ。商品を登録する前に、自分で試すため
                Divider(Modifier.padding(start = 18.dp))
                Action(if (Store.testPremium) "テスト用：無料で使うをやめる" else "テスト用：無料で使う（開発用のビルドだけ）", Theme.inkSoft) {
                    m.setTestPremium(!Store.testPremium)
                }
            }
        }

        if (m.isPremium) {
            Group("保護者用設定", "オンにすると、ルールの変更・設定・プランの管理に、パスコードが必要になります。お子さんが知らない4桁の数字にしてください。この設定は、設定の画面の中にあるので、パスコードを知らないと、オフにできません。4回まちがえると、しばらく入力できなくなります。パスコードは、この端末の中だけに保存されます。") {
                ToggleRow("保護者用設定", ParentLock.isEnabled) { on ->
                    if (on) { if (ParentLock.hasPasscode) ParentLock.setEnabled(true) else showPasscodeSetup = true }
                    else ParentLock.setEnabled(false)
                }
                Divider(Modifier.padding(start = 18.dp))
                if (ParentLock.hasPasscode) {
                    Action("パスコードを変える", Theme.tealDeep) { showPasscodeSetup = true }
                    Divider(Modifier.padding(start = 18.dp))
                    Action("パスコードを消す", Theme.danger) { confirmClear = true }
                } else {
                    Action("パスコードを決める", Theme.tealDeep) { showPasscodeSetup = true }
                }
            }
        }

        Group("問題の共有", "「分からない」や、正解したあとに、問題の画像を X や LINE などで共有できます。答えと解説は入りません。保護者用設定をオンにすると、最初はオフになります。") {
            ToggleRow("問題を共有できる", ShareSetting.isAllowed) { ShareSetting.set(it); tick++ }
        }

        Group("見守り（ユーザー補助）", checkedFooter(m.guardEnabled)) {
            Value("見守り", if (m.guardEnabled) "オン" else "オフ", if (m.guardEnabled) Theme.tealDeep else Theme.danger)
            Divider(Modifier.padding(start = 18.dp))
            Action(if (m.guardEnabled) "ユーザー補助の設定を開く" else "オンにする", Theme.tealDeep) {
                if (m.guardEnabled) Permissions.openAccessibilitySettings(ctx) else showDisclosure = true
            }
        }

        Group("ロック画面", "ロックがかかっている間に画面をつけると、端末のロック画面の上に問題が出ます。端末のロックを外さずに答えられます。アプリを使うときは、ふだんどおり端末のロックを外します。") {
            ToggleRow("ロック画面の上に問題を出す", Store.lockScreenChallenge) { Store.lockScreenChallenge = it; tick++ }
        }

        Group("通知", "ロックがかかったときに、問題が届いたことを知らせます。通知をタップすると、ロック画面の上でも問題を開けます。") {
            Value("通知", if (m.notificationsAllowed) "許可済み" else "オフ", if (m.notificationsAllowed) Theme.tealDeep else Theme.inkSoft)
            if (!m.notificationsAllowed) {
                Divider(Modifier.padding(start = 18.dp))
                Action("許可する", Theme.tealDeep) {
                    (ctx.findActivity() as? MainActivity)?.requestNotifications() ?: Permissions.openNotificationSettings(ctx)
                }
            }
        }

        Group("もしものとき", "制限中でも、電話などの Android の基本の機能は使えます。どうしても必要なときは、問題を解かずに解除できます（記録に残ります）。") {
            Action("緊急解除", if (m.isLocked) Theme.danger else Theme.inkFaint, enabled = m.isLocked) { confirmEmergency = true }
        }

        Group("規約など") {
            Link("利用規約") { open(LegalLinks.TERMS) }
            Divider(Modifier.padding(start = 18.dp))
            Link("プライバシーポリシー") { open(LegalLinks.PRIVACY) }
        }

        Group("このアプリについて") {
            Link("使い方を見る") { showGuide = true }
            Divider(Modifier.padding(start = 18.dp))
            Link("診断") { showDiagnostics = true }
            Divider(Modifier.padding(start = 18.dp))
            Link("ライセンス") { showLicense = true }
            Divider(Modifier.padding(start = 18.dp))
            Value("バージョン", BuildConfig.VERSION_NAME, Theme.inkSoft)
        }
    }

    if (confirmEmergency) Confirm("緊急解除しますか？", "問題を解かずにすべての制限を外します。記録には「緊急解除」として残ります。",
        buttons = listOf("緊急解除する" to { m.emergencyUnlock() }), cancel = "緊急解除しない", destructiveFirst = true) { confirmEmergency = false }
    if (confirmClear) Confirm("パスコードを消しますか？", buttons = listOf("消す" to { ParentLock.clearPasscode() }), destructiveFirst = true) { confirmClear = false }
    if (showGuide) Sheet({ showGuide = false }) { Onboarding(replay = true, onClose = { showGuide = false }) }
    if (showDiagnostics) Sheet({ showDiagnostics = false }) { Diagnostics { showDiagnostics = false } }
    if (showPasscodeSetup) Sheet({ showPasscodeSetup = false }) { PasscodeSetup { showPasscodeSetup = false } }
    if (showLicense) Sheet({ showLicense = false }) { License { showLicense = false } }
    if (showDisclosure) Sheet({ showDisclosure = false }) {
        GuardDisclosureSheet(onAgree = { showDisclosure = false; Permissions.openAccessibilitySettings(ctx) }, onDecline = { showDisclosure = false })
    }
}

private fun checkedFooter(enabled: Boolean): String? {
    val checked = ParentLockAuth.checkedAt ?: return null
    val f = SimpleDateFormat("M/d H:mm", Locale.JAPAN)
    var t = "アプリを開いたときに確かめています。最後に確かめたのは ${f.format(Date(checked))} です。"
    if (!enabled) ParentLockAuth.approvedAt?.let { t += "オンだったのを最後に確かめられたのは ${f.format(Date(it))} です。" }
    return t
}

@Composable
private fun Group(title: String, footer: String? = null, content: @Composable () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        SectionLabel(title)
        Card(padding = 0.dp) { Column { content() } }
        footer?.let { T(it, 12, color = Theme.inkSoft) }
    }
}

@Composable
private fun Value(title: String, value: String, color: Color) {
    Row(Modifier.fillMaxWidth().padding(horizontal = 18.dp, vertical = 14.dp), verticalAlignment = Alignment.CenterVertically) {
        T(title, 16, modifier = Modifier.weight(1f))
        T(value, 15, W.semibold, color)
    }
}

@Composable
private fun Action(title: String, color: Color, enabled: Boolean = true, run: () -> Unit) {
    T(title, 16, W.semibold, color, Modifier.fillMaxWidth().clickable(enabled = enabled, onClick = run).padding(horizontal = 18.dp, vertical = 14.dp))
}

@Composable
private fun Link(title: String, run: () -> Unit) {
    Row(Modifier.fillMaxWidth().clickable(onClick = run).padding(horizontal = 18.dp, vertical = 14.dp), verticalAlignment = Alignment.CenterVertically) {
        T(title, 16, modifier = Modifier.weight(1f))
        Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Theme.inkFaint, modifier = Modifier.size(18.dp))
    }
}

@Composable
private fun ToggleRow(title: String, on: Boolean, onChange: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth().padding(horizontal = 18.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
        T(title, 16, modifier = Modifier.weight(1f))
        Toggle(on, onChange)
    }
}

@Composable
private fun License(onClose: () -> Unit) {
    val ctx = LocalContext.current
    val text = remember { runCatching { ctx.assets.open("licenses/OFL-MPLUSRounded1c.txt").bufferedReader().use { it.readText() } }.getOrDefault("") }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp).padding(bottom = 32.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)) {
        SheetHeader("ライセンス", onAction = onClose)
        T("数式の表示：KaTeX（MIT License）", 14, W.semibold)
        T("文字：M PLUS Rounded 1c（SIL Open Font License 1.1）", 14, W.semibold)
        T(text, 11, color = Theme.inkSoft)
    }
}
