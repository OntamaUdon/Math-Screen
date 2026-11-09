package com.ontamaudon.qlock.ui.screens

import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowLeft
import androidx.compose.material.icons.filled.ArrowDownward
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.QuestionMark
import androidx.compose.material.icons.outlined.HourglassEmpty
import androidx.compose.material.icons.outlined.Notifications
import androidx.compose.material.icons.outlined.TouchApp
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.MainActivity
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.ProblemBank
import com.ontamaudon.qlock.guard.Permissions
import com.ontamaudon.qlock.ui.Card
import com.ontamaudon.qlock.ui.IsoBackground
import com.ontamaudon.qlock.ui.IsoTextButton
import com.ontamaudon.qlock.ui.SectionLabel
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.components.MathText
import com.ontamaudon.qlock.ui.components.findActivity
import com.ontamaudon.qlock.ui.slab

/**
 * はじめの説明（4画面）。設定の「使い方を見る」から、あとで見直せる（replay = true）。
 * iPhone 版と同じ流れ。Android では通知を経由しなくてよいので、2枚目の手順と、3枚目の許可の説明が違う。
 */
@Composable
fun Onboarding(replay: Boolean, onClose: () -> Unit) {
    var page by remember { mutableIntStateOf(0) }
    val last = 3
    val ctx = LocalContext.current
    fun go(p: Int) { page = p.coerceIn(0, last) }
    IsoBackground {
        Column(Modifier.fillMaxSize().let { if (replay) it else it.statusBarsPadding().navigationBarsPadding() }
            .padding(horizontal = 24.dp).padding(bottom = 20.dp)
            .pointerInput(Unit) {
                var total = 0f
                detectHorizontalDragGestures(onDragStart = { total = 0f }, onDragEnd = {
                    if (total < -50 && page < last) go(page + 1)
                    if (total > 50 && page > 0) go(page - 1)
                }) { _, d -> total += d }
            },
            verticalArrangement = Arrangement.spacedBy(16.dp)) {
            Row(Modifier.fillMaxWidth().height(32.dp).padding(top = if (replay) 16.dp else 8.dp), verticalAlignment = Alignment.CenterVertically) {
                if (page > 0) Row(Modifier.clickable { go(page - 1) }, verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.AutoMirrored.Filled.KeyboardArrowLeft, null, tint = Theme.inkSoft, modifier = Modifier.size(20.dp))
                    T("もどる", 15, W.semibold, Theme.inkSoft)
                }
                Box(Modifier.weight(1f))
                if (replay) T("とじる", 15, W.semibold, Theme.inkSoft, Modifier.clickable(onClick = onClose))
            }
            Column(Modifier.weight(1f).verticalScroll(rememberScrollState()).padding(bottom = 12.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                when (page) {
                    0 -> Intro()
                    1 -> HowToSolve()
                    2 -> GuardPermission()
                    else -> NotificationPermission()
                }
            }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp, Alignment.CenterHorizontally)) {
                for (i in 0..last) {
                    val w by animateDpAsState(if (i == page) 20.dp else 8.dp, label = "dot")
                    Box(Modifier.width(w).height(6.dp).clip(CircleShape).background(if (i == page) Theme.tealDeep else Theme.line))
                }
            }
            when {
                replay -> if (page < last) IsoTextButton("つぎへ", { go(page + 1) }) else IsoTextButton("とじる", onClose)
                page < 2 -> IsoTextButton("つぎへ", { go(page + 1) })
                page == 2 -> {
                    IsoTextButton("同意して設定を開く", { Permissions.openAccessibilitySettings(ctx); go(3) })
                    T("同意しない（あとで）", 15, W.semibold, Theme.inkSoft, Modifier.fillMaxWidth().clickable { go(3) }.padding(4.dp),
                        align = androidx.compose.ui.text.style.TextAlign.Center)
                }
                else -> {
                    IsoTextButton("通知を許可してはじめる", {
                        (ctx.findActivity() as? MainActivity)?.requestNotifications()
                        AppModel.finishOnboarding()
                    })
                    T("あとで", 15, W.semibold, Theme.inkSoft, Modifier.fillMaxWidth().clickable { AppModel.finishOnboarding() }.padding(4.dp),
                        align = androidx.compose.ui.text.style.TextAlign.Center)
                }
            }
        }
    }
}

