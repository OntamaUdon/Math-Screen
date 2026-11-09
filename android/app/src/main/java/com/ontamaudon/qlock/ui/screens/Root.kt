package com.ontamaudon.qlock.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.LibraryBooks
import androidx.compose.material.icons.outlined.BarChart
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.ParentLock
import com.ontamaudon.qlock.ui.Divider
import com.ontamaudon.qlock.ui.IsoBackground
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.components.Confirm
import com.ontamaudon.qlock.ui.components.PasscodeEntry
import com.ontamaudon.qlock.ui.components.Sheet

/** いちばん外側（iPhone 版の RootView）。はじめての人には案内、そのあとはタブの画面。 */
@Composable
fun QlockRoot(initialTab: Int = 0) {
    if (AppModel.hasOnboarded) MainTabs(initialTab) else Onboarding(replay = false, onClose = {})

    if (AppModel.showPlan) Sheet({ AppModel.showPlan = false; afterPlan() }) { PlanScreen(onClose = { AppModel.showPlan = false; afterPlan() }) }
    if (AppModel.showParentSetup) Sheet({ AppModel.showParentSetup = false }) { ParentSetupIntro(onClose = { AppModel.showParentSetup = false }) }
    if (ParentLock.showEntry) Sheet({ ParentLock.cancelEntry() }) { PasscodeEntry() }
    AppModel.lastError?.let { e ->
        Confirm(AppModel.alertTitle, e, buttons = emptyList(), cancel = "OK") { AppModel.lastError = null; AppModel.alertTitle = "エラー" }
    }
}

private fun afterPlan() {
    if (AppModel.parentSetupPending) { AppModel.parentSetupPending = false; AppModel.showParentSetup = true }
}

private data class TabItem(val label: String, val icon: ImageVector)

@Composable
fun MainTabs(initial: Int = 0) {
    var tab by rememberSaveable { mutableIntStateOf(initial) }
    LaunchedEffect(tab) { if (tab != 3) ParentLock.lock() }
    val tabs = listOf(TabItem("ホーム", Icons.Outlined.Home), TabItem("問題集", Icons.AutoMirrored.Outlined.LibraryBooks),
        TabItem("記録", Icons.Outlined.BarChart), TabItem("設定", Icons.Outlined.Settings))
    Column(Modifier.fillMaxSize().background(Theme.background)) {
        Box(Modifier.weight(1f)) {
            when (tab) {
                0 -> HomeScreen()
                1 -> ProblemBookScreen()
                2 -> StatsScreen()
                else -> SettingsScreen()
            }
        }
        // 下のタブ（iPhone の TabView の見た目）
        Column(Modifier.fillMaxWidth().background(Theme.surface.copy(alpha = 0.96f)).windowInsetsPadding(WindowInsets.navigationBars)) {
            Divider()
            Row(Modifier.fillMaxWidth().height(54.dp)) {
                tabs.forEachIndexed { i, t ->
                    val on = i == tab
                    Column(Modifier.weight(1f).fillMaxSize().clickable(remember { MutableInteractionSource() }, null) { tab = i },
                        horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                        Icon(t.icon, null, Modifier.size(25.dp), tint = if (on) Theme.tealDeep else Theme.inkFaint)
                        T(t.label, 10, W.medium, if (on) Theme.tealDeep else Theme.inkFaint)
                    }
                }
            }
        }
    }
}

/** 画面共通のスクロール + タイトル（iPhone 版の Screen）。 */
@Composable
fun Screen(title: String, subtitle: String? = null, content: @Composable ColumnScope.() -> Unit) {
    IsoBackground {
        Column(Modifier.fillMaxSize().statusBarsPadding().verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp).padding(bottom = 32.dp), verticalArrangement = Arrangement.spacedBy(20.dp)) {
            Column(Modifier.padding(top = 12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                T(title, 28, W.bold)
                subtitle?.let { T(it, 14, color = Theme.inkSoft) }
            }
            content()
        }
    }
}

/** シートの上の行（タイトル + 閉じる）。 */
@Composable
fun SheetHeader(title: String, size: Int = 22, action: String = "閉じる", actionColor: androidx.compose.ui.graphics.Color = Theme.inkSoft,
                actionWeight: androidx.compose.ui.text.font.FontWeight = W.semibold, actionEnabled: Boolean = true, onAction: () -> Unit) {
    Row(Modifier.fillMaxWidth().padding(top = 24.dp), verticalAlignment = Alignment.CenterVertically) {
        T(title, size, W.bold, modifier = Modifier.weight(1f))
        Box(Modifier.clickable(enabled = actionEnabled, onClick = onAction).padding(8.dp)) { T(action, if (actionWeight == W.bold) 16 else 15, actionWeight, actionColor) }
    }
}
