package com.ontamaudon.qlock.ui.components

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.wrapContentSize
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AddCircle
import androidx.compose.material.icons.filled.CenterFocusStrong
import androidx.compose.material.icons.filled.CheckBox
import androidx.compose.material.icons.filled.CheckBoxOutlineBlank
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.IndeterminateCheckBox
import androidx.compose.material.icons.filled.RemoveCircle
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.TransformOrigin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.data.Subject
import com.ontamaudon.qlock.data.UnitProgress
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.hex
import com.ontamaudon.qlock.ui.slab
import kotlinx.coroutines.launch

/** マインドマップの1つの枝。子が空なら葉。 */
data class MapNode(
    val id: String,
    val title: String,
    val subtitle: String? = null,
    val subject: Subject? = null,
    val children: List<MapNode> = emptyList(),
    val progress: UnitProgress? = null,
) {
    val tint: Pair<Color, Color>
        get() = when (subject) {
            Subject.math -> Theme.teal to Theme.tealDeep
            Subject.english -> Theme.violet to Theme.violetDeep
            Subject.social -> Theme.gold to Theme.goldDeep
            Subject.science -> Theme.coral to Theme.coralDeep
            Subject.japanese -> hex(0x5B8DEF) to hex(0x3A66C4)
            Subject.general -> hex(0xFF6FA8) to hex(0xD14780)
            null -> Theme.ink to hex(0x0F1020)
        }

    val allIDs: List<String> get() = listOf(id) + children.flatMap { it.allIDs }
}

enum class CheckState { off, partial, on }

private data class Placed(val node: MapNode, val depth: Int, val y: Float, val parent: String?, val open: Boolean)

/** 指で動かして、つまんで拡大・縮小できるマインドマップ（iPhone 版の MindMapView）。 */
@Composable
fun MindMap(
    root: MapNode,
    modifier: Modifier = Modifier,
    openPath: List<String> = emptyList(),
    initialScale: Float = 1f,
    checkState: ((MapNode) -> CheckState)? = null,
    onCheck: ((MapNode) -> Unit)? = null,
    onSelect: (MapNode) -> Unit,
) {
    val nodeW = if (checkState == null) 148f else 176f
    val colW = nodeW + 48
    val nodeH = 64f
    val rowH = 76f
    val margin = 20f
    var expanded by remember { mutableStateOf(openPath.toSet()) }
    val ox = remember { Animatable(0f) }
    val oy = remember { Animatable(0f) }
    var scale by remember { mutableFloatStateOf(initialScale) }
    var viewH by remember { mutableFloatStateOf(0f) }
    var viewW by remember { mutableFloatStateOf(0f) }
    var started by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val density = LocalDensity.current

    fun layout(open: Set<String>): Triple<List<Placed>, Float, Float> {
        val items = mutableListOf<Placed>()
        var maxDepth = 0
        fun place(node: MapNode, depth: Int, start: Float, parent: String?): Float {
            maxDepth = maxOf(maxDepth, depth)
            val kids = if (node.id in open) node.children else emptyList()
            var used = 0f
            for (k in kids) used += place(k, depth + 1, start + used, node.id)
            val slots = maxOf(used, 1f)
            items += Placed(node, depth, (start + slots / 2) * rowH, parent, node.id in open)
            return slots
        }
        val total = place(root, 0, 0f, null)
        return Triple(items, margin * 2 + maxDepth * colW + nodeW + 8, total * rowH + 8)
    }

    fun center(p: Placed) = Offset(margin + p.depth * colW + nodeW / 2, p.y)

    fun find(id: String, node: MapNode): MapNode? {
        if (node.id == id) return node
        for (c in node.children) find(id, c)?.let { return it }
        return null
    }

    fun recenter(animated: Boolean) {
        scale = initialScale
        val items = layout(expanded).first
        val t = items.firstOrNull { it.depth == 0 } ?: return
        val c = center(t)
        val ny = viewH / 2 - c.y * scale
        scope.launch {
            if (animated) { launch { ox.animateTo(0f, tween(300)) }; oy.animateTo(ny, tween(300)) }
            else { ox.snapTo(0f); oy.snapTo(ny) }
        }
    }

    fun tap(p: Placed) {
        if (p.node.children.isEmpty()) { onSelect(p.node); return }
        val next = expanded.toMutableSet()
        if (p.node.id in next) {
            next.removeAll(p.node.allIDs.toSet())
        } else {
            p.parent?.let { pid -> find(pid, root)?.children?.filter { it.id != p.node.id }?.forEach { next.removeAll(it.allIDs.toSet()) } }
            next += p.node.id
        }
        val before = layout(expanded).first.firstOrNull { it.node.id == p.node.id }
        val after = layout(next).first.firstOrNull { it.node.id == p.node.id }
        expanded = next
        if (before != null && after != null) {
            scope.launch { oy.snapTo(oy.value + (before.y - after.y) * scale) }
        }
    }

    BoxWithConstraints(modifier.fillMaxSize()) {
        val wPx = constraints.maxWidth.toFloat()
        val hPx = constraints.maxHeight.toFloat()
        val dpx = with(density) { 1.dp.toPx() }
        viewW = wPx / dpx
        viewH = hPx / dpx
        LaunchedEffect(Unit) { if (!started) { started = true; recenter(false) } }
        val (items, lw, lh) = layout(expanded)
        val byID = items.associateBy { it.node.id }
        Box(Modifier.fillMaxSize().clip(RoundedCornerShape(0.dp))
            .pointerInput(Unit) {
                detectTransformGestures { _, pan, zoom, _ ->
                    scale = (scale * zoom).coerceIn(0.5f, 1.6f)
                    scope.launch { ox.snapTo(ox.value + pan.x / dpx); oy.snapTo(oy.value + pan.y / dpx) }
                }
            }) {
            Box(Modifier
                .wrapContentSize(Alignment.TopStart, unbounded = true)
                .size(lw.dp, lh.dp)
                .graphicsLayer {
                    transformOrigin = TransformOrigin(0f, 0f)
                    scaleX = scale; scaleY = scale
                    translationX = ox.value * dpx
                    translationY = oy.value * dpx
                }) {
                Canvas(Modifier.fillMaxSize()) {
                    for (item in items) {
                        val parent = item.parent?.let { byID[it] } ?: continue
                        val a = center(parent); val b = center(item)
                        val from = Offset((a.x + nodeW / 2) * dpx, a.y * dpx)
                        val to = Offset((b.x - nodeW / 2) * dpx, b.y * dpx)
                        val mid = (from.x + to.x) / 2
                        val path = Path().apply { moveTo(from.x, from.y); cubicTo(mid, from.y, mid, to.y, to.x, to.y) }
                        drawPath(path, item.node.tint.second.copy(alpha = 0.45f), style = Stroke(2.5f * dpx, cap = StrokeCap.Round))
                    }
                }
                for (item in items) {
                    val c = center(item)
                    Box(Modifier.offset((c.x - nodeW / 2).dp, (c.y - nodeH / 2).dp).size(nodeW.dp, nodeH.dp)) {
                        Node(item, nodeH, checkState, onCheck) { tap(item) }
                    }
                }
            }
            // 元の位置に戻すボタン
            Box(Modifier.align(Alignment.BottomStart).padding(start = 14.dp, bottom = 14.dp).size(47.dp)
                .slab(Theme.surface, Theme.surfaceSide, 3.dp, 12.dp).padding(end = 3.dp, bottom = 3.dp)
                .clickable { recenter(true) }, contentAlignment = Alignment.Center) {
                Icon(Icons.Filled.CenterFocusStrong, "マップを元の位置に戻す", tint = Theme.tealDeep, modifier = Modifier.size(22.dp))
            }
            T("指で動かす・つまんで拡大", 11, color = Theme.inkFaint, modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 8.dp))
        }
    }
}