@Composable
private fun PageIcon(icon: ImageVector) {
    Box(Modifier.padding(bottom = 6.dp).size(70.dp).slab(Theme.teal, Theme.tealDeep, 6.dp, 12.dp).padding(end = 6.dp, bottom = 6.dp),
        contentAlignment = Alignment.Center) {
        Icon(icon, null, tint = Color.White, modifier = Modifier.size(32.dp))
    }
}

@Composable
private fun Intro() {
    PageIcon(Icons.Filled.QuestionMark)
    T("スマホの使い過ぎをとめよう", 26, W.bold)
    T("アプリを使い過ぎるとロックされ、問題が出題されます。見事問題に正解したら、またアプリを使えるようになります！", 16, color = Theme.inkSoft)
    SectionLabel("例題")
    for (id in listOf("j06", "b07")) {
        val p = ProblemBank.find(id) ?: continue
        Card(padding = 14.dp) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                T(p.categoryInfo.label, 12, W.semibold, Theme.inkSoft)
                MathText(p.body, 16, spoken = p.plain)
                T("答え：${p.answerText}", 13, W.semibold, Theme.tealDeep)
            }
        }
    }
    T("数学以外の科目の問題も出題できます。", 13, color = Theme.inkSoft)
}

@Composable
private fun HowToSolve() {
    PageIcon(Icons.Outlined.TouchApp)
    T("問題を解く手順", 26, W.bold)
    val steps = listOf(
        Triple(Icons.Filled.Lock, "時間になると、問題が出る", "使っていたアプリの上に、問題の画面が出る"),
        Triple(Icons.Filled.Edit, "問題に答える", "答えを入力（または選択）して「こたえる」"),
        Triple(Icons.Filled.Check, "正解すると再開", "そのまま、もとのアプリに戻れる"),
    )
    Card(padding = 16.dp) {
        Column {
            steps.forEachIndexed { i, (icon, title, detail) ->
                val lastStep = i == steps.lastIndex
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                    Box(Modifier.size(57.dp).slab(if (lastStep) Theme.coral else Theme.teal, if (lastStep) Theme.coralDeep else Theme.tealDeep, 5.dp, 10.dp)
                        .padding(end = 5.dp, bottom = 5.dp), contentAlignment = Alignment.Center) {
                        Icon(icon, null, tint = Color.White, modifier = Modifier.size(22.dp))
                    }
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        T("${i + 1}　$title", 16, W.bold)
                        T(detail, 13, color = Theme.inkSoft)
                    }
                }
                if (!lastStep) Box(Modifier.width(52.dp).padding(vertical = 4.dp), contentAlignment = Alignment.Center) {
                    Icon(Icons.Filled.ArrowDownward, null, tint = Theme.inkFaint, modifier = Modifier.size(16.dp))
                }
            }
        }
    }
    T("端末のロック画面の上でも、問題に答えられます（設定で切りかえられます）。", 13, color = Theme.inkSoft)
}

@Composable
private fun GuardPermission() {
    PageIcon(Icons.Outlined.HourglassEmpty)
    T("見守りの許可", 26, W.bold)
    GuardDisclosureContent()
    T("アプリを制限する機能は、解くロックプランで使えます（7日間は無料）。", 13, color = Theme.inkSoft)
}

@Composable
private fun NotificationPermission() {
    PageIcon(Icons.Outlined.Notifications)
    T("通知の許可", 26, W.bold)
    T("ロックがかかったときに、問題が届いたことを通知で知らせます。通知をタップすると、ロック画面の上でも問題を開けます。", 16, color = Theme.inkSoft)
    T("通知がオフでも、問題の画面は出ます。", 13, color = Theme.inkSoft)
}
