package com.ontamaudon.qlock.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.Backspace
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.ui.IsoButton
import com.ontamaudon.qlock.ui.IsoTextButton
import com.ontamaudon.qlock.ui.Kind
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W

/** 整数入力用のテンキー。 */
@Composable
fun NumberPad(text: String, onText: (String) -> Unit, onSubmit: () -> Unit) {
    val haptic = LocalHapticFeedback.current
    val rows = listOf(listOf("7", "8", "9"), listOf("4", "5", "6"), listOf("1", "2", "3"), listOf("±", "0", "⌫"))
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        for (row in rows) {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                for (key in row) {
                    IsoButton(onClick = {
                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                        onText(tap(text, key))
                    }, modifier = Modifier.weight(1f), kind = if (key == "±" || key == "⌫") Kind.quiet else Kind.secondary, large = true) {
                        if (key == "⌫") Icon(Icons.AutoMirrored.Outlined.Backspace, "けす", tint = Theme.ink)
                        else T(key, 22, W.bold)
                    }
                }
            }
        }
        IsoTextButton("こたえる", onSubmit, Modifier.padding(top = 4.dp), enabled = text.toIntOrNull() != null)
    }
}

private fun tap(text: String, key: String): String = when (key) {
    "⌫" -> text.dropLast(1)
    "±" -> if (text.startsWith("-")) text.drop(1) else "-$text"
    else -> {
        val digits = text.filter { it.isDigit() }
        if (digits.length >= 9) text
        else (if (digits == "0") text.replace("0", "") else text) + key
    }
}