@Composable
private fun Node(item: Placed, nodeH: Float, checkState: ((MapNode) -> CheckState)?, onCheck: ((MapNode) -> Unit)?, onTap: () -> Unit) {
    val n = item.node
    val (top, side) = n.tint
    val isRoot = item.depth == 0
    val isLeaf = n.children.isEmpty()
    val filled = isRoot || item.depth == 1
    val ink = if (filled) Color.White else Theme.ink
    Box(Modifier.fillMaxSize()
        .slab(if (filled) top else Theme.surface, if (filled) side else Theme.surfaceSide, 4.dp, 12.dp)
        .padding(end = 4.dp, bottom = 4.dp)
        .let { if (!filled) it.border(2.dp, top.copy(alpha = 0.6f), RoundedCornerShape(12.dp)) else it }
        .clickable(remember { MutableInteractionSource() }, null, onClick = onTap)) {
        Row(Modifier.fillMaxSize().padding(start = if (checkState == null) 10.dp else 2.dp, end = 10.dp),
            verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            checkState?.invoke(n)?.let { cs ->
                Box(Modifier.width(34.dp).fillMaxHeight().clickable(remember { MutableInteractionSource() }, null) { onCheck?.invoke(n) },
                    contentAlignment = Alignment.Center) {
                    Icon(when (cs) { CheckState.on -> Icons.Filled.CheckBox; CheckState.partial -> Icons.Filled.IndeterminateCheckBox; CheckState.off -> Icons.Filled.CheckBoxOutlineBlank },
                        null, Modifier.size(26.dp),
                        tint = if (cs == CheckState.off) (if (filled) Color.White.copy(alpha = 0.85f) else Theme.inkFaint) else (if (filled) Color.White else top))
                }
            }
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(1.dp)) {
                T(n.title, if (isRoot) 16 else 14, W.bold, ink, maxLines = 2)
                n.subtitle?.let { T(it, 11, color = if (filled) Color.White.copy(alpha = 0.85f) else Theme.inkSoft, maxLines = 1) }
                n.progress?.let { MasteryMeter(it, Modifier.padding(top = 3.dp)) }
            }
            if (!isLeaf) {
                Icon(if (item.open) Icons.Filled.RemoveCircle else Icons.Filled.AddCircle, null, Modifier.size(18.dp),
                    tint = if (filled) Color.White.copy(alpha = 0.9f) else top)
            }
        }
    }
}

/** 単元の完成度を示す棒。未学習=グレー、練習中=コーラル、得意=ティール、完成=金。 */
@Composable
fun MasteryMeter(progress: UnitProgress, modifier: Modifier = Modifier) {
    val fraction = when (progress.level) {
        com.ontamaudon.qlock.data.MasteryLevel.none -> 0f
        com.ontamaudon.qlock.data.MasteryLevel.complete -> 1f
        else -> maxOf(0.08f, progress.score.toFloat())
    }
    val color = when (progress.level) {
        com.ontamaudon.qlock.data.MasteryLevel.none -> Theme.inkFaint
        com.ontamaudon.qlock.data.MasteryLevel.learning -> Theme.coral
        com.ontamaudon.qlock.data.MasteryLevel.good -> Theme.teal
        com.ontamaudon.qlock.data.MasteryLevel.complete -> Theme.gold
    }
    Box(modifier.fillMaxWidth().height(6.dp).clip(CircleShape).background(Theme.sunken)) {
        if (fraction > 0) Box(Modifier.fillMaxWidth(fraction).height(6.dp).clip(CircleShape).background(color))
    }
}
