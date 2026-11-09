package com.ontamaudon.qlock.ui

import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.clickable
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ontamaudon.qlock.QlockApp
import kotlin.math.tan

fun hex(v: Long, alpha: Float = 1f): Color = Color(
    red = ((v shr 16) and 0xFF) / 255f, green = ((v shr 8) and 0xFF) / 255f, blue = (v and 0xFF) / 255f, alpha = alpha)

/** アイソメトリック：白とグレーのブロックに、ティール（主）とコーラル（警告・今日）の2色。iPhone 版の Theme と同じ値。 */
object Theme {
    val background = hex(0xEEF1F7)
    val surface = Color.White
    val surfaceSide = hex(0xCBD1E1)
    val sunken = hex(0xE3E7F2)
    val sunkenSide = hex(0xC7CCDA)
    val line = hex(0xDDE1EC)
    val ink = hex(0x23263A)
    val inkSoft = hex(0x6B7088)
    val inkFaint = hex(0x9AA0B5)

    val tealLight = hex(0x7FE0D3)
    val teal = hex(0x3CC5B5)
    val tealDeep = hex(0x26968A)
    val coralLight = hex(0xFFB29D)
    val coral = hex(0xFF7A59)
    val coralDeep = hex(0xD2553A)
    val danger = coralDeep

    val goldLight = hex(0xFFE08A)
    val gold = hex(0xF2B632)
    val goldDeep = hex(0xC48A12)
    val violetLight = hex(0xCDB6FF)
    val violet = hex(0x9B7BF0)
    val violetDeep = hex(0x6B4FC0)

    val radius = 8.dp

    /** 丸ゴシック（M PLUS Rounded 1c）。iPhone 版の SF Rounded の代わり。 */
    val rounded: FontFamily by lazy {
        val am = QlockApp.instance.assets
        FontFamily(
            Font(path = "fonts/mplus_rounded_regular.ttf", assetManager = am, weight = FontWeight.Normal),
            Font(path = "fonts/mplus_rounded_medium.ttf", assetManager = am, weight = FontWeight.Medium),
            Font(path = "fonts/mplus_rounded_medium.ttf", assetManager = am, weight = FontWeight.SemiBold),
            Font(path = "fonts/mplus_rounded_bold.ttf", assetManager = am, weight = FontWeight.Bold),
            Font(path = "fonts/mplus_rounded_extrabold.ttf", assetManager = am, weight = FontWeight.ExtraBold),
            Font(path = "fonts/mplus_rounded_extrabold.ttf", assetManager = am, weight = FontWeight.Black),
        )
    }

    fun font(size: Int, weight: FontWeight = FontWeight.Normal, color: Color = ink): TextStyle =
        TextStyle(fontFamily = rounded, fontWeight = weight, fontSize = size.sp, color = color, lineHeight = (size * 1.35).sp)
}

/** iPhone 版の Font.Weight の名前に合わせた別名。 */
object W {
    val regular = FontWeight.Normal
    val medium = FontWeight.Medium
    val semibold = FontWeight.SemiBold
    val bold = FontWeight.Bold
    val heavy = FontWeight.ExtraBold
}

@Composable
fun T(text: String, size: Int, weight: FontWeight = W.regular, color: Color = Theme.ink, modifier: Modifier = Modifier,
      maxLines: Int = Int.MAX_VALUE, lineHeight: TextUnit = TextUnit.Unspecified,
      align: androidx.compose.ui.text.style.TextAlign? = null) {
    Text(text, modifier = modifier, style = Theme.font(size, weight, color).let { if (lineHeight != TextUnit.Unspecified) it.copy(lineHeight = lineHeight) else it },
        maxLines = maxLines, textAlign = align, overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis)
}

/** 右下方向に厚みのある板を、背景として描く。 */
fun Modifier.slab(top: Color, side: Color, depth: Dp, radius: Dp = Theme.radius): Modifier = drawBehind {
    val d = depth.toPx()
    val r = CornerRadius(radius.toPx())
    val w = size.width - d
    val h = size.height - d
    if (w <= 0 || h <= 0) return@drawBehind
    var k = d
    while (k >= 1f) {
        drawRoundRect(side, topLeft = Offset(k, k), size = Size(w, h), cornerRadius = r)
        k -= 1f
    }
    drawRoundRect(top, topLeft = Offset.Zero, size = Size(w, h), cornerRadius = r)
}

/** 白いブロックのカード（iPhone 版の .card()）。 */
@Composable
fun Card(modifier: Modifier = Modifier, padding: Dp = 18.dp, top: Color = Theme.surface, side: Color = Theme.surfaceSide,
         depth: Dp = 6.dp, content: @Composable () -> Unit) {
    Box(modifier.fillMaxWidth().slab(top, side, depth).padding(end = depth, bottom = depth)) {
        Box(Modifier.fillMaxWidth().padding(padding)) { content() }
    }
}

