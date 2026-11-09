package com.ontamaudon.qlock.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.border
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextMeasurer
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.hex
import kotlin.math.cos
import kotlin.math.max
import kotlin.math.min

/**
 * アイソメトリックの棒グラフ（iPhone 版の IsoBarChart と同じ描き方）。
 * 手前の1列が今週（月〜日）、過去の週は奥（右上）へ1週ずつ並ぶ。1問ごとに色が変わり、10問で最も華やかになる。
 */
@Composable
fun IsoBarChart(weeks: List<List<Int?>>, caption: String) {
    val rows = max(weeks.size, 1)
    val height = if (rows == 1) 190.dp else (210 + 28 * (rows - 1)).dp
    val measurer = rememberTextMeasurer()
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Canvas(Modifier.fillMaxWidth().height(height).semantics {
            contentDescription = "$caption：今週は " + (weeks.firstOrNull() ?: emptyList()).joinToString("、") { it?.toString() ?: "-" }
        }) { draw(this, weeks, measurer) }
        Row(horizontalArrangement = Arrangement.spacedBy(3.dp)) {
            for (tier in 1..10) {
                val c = tierColors(tier)
                Box(Modifier.weight(1f).height(10.dp).clip(RoundedCornerShape(3.dp)).background(c.second)
                    .border(1.dp, c.third.copy(alpha = 0.5f), RoundedCornerShape(3.dp)))
            }
        }
        T(caption, 12, W.bold, Theme.inkSoft)
    }
}

private fun tierColors(tier: Int): Triple<Color, Color, Color> = when (min(tier, 10)) {
    1 -> Triple(hex(0xBDE3FF), hex(0x5BB8F5), hex(0x2F86C9))
    2 -> Triple(hex(0xC4F0B0), hex(0x6FD04F), hex(0x3FA32E))
    3 -> Triple(hex(0xFFE08A), hex(0xF2B632), hex(0xC48A12))
    4 -> Triple(hex(0xFFC999), hex(0xFF9A3C), hex(0xD1701A))
    5 -> Triple(hex(0xFFC2DA), hex(0xFF6FA8), hex(0xD14780))
    6 -> Triple(hex(0xCDB6FF), hex(0x9B7BF0), hex(0x6B4FC0))
    7 -> Triple(hex(0xA9B8FF), hex(0x4A5FE0), hex(0x2B3AA8))
    8 -> Triple(hex(0xFF9AA0), hex(0xE0323F), hex(0xA81F2B))
    9 -> Triple(hex(0xFFFFFF), hex(0xD5DAE6), hex(0x9AA3B8))
    else -> Triple(hex(0xFFD25E), hex(0x3A3E58), hex(0x23263A))
}

