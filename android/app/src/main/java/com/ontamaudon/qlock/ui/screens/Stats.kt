package com.ontamaudon.qlock.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.ui.Card
import com.ontamaudon.qlock.ui.Divider
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.components.IsoBarChart

@Composable
fun StatsScreen() {
    val m = AppModel
    val total = m.totals
    val accuracy = if (total.attempts == 0) 0 else Math.round(total.correct.toDouble() / total.attempts * 100).toInt()
    Screen("記録") {
        Card(padding = 0.dp) {
            Column {
                StatRow("制限の発動", "${total.triggers} 回"); Divider()
                StatRow("累計正解", "${total.correct} 問"); Divider()
                StatRow("正答率", "$accuracy %"); Divider()
                StatRow("連続正解日数", "${m.dayStreak} 日"); Divider()
                StatRow("いまの連続正解", "${m.currentStreak} 問"); Divider()
                StatRow("最高連続正解", "${m.bestStreak} 問")
            }
        }
        Card {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                T("過去の成績", 15, W.bold)
                IsoBarChart(m.weeklyCorrect(AppModel.PREMIUM_WEEKS), "正解数（手前が今週、奥が過去）")
            }
        }
        Card(padding = 0.dp) {
            Column {
                StatRow("問題で解除した回数", "${total.unlocks} 回"); Divider()
                StatRow("緊急解除した回数", "${total.emergencyUnlocks} 回")
            }
        }
    }
}

@Composable
private fun StatRow(title: String, value: String) {
    Row(Modifier.fillMaxWidth().padding(horizontal = 18.dp, vertical = 14.dp), verticalAlignment = Alignment.CenterVertically) {
        T(title, 15, color = Theme.inkSoft, modifier = Modifier.weight(1f))
        T(value, 16, W.semibold)
    }
}