/** 掘り込まれた面（入力欄など）。 */
fun Modifier.well(radius: Dp = Theme.radius): Modifier = drawBehind {
    val r = CornerRadius(radius.toPx())
    drawRoundRect(Theme.line, cornerRadius = r)
    drawRoundRect(Theme.surface, topLeft = Offset(3.dp.toPx(), 3.dp.toPx()),
        size = Size(size.width - 3.dp.toPx(), size.height - 3.dp.toPx()), cornerRadius = r)
}

/** アイソメトリックの方眼（30°/150° の細い線）。 */
@Composable
fun IsoGrid(modifier: Modifier = Modifier) {
    Canvas(modifier.fillMaxSize()) {
        drawRect(Theme.background)
        val step = 26.dp.toPx()
        val slope = tan(Math.PI / 6).toFloat()
        val c = Theme.ink.copy(alpha = 0.045f)
        val stroke = 1.dp.toPx()
        val run = size.height / slope
        var x = -run
        while (x < size.width + run) {
            drawLine(c, Offset(x, 0f), Offset(x + run, size.height), stroke)
            drawLine(c, Offset(x, 0f), Offset(x - run, size.height), stroke)
            x += step
        }
    }
}

/** 方眼を背景に敷く。 */
@Composable
fun IsoBackground(modifier: Modifier = Modifier, content: @Composable BoxScope.() -> Unit) {
    Box(modifier.fillMaxSize().background(Theme.background)) {
        IsoGrid()
        content()
    }
}

enum class Kind { primary, secondary, quiet, alert }

/** 押すと沈む立体ボタン（iPhone 版の IsoButtonStyle）。 */
@Composable
fun IsoButton(onClick: () -> Unit, modifier: Modifier = Modifier, kind: Kind = Kind.primary, large: Boolean = false,
              enabled: Boolean = true, fill: Boolean = true, content: @Composable BoxScope.() -> Unit) {
    val source = remember { MutableInteractionSource() }
    val pressed by source.collectIsPressedAsState()
    val depth = 4.dp
    val d by animateDpAsState(if (pressed) 1.dp else depth, tween(80), label = "press")
    val (top, side) = when (kind) {
        Kind.primary -> Theme.teal to Theme.tealDeep
        Kind.secondary -> Theme.surface to Theme.sunkenSide
        Kind.quiet -> Theme.sunken to Theme.sunkenSide
        Kind.alert -> Theme.coral to Theme.coralDeep
    }
    Box(modifier.let { if (fill) it.fillMaxWidth() else it }) {
        Box(
            Modifier.let { if (fill) it.fillMaxWidth() else it }
                .padding(start = depth - d, top = depth - d)
                .slab(top, side, d)
                .padding(end = d, bottom = d)
                .clickable(interactionSource = source, indication = null, enabled = enabled, onClick = onClick)
                .padding(vertical = if (large) 11.dp else 14.dp),
            contentAlignment = Alignment.Center,
            content = content,
        )
    }
}

fun kindInk(kind: Kind): Color = when (kind) {
    Kind.primary, Kind.alert -> Color.White
    Kind.secondary, Kind.quiet -> Theme.ink
}

/** 文字だけのボタン（いちばんよく使う形）。 */
@Composable
fun IsoTextButton(label: String, onClick: () -> Unit, modifier: Modifier = Modifier, kind: Kind = Kind.primary,
                  large: Boolean = false, enabled: Boolean = true) {
    IsoButton(onClick, modifier.alpha(if (enabled) 1f else 0.5f), kind, large, enabled) {
        T(label, if (large) 22 else 16, W.bold, kindInk(kind))
    }
}

/** 小さなラベル。選択中はティールのブロック。 */
@Composable
fun Tag(text: String, isOn: Boolean, modifier: Modifier = Modifier) {
    Box(
        modifier.slab(if (isOn) Theme.teal else Theme.sunken, if (isOn) Theme.tealDeep else Theme.sunkenSide,
            if (isOn) 3.dp else 2.dp, 6.dp)
            .padding(end = if (isOn) 3.dp else 2.dp, bottom = if (isOn) 3.dp else 2.dp)
            .padding(horizontal = 12.dp, vertical = 7.dp),
        contentAlignment = Alignment.Center,
    ) {
        T(text, 13, W.bold, if (isOn) Color.White else Theme.inkSoft)
    }
}

@Composable
fun SectionLabel(text: String) = T(text, 13, W.bold, Theme.inkSoft)

/** 区切り線（iPhone の Divider）。 */
@Composable
fun Divider(modifier: Modifier = Modifier) {
    Box(modifier.fillMaxWidth().height(1.dp).background(Theme.line))
}