private fun draw(scope: DrawScope, weeks: List<List<Int?>>, tm: TextMeasurer) = with(scope) {
    val cos30 = cos(Math.PI / 6).toFloat()
    val dayLabels = listOf("月", "火", "水", "木", "金", "土", "日")
    val gap = 1.15f
    val rowGap = 1.9f
    val full = 10f
    val rows = max(weeks.size, 1)
    val n = rows.toFloat()
    val maxBar = if (rows == 1) 2.2f else 1.7f
    val span = 7 * gap + 0.4f
    val depth = (n - 1) * rowGap
    val dp1 = 1.dp.toPx()
    val w = size.width / dp1
    val h = size.height / dp1
    val labelMargin = 46f
    val s = min((w - labelMargin) / ((10.45f + depth) * cos30), (h - 16) / ((10.45f + depth) * 0.5f + maxBar + 0.2f))
    val slack = max(0f, (w - labelMargin - (10.45f + depth) * cos30 * s) / 2)
    val ox = 4 + 1.6f * cos30 * s + slack
    val oy = 6 + ((0.8f + depth) * 0.5f + maxBar + 0.2f) * s

    fun p(x: Float, y: Float, z: Float) = Offset((ox + (x - y) * cos30 * s) * dp1, (oy + (x + y) * 0.5f * s - z * s) * dp1)
    fun face(pts: List<Triple<Float, Float, Float>>, color: Color) {
        val path = Path()
        pts.forEachIndexed { i, t -> val o = p(t.first, t.second, t.third); if (i == 0) path.moveTo(o.x, o.y) else path.lineTo(o.x, o.y) }
        path.close()
        drawPath(path, color)
    }
    fun box(x: Float, y: Float, z: Float, bw: Float, d: Float, bh: Float, top: Color, left: Color, right: Color) {
        face(listOf(Triple(x, y + d, z), Triple(x + bw, y + d, z), Triple(x + bw, y + d, z + bh), Triple(x, y + d, z + bh)), left)
        face(listOf(Triple(x + bw, y, z), Triple(x + bw, y + d, z), Triple(x + bw, y + d, z + bh), Triple(x + bw, y, z + bh)), right)
        face(listOf(Triple(x, y, z + bh), Triple(x + bw, y, z + bh), Triple(x + bw, y + d, z + bh), Triple(x, y + d, z + bh)), top)
    }
    fun label(text: String, at: Offset, size: Int, color: Color, weight: androidx.compose.ui.text.font.FontWeight = W.bold) {
        val layout = tm.measure(text, Theme.font(size, weight, color))
        drawText(layout, topLeft = Offset(at.x - layout.size.width / 2f, at.y - layout.size.height / 2f))
    }

    val items = mutableListOf<Pair<Float, () -> Unit>>()
    for (k in 0 until rows) {
        val y = -k * rowGap
        items += (y - 0.5f) to { box(-0.2f, y - 0.6f, 0f, span, 1.6f, 0.2f, Theme.surface, Theme.line, Theme.sunkenSide) }
    }
    val todayIndex = weeks.firstOrNull()?.indexOfLast { it != null }?.takeIf { it >= 0 }
    weeks.forEachIndexed { k, row ->
        row.forEachIndexed { i, value ->
            if (value == null) return@forEachIndexed
            val y = -k * rowGap - 0.3f
            val isToday = k == 0 && i == todayIndex
            val tier = min(value, 10)
            val colors = when {
                tier >= 1 -> tierColors(tier)
                isToday -> Triple(Theme.coralLight, Theme.coral, Theme.coralDeep)
                k == 0 -> Triple(Theme.tealLight, Theme.teal, Theme.tealDeep)
                else -> Triple(hex(0xBFEFE8), hex(0x8ADBD0), hex(0x5EBFB2))
            }
            val bh = max(0.12f, min(value / full, 1f) * maxBar)
            items += (i * gap + 0.1f + y + 10) to {
                val bx = i * gap + 0.1f
                box(bx, y, 0.2f, 0.8f, 0.8f, bh, colors.first, colors.second, colors.third)
                if (tier >= 5) {
                    face(listOf(Triple(bx + 0.14f, y + 0.14f, 0.2f + bh), Triple(bx + 0.5f, y + 0.14f, 0.2f + bh),
                        Triple(bx + 0.5f, y + 0.3f, 0.2f + bh), Triple(bx + 0.14f, y + 0.3f, 0.2f + bh)), Color.White.copy(alpha = 0.55f))
                }
                if (tier >= 8) {
                    val t = p(bx + 0.4f, y + 0.4f, 0.2f + bh)
                    label("✦", Offset(t.x, t.y - 9 * dp1), 13, colors.second)
                }
                if (k == 0 && value > 0 && i != todayIndex) {
                    val t = p(bx + 0.4f, y + 0.4f, 0.2f + bh)
                    label("$value", Offset(t.x, t.y - (if (tier >= 8) 22 else 10) * dp1), 11, Theme.ink, W.heavy)
                }
            }
        }
    }
    for ((_, f) in items.sortedBy { it.first }) f()

    dayLabels.forEachIndexed { i, l -> label(l, p(i * gap + 0.5f, 1.3f, 0f), 10, Theme.inkSoft) }
    for (k in 0 until rows) {
        val at = p(span - 0.2f + 0.15f, -k * rowGap + 0.2f, 0f)
        label(if (k == 0) "今週" else "${k}週前", Offset(at.x + 22 * dp1, at.y), 10, Theme.inkSoft)
    }
    if (todayIndex != null) {
        val v = weeks[0][todayIndex] ?: 0
        val bh = max(0.12f, min(v / full, 1f) * maxBar)
        val top = p(todayIndex * gap + 0.5f, -0.3f + 0.4f, 0.2f + bh)
        label("今日 $v", Offset(top.x, top.y - (if (v >= 8) 26 else 12) * dp1), 11, Theme.ink, W.heavy)
    }
}
