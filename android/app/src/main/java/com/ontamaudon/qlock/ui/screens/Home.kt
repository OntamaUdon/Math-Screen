package com.ontamaudon.qlock.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.ScreenshotMode
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.GuardRule
import com.ontamaudon.qlock.data.ParentLock
import com.ontamaudon.qlock.data.Subject
import com.ontamaudon.qlock.guard.GuardEngine
import com.ontamaudon.qlock.ui.Card
import com.ontamaudon.qlock.ui.Divider
import com.ontamaudon.qlock.ui.IsoTextButton
import com.ontamaudon.qlock.ui.Kind
import com.ontamaudon.qlock.ui.SectionLabel
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.components.AppIcon
import com.ontamaudon.qlock.ui.components.IsoBarChart
import com.ontamaudon.qlock.ui.components.Sheet
import com.ontamaudon.qlock.ui.components.Toggle
import com.ontamaudon.qlock.ui.well
import kotlinx.coroutines.delay
import androidx.compose.ui.platform.LocalContext

@Composable
fun HomeScreen() {
    var editing by remember { mutableStateOf<GuardRule?>(null) }
    val ctx = LocalContext.current
    LaunchedEffect(Unit) { while (true) { delay(15_000); AppModel.refresh() } }
    val m = AppModel
    Screen("解くロック") {
        Box(Modifier.padding(vertical = 4.dp)) { IsoBarChart(m.weeklyCorrect(1), "今週の正解数") }
        if (m.isLocked) {
            Card(top = Theme.coral, side = Theme.coralDeep) {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Icon(Icons.Filled.Lock, null, tint = Color.White, modifier = Modifier.size(18.dp))
                        T("制限中", 17, W.heavy, Color.White)
                    }
                    T("制限中のアプリがあります。${m.requiredCorrect}問解くと再開できます。", 14, color = Color.White.copy(alpha = 0.9f))
                    IsoTextButton("問題を解く", { GuardEngine.launchChallenge(ctx, fromLockScreen = false) }, kind = Kind.secondary)
                }
            }
        }
        val t = m.today
        Card {
            Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                SectionLabel("今日")
                Row(verticalAlignment = Alignment.CenterVertically) {
                    StatCell(t.triggers, "発動", Modifier.weight(1f))
                    Box(Modifier.width(1.dp).height(36.dp).background(Theme.line))
                    StatCell(t.correct, "正解", Modifier.weight(1f))
                    Box(Modifier.width(1.dp).height(36.dp).background(Theme.line))
                    StatCell(m.currentStreak, "連続正解", Modifier.weight(1f))
                }
            }
        }
        // 見守るアプリ
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                T("見守るアプリ", 18, W.bold, modifier = Modifier.weight(1f))
                Row(Modifier.clickable {
                    if (!m.isPremium) { m.showPlan = true; return@clickable }
                    ParentLock.request { editing = GuardRule(thresholdMinutes = 10, questionCount = 1) }
                }.padding(6.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    Icon(Icons.Filled.Add, null, tint = Theme.tealDeep, modifier = Modifier.size(16.dp))
                    T("追加", 14, W.semibold, Theme.tealDeep)
                }
            }
            if (!m.guardEnabled && !ParentLock.isActive && !ScreenshotMode.active) {
                T("「見守り」（ユーザー補助）がオフです。「設定」タブからオンにしてください。", 14, color = Theme.danger,
                    modifier = Modifier.fillMaxWidth().well().padding(14.dp))
            }
            if (!m.isPremium) {
                Card {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        T(if (m.rules.isEmpty()) "アプリロックは、解くロックプランで使えます。" else "プランが終わっているので、ロックは止まっています。", 15, W.bold)
                        T(if (m.rules.isEmpty()) "初めての方は、7日間無料です。" else "もう一度始めると、ルールはそのまま、また動きます。", 13, color = Theme.inkSoft)
                        IsoTextButton("プランを見る", { m.showPlan = true })
                    }
                }
            }
            if (m.rules.isEmpty()) {
                T("「追加」から、使いすぎたくないアプリと時間を決めましょう。", 15, color = Theme.inkSoft,
                    modifier = Modifier.fillMaxWidth().well().padding(20.dp))
            } else {
                Card(padding = 0.dp) {
                    Column {
                        m.rules.forEachIndexed { i, rule ->
                            if (i > 0) Divider(Modifier.padding(start = 16.dp))
                            RuleRow(rule, rule.id in m.lockedRuleIDs, m.usedMinutes(rule),
                                onToggle = { on ->
                                    if (!m.isPremium) m.showPlan = true
                                    else ParentLock.request { m.setEnabled(rule, on) }
                                },
                                onTap = {
                                    if (!m.isPremium) m.showPlan = true
                                    else ParentLock.request { editing = rule }
                                })
                        }
                    }
                }
            }
        }
    }
    editing?.let { rule ->
        Sheet({ editing = null }) {
            RuleEditor(rule, isNew = AppModel.rules.none { it.id == rule.id }, onClose = { editing = null })
        }
    }
}

@Composable
fun StatCell(value: Int, label: String, modifier: Modifier = Modifier) {
    Column(modifier, horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(2.dp)) {
        T("$value", 26, W.bold)
        T(label, 12, color = Theme.inkSoft)
    }
}

/** 例：「数学・英語」 */
fun subjectNames(rule: GuardRule): String {
    val names = Subject.entries.filter { s -> s.categories.any { it.name in rule.categories } }.map { it.label }
    val main = Subject.entries.filter { it != Subject.general }
    return if (main.all { it.label in names }) "すべての教科" else names.joinToString("・")
}

@Composable
private fun RuleRow(rule: GuardRule, locked: Boolean, used: Int, onToggle: (Boolean) -> Unit, onTap: () -> Unit) {
    Row(Modifier.fillMaxWidth().clickable(onClick = onTap).padding(horizontal = 16.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                T(rule.title, 16, W.semibold)
                if (locked) Icon(Icons.Filled.Lock, null, tint = Theme.tealDeep, modifier = Modifier.size(13.dp))
            }
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                for (p in rule.packages.take(4)) AppIcon(p, 18.dp)
                T("${rule.itemCount}件 ・ ${subjectNames(rule)}", 13, color = Theme.inkSoft)
            }
            if (rule.isEnabled) {
                val total = maxOf(rule.thresholdMinutes, 1)
                val fraction = if (locked) 1f else minOf(used.toFloat() / total, 1f)
                Column(Modifier.padding(top = 2.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Box(Modifier.fillMaxWidth().height(8.dp).clip(CircleShape).background(Theme.sunken)) {
                        Box(Modifier.fillMaxWidth(maxOf(fraction, 0.03f)).height(8.dp).clip(CircleShape)
                            .background(if (locked) Theme.coral else Theme.teal))
                    }
                    T(if (locked) "ロック中" else "あと約${maxOf(total - used, 0)}分", 12, color = if (locked) Theme.coralDeep else Theme.inkSoft)
                }
            }
        }
        Spacer(Modifier.width(8.dp))
        Toggle(rule.isEnabled, onToggle)
    }
}
