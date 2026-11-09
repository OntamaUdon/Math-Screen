package com.ontamaudon.qlock.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.Backspace
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.data.ParentLock
import com.ontamaudon.qlock.ui.IsoButton
import com.ontamaudon.qlock.ui.IsoTextButton
import com.ontamaudon.qlock.ui.Kind
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import kotlinx.coroutines.delay

/** 4桁のテンキー。 */
@Composable
fun PasscodeKeypad(code: String, onCode: (String) -> Unit, disabled: Boolean = false) {
    val rows = listOf(listOf("1", "2", "3"), listOf("4", "5", "6"), listOf("7", "8", "9"), listOf("", "0", "⌫"))
    Column(Modifier.alpha(if (disabled) 0.5f else 1f), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Row(Modifier.fillMaxWidth().padding(bottom = 12.dp), horizontalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterHorizontally)) {
            for (i in 0 until 4) Box(Modifier.size(16.dp).clip(CircleShape).background(if (i < code.length) Theme.tealDeep else Theme.sunken))
        }
        for (row in rows) {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                for (key in row) {
                    if (key.isEmpty()) Box(Modifier.weight(1f))
                    else IsoButton({
                        if (key == "⌫") onCode(code.dropLast(1)) else if (code.length < 4) onCode(code + key)
                    }, Modifier.weight(1f), kind = if (key == "⌫") Kind.quiet else Kind.secondary, large = true, enabled = !disabled) {
                        if (key == "⌫") Icon(Icons.AutoMirrored.Outlined.Backspace, "けす", tint = Theme.ink) else T(key, 22, W.bold)
                    }
                }
            }
        }
    }
}

/** 保護者のパスコードを入れる画面。 */
@Composable
fun PasscodeEntry() {
    var code by remember { mutableStateOf("") }
    var message by remember { mutableStateOf<String?>(null) }
    var now by remember { mutableLongStateOf(System.currentTimeMillis()) }
    LaunchedEffect(Unit) { while (true) { delay(1000); now = System.currentTimeMillis() } }
    val until = ParentLock.lockedUntil.takeIf { now >= 0 }
    LaunchedEffect(code) {
        if (code.length != 4) return@LaunchedEffect
        when (ParentLock.verify(code)) {
            ParentLock.Result.ok -> {}
            ParentLock.Result.wrong -> { code = ""; message = if (ParentLock.lockedUntil == null) "パスコードが違います。" else null }
            ParentLock.Result.waiting -> code = ""
            ParentLock.Result.puzzleAnswer -> {
                code = ""
                message = "この問題が解けるなら、あなたは十分に勉強している証拠。現実的な別のやり方を考えよう。"
            }
        }
    }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(18.dp)) {
        T("保護者のパスコード", 22, W.bold)
        T(until?.let { "しばらく入力できません。あと${remaining(it - now)}" } ?: (message ?: "4桁のパスコードを入れてください。"), 14,
            color = if (until != null || message != null) Theme.danger else Theme.inkSoft, align = TextAlign.Center)
        ParentLock.warning?.let { T(it, 16, W.bold, Theme.danger, align = TextAlign.Center) }
        ParentLock.puzzle?.let { T(it, 20, W.semibold, align = TextAlign.Center) }
        Box(Modifier.padding(horizontal = 24.dp)) { PasscodeKeypad(code, { code = it }, disabled = until != null) }
        IsoTextButton("やめる", { ParentLock.cancelEntry() }, kind = Kind.quiet)
    }
}

private fun remaining(ms: Long): String {
    val s = maxOf(((ms + 999) / 1000).toInt(), 0)
    return if (s >= 60) "${(s + 59) / 60}分" else "${s}秒"
}

/** パスコードを新しく決める画面（2回入れて確認）。 */
@Composable
fun PasscodeSetup(onDone: () -> Unit) {
    var first by remember { mutableStateOf<String?>(null) }
    var code by remember { mutableStateOf("") }
    var message by remember { mutableStateOf<String?>(null) }
    var showIntro by remember { mutableStateOf(true) }
    LaunchedEffect(code) {
        if (code.length != 4) return@LaunchedEffect
        val f = first
        if (f != null) {
            if (f == code) { ParentLock.setPasscode(code); onDone() }
            else { first = null; message = "一致しませんでした。もう一度はじめから入れてください。" }
        } else {
            first = code; message = null
        }
        code = ""
    }
    Column(Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(18.dp, Alignment.CenterVertically)) {
        T(if (first == null) "新しいパスコード" else "もう一度入れてください", 22, W.bold)
        T(message ?: "使う人が知らない4桁の数字にしてください。忘れると、アプリを入れ直すしかなく、ルールも消えます。", 14,
            color = if (message == null) Theme.inkSoft else Theme.danger, align = TextAlign.Center)
        Box(Modifier.padding(horizontal = 24.dp)) { PasscodeKeypad(code, { code = it }) }
        IsoTextButton("やめる", onDone, kind = Kind.quiet)
    }
    if (showIntro) {
        Confirm("新しいパスコードを設定してください", "これから使うパスコードを、新しく決めます。前に決めたパスコードを入れる画面ではありません。",
            buttons = listOf("OK" to {}), cancel = "") { showIntro = false }
    }
}
