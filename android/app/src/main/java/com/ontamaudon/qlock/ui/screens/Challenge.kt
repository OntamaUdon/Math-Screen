package com.ontamaudon.qlock.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.data.Adaptive
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.Problem
import com.ontamaudon.qlock.ui.Card
import com.ontamaudon.qlock.ui.IsoBackground
import com.ontamaudon.qlock.ui.IsoTextButton
import com.ontamaudon.qlock.ui.Kind
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.components.Confirm
import com.ontamaudon.qlock.ui.components.ProblemSolver

/**
 * ロック解除のための問題画面（iPhone 版の ChallengeView）。制限したアプリの上や、ロック画面の上に出る。
 * onLeave：解かずに閉じる。onUnlocked：正解して解除した。
 */
@Composable
fun ChallengeScreen(onLockScreen: Boolean, onLeave: () -> Unit, onUnlocked: () -> Unit) {
    val m = AppModel
    var problem by remember { mutableStateOf<Problem?>(null) }
    var solvedCount by remember { mutableIntStateOf(0) }
    var confirmEmergency by remember { mutableStateOf(false) }
    fun next() {
        val p = problem
        if (p == null && solvedCount == 0) m.pendingProblem?.let { problem = it; return }
        problem = Adaptive.pick(m.challengeCategories, m.challengeUnits, p?.id)
    }
    LaunchedEffect(Unit) { if (problem == null) next() }

    IsoBackground {
        Column(Modifier.fillMaxSize().statusBarsPadding().navigationBarsPadding().verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp).padding(bottom = 32.dp), verticalArrangement = Arrangement.spacedBy(20.dp)) {
            Row(Modifier.fillMaxWidth().padding(top = 20.dp), verticalAlignment = Alignment.Top) {
                Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    T("${m.requiredCorrect}問解いて再開", 24, W.bold)
                    if (m.isLocked) T("正解 $solvedCount / ${m.requiredCorrect}", 14, color = Theme.inkSoft)
                }
                Box(Modifier.size(36.dp).clip(CircleShape).background(Theme.sunken).clickable(onClick = onLeave), contentAlignment = Alignment.Center) {
                    Icon(Icons.Filled.Close, "閉じる", tint = Theme.inkSoft, modifier = Modifier.size(16.dp))
                }
            }
            val p = problem
            if (!m.isLocked) {
                Card {
                    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                        T("いまは制限されていません", 17, W.semibold)
                        IsoTextButton("閉じる", onLeave, kind = Kind.secondary)
                    }
                }
            } else if (p != null) {
                key(p.id) {
                    ProblemSolver(
                        p,
                        onCorrect = { solvedCount++ },
                        onSkip = { next() },
                        continueLabel = if (solvedCount >= m.requiredCorrect) "解除してアプリに戻る" else "次の問題へ",
                        onContinue = {
                            if (solvedCount >= m.requiredCorrect) { m.completeChallenge(); onUnlocked() } else next()
                        },
                        allowShare = !onLockScreen,
                    )
                }
                T("緊急解除", 13, W.semibold, Theme.inkFaint, Modifier.fillMaxWidth().clickable { confirmEmergency = true }.padding(top = 4.dp),
                    align = androidx.compose.ui.text.style.TextAlign.Center)
            }
        }
    }
    if (confirmEmergency) Confirm("緊急解除しますか？", "問題を解かずにすべての制限を外します。記録には「緊急解除」として残ります。",
        buttons = listOf("緊急解除する" to { m.emergencyUnlock(); onUnlocked() }), cancel = "緊急解除しない", destructiveFirst = true) { confirmEmergency = false }
}
