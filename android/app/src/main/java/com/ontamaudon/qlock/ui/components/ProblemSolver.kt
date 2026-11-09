package com.ontamaudon.qlock.ui.components

import android.graphics.Rect
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.HelpOutline
import androidx.compose.material.icons.filled.Autorenew
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.outlined.IosShare
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.layout.boundsInWindow
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.Community
import com.ontamaudon.qlock.data.MasteryStore
import com.ontamaudon.qlock.data.Problem
import com.ontamaudon.qlock.data.ProblemMark
import com.ontamaudon.qlock.data.ProblemMarkStore
import com.ontamaudon.qlock.ui.Card
import com.ontamaudon.qlock.ui.IsoButton
import com.ontamaudon.qlock.ui.IsoTextButton
import com.ontamaudon.qlock.ui.Kind
import com.ontamaudon.qlock.ui.SectionLabel
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.well
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlin.math.PI
import kotlin.math.roundToInt
import kotlin.math.sin

/** 1問を解く部品。ロック解除・練習の両方で使う（iPhone 版の ProblemSolverView）。 */
@Composable
fun ProblemSolver(
    problem: Problem,
    onCorrect: (attempts: Int) -> Unit,
    onSkip: (() -> Unit)? = null,
    continueLabel: String,
    onContinue: () -> Unit,
    allowShare: Boolean = true,
) {
    var input by remember(problem.id) { mutableStateOf("") }
    var attempts by remember(problem.id) { mutableIntStateOf(0) }
    var solved by remember(problem.id) { mutableStateOf(false) }
    var wrongCount by remember(problem.id) { mutableIntStateOf(0) }
    var showWrong by remember(problem.id) { mutableStateOf(false) }
    var eliminated by remember(problem.id) { mutableStateOf(setOf<Int>()) }
    var picked by remember(problem.id) { mutableStateOf<Int?>(null) }
    var cardRect by remember { mutableStateOf(Rect()) }
    var showHelp by remember { mutableStateOf(false) }
    var confirmSkip by remember { mutableStateOf(false) }
    var shareFailed by remember { mutableStateOf(false) }
    val haptic = LocalHapticFeedback.current
    val ctx = LocalContext.current
    val shake = remember { Animatable(0f) }
    val canShare = allowShare && ShareSetting.isAllowed

    LaunchedEffect(wrongCount) {
        if (wrongCount > 0) {
            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
            shake.snapTo(0f); shake.animateTo(1f, tween(400))
        }
    }

    fun first(correct: Boolean) {
        if (attempts == 1) {
            MasteryStore.record(problem, correct)
            AppModel.scope.launch(Dispatchers.IO) { Community.recordFirstAttempt(problem.id, correct) }
        }
    }

    fun submit() {
        val value = input.toIntOrNull() ?: return
        attempts++
        val correct = value == problem.answer
        AppModel.recordAnswer(correct)
        first(correct)
        if (correct) {
            solved = true
            ProblemMarkStore.record(problem.id, ProblemMark.solved(attempts - 1))
            onCorrect(attempts)
        } else {
            wrongCount++
            showWrong = true
            input = ""
        }
    }

    fun submitChoice(i: Int) {
        attempts++
        val correct = i == problem.answer
        AppModel.recordAnswer(correct)
        first(correct)
        if (correct) {
            solved = true
            ProblemMarkStore.record(problem.id, ProblemMark.solved(attempts - 1))
            onCorrect(attempts)
        } else {
            eliminated = eliminated + i
            picked = null
            wrongCount++
            showWrong = true
        }
    }

    fun share(kind: ShareKind) = ShareImage.share(ctx, cardRect, kind) { shareFailed = true }

    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        // 問題
        Box(Modifier.onGloballyPositioned { c ->
            val b = c.boundsInWindow()
            cardRect = Rect(b.left.roundToInt(), b.top.roundToInt(), b.right.roundToInt() - 6, b.bottom.roundToInt() - 6)
        }) {
            Card {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    T("${problem.categoryInfo.label} ・ ${problem.title}", 13, W.semibold, Theme.inkSoft)
                    MathText(problem.body, 19, spoken = problem.plain)
                    T(if (problem.isChoice) "正しいものを選んで「こたえる」を押す" else "答えを入力して「こたえる」を押す", 12, color = Theme.inkFaint)
                }
            }
        }
        if (solved) {
            AnimatedVisibility(true, enter = fadeIn(tween(200))) {
                Card {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Icon(Icons.Filled.CheckCircle, null, tint = Theme.tealDeep, modifier = Modifier.size(24.dp))
                            T("正解　答えは ${problem.answerText}", 20, W.bold, Theme.tealDeep)
                        }
                        SectionLabel("解説")
                        MathText(problem.explanation, 16)
                        if (canShare) {
                            IsoButton({ share(ShareKind.solved) }, kind = Kind.quiet) {
                                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                    Icon(Icons.Outlined.IosShare, null, tint = Theme.ink, modifier = Modifier.size(18.dp))
                                    T("この問題を共有する", 15, W.semibold)
                                }
                            }
                        }
                        IsoTextButton(continueLabel, onContinue, Modifier.padding(top = 6.dp))
                    }
                }
            }
        } else {
            val dx = (8 * sin(shake.value * PI * 4)).toFloat()
            val choices = problem.choices
            if (choices != null) {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    choices.forEachIndexed { i, c ->
                        val gone = i in eliminated
                        Box(Modifier.alpha(if (gone) 0.4f else 1f)) {
                            IsoButton({ if (!gone) picked = i }, kind = Kind.secondary, enabled = !gone,
                                modifier = Modifier.let { m ->
                                    if (picked == i) m.border(2.5.dp, Theme.tealDeep, RoundedCornerShape(12.dp)) else m
                                }) {
                                Row(Modifier.fillMaxWidth().padding(horizontal = 14.dp), verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                    if (picked == i) Icon(Icons.Filled.CheckCircle, null, tint = Theme.tealDeep, modifier = Modifier.size(22.dp))
                                    else T(Problem.CHOICE_MARKS[i], 18, W.bold, Theme.tealDeep)
                                    MathText(c, 17, modifier = Modifier.weight(1f))
                                }
                            }
                        }
                    }
                    if (showWrong) T("ちがうみたい。もう一度選んでください。", 14, W.semibold, Theme.danger, Modifier.offset { IntOffset(dx.roundToInt(), 0) })
                    IsoTextButton("こたえる", { picked?.let { submitChoice(it) } }, Modifier.padding(top = 4.dp), enabled = picked != null)
                }
            } else {
                Row(
                    Modifier.offset(x = dx.dp).fillMaxWidth().height(68.dp).well()
                        .border(1.5.dp, if (showWrong) Theme.danger else Color.Transparent, RoundedCornerShape(12.dp))
                        .padding(horizontal = 20.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    T(if (input.isEmpty()) "?" else input.replace("-", "−"), 32, W.bold, if (input.isEmpty()) Theme.inkFaint else Theme.ink)
                    Spacer(Modifier.weight(1f))
                    if (showWrong) T("不正解", 14, W.semibold, Theme.danger)
                }
                NumberPad(input, { input = it }, ::submit)
            }
            // 分からないとき
            if (canShare) {
                IsoButton({ showHelp = true }, kind = Kind.quiet) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        Icon(Icons.AutoMirrored.Outlined.HelpOutline, null, tint = Theme.ink, modifier = Modifier.size(18.dp))
                        T("分からない", 15, W.semibold)
                    }
                }
            } else if (onSkip != null) {
                IsoButton({ if (AppModel.isPremium) confirmSkip = true else AppModel.showPlan = true }, kind = Kind.quiet) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        Icon(Icons.Filled.Autorenew, null, tint = Theme.ink, modifier = Modifier.size(18.dp))
                        T("別の問題", 15, W.semibold)
                        if (!AppModel.isPremium) Icon(Icons.Filled.Lock, null, tint = Theme.ink, modifier = Modifier.size(12.dp))
                    }
                }
            }
        }
    }

    if (showHelp) {
        val buttons = buildList<Pair<String, () -> Unit>> {
            if (onSkip != null) add((if (AppModel.isPremium) "問題を変える" else "問題を変える（プランで使えます）") to {
                if (AppModel.isPremium) confirmSkip = true else AppModel.showPlan = true
            })
            add("共有してヒントをもらう" to { share(ShareKind.ask) })
        }
        Confirm("分からないとき", buttons = buttons, cancel = "やめる") { showHelp = false }
    }
    if (confirmSkip) {
        Confirm("別の問題にしますか？", buttons = listOf("はい" to {
            ProblemMarkStore.record(problem.id, ProblemMark.skipped)
            onSkip?.invoke()
            Unit
        }), cancel = "いいえ") { confirmSkip = false }
    }
    if (shareFailed) {
        Confirm("画像をつくれませんでした", buttons = emptyList(), cancel = "OK") { shareFailed = false }
    }
}
