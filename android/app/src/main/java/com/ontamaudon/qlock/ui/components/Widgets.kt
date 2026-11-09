package com.ontamaudon.qlock.ui.components

import androidx.activity.compose.BackHandler
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.Orientation
import androidx.compose.foundation.gestures.draggable
import androidx.compose.foundation.gestures.rememberDraggableState
import androidx.compose.foundation.gestures.snapping.rememberSnapFlingBehavior
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.core.graphics.drawable.toBitmap
import com.ontamaudon.qlock.guard.AppCatalog
import com.ontamaudon.qlock.ui.IsoBackground
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import kotlin.math.roundToInt

/** 下から出てくる画面（iPhone 版の roomySheet：画面の9割の高さ。上の余白をタップするか、下へ引いて戻る）。 */
@Composable
fun Sheet(onDismiss: () -> Unit, content: @Composable ColumnScope.() -> Unit) {
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false, decorFitsSystemWindows = false)) {
        var shown by remember { mutableStateOf(false) }
        var drag by remember { mutableFloatStateOf(0f) }
        val density = LocalDensity.current
        LaunchedEffect(Unit) { shown = true }
        Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.25f))
            .clickable(remember { MutableInteractionSource() }, null) { onDismiss() }) {
            AnimatedVisibility(shown, Modifier.align(Alignment.BottomCenter),
                enter = slideInVertically(tween(260)) { it } + fadeIn(tween(160))) {
                Box(Modifier.fillMaxWidth().fillMaxHeight(0.9f)
                    .offset { IntOffset(0, drag.roundToInt().coerceAtLeast(0)) }
                    .clip(RoundedCornerShape(topStart = 12.dp, topEnd = 12.dp))
                    .clickable(remember { MutableInteractionSource() }, null) {}) {
                    IsoBackground {
                        Column(Modifier.fillMaxSize()) { content() }
                    }
                    // つまみ（下へ引くと閉じる）
                    Box(Modifier.fillMaxWidth().height(28.dp)
                        .draggable(rememberDraggableState { drag += it }, Orientation.Vertical,
                            onDragStopped = {
                                if (drag > with(density) { 120.dp.toPx() }) { onDismiss() } else { drag = 0f }
                            }),
                        contentAlignment = Alignment.TopCenter) {
                        Box(Modifier.padding(top = 6.dp).width(36.dp).height(5.dp).clip(CircleShape).background(Theme.inkFaint.copy(alpha = 0.5f)))
                    }
                }
            }
        }
    }
}

/** 画面いっぱいに出す画面（iPhone 版の fullScreenCover）。 */
@Composable
fun FullScreen(onDismiss: () -> Unit, content: @Composable () -> Unit) {
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false, decorFitsSystemWindows = false)) {
        BackHandler { onDismiss() }
        Box(Modifier.fillMaxSize()) { content() }
    }
}

/** オン・オフのスイッチ（iPhone の Toggle の見た目）。 */
@Composable
fun Toggle(on: Boolean, onChange: (Boolean) -> Unit, enabled: Boolean = true) {
    val x by animateDpAsState(if (on) 22.dp else 2.dp, tween(150), label = "toggle")
    val density = LocalDensity.current
    Box(Modifier.width(51.dp).height(31.dp).clip(CircleShape)
        .background(if (on) Theme.tealDeep else hexGray)
        .clickable(enabled = enabled) { onChange(!on) }) {
        Box(Modifier.offset { with(density) { IntOffset(x.roundToPx(), 2.dp.roundToPx()) } }.size(27.dp).clip(CircleShape).background(Color.White))
    }
}

private val hexGray = Color(0xFFE5E5EA)

/** アプリのアイコン。 */
@Composable
fun AppIcon(pkg: String, size: Dp) {
    val ctx = LocalContext.current
    val bmp = remember(pkg) { AppCatalog.icon(ctx, pkg)?.toBitmap(96, 96)?.asImageBitmap() }
    if (bmp != null) Image(bmp, null, Modifier.size(size))
    else Box(Modifier.size(size).clip(RoundedCornerShape(6.dp)).background(Theme.sunken))
}

/** くるくる回して選ぶ部品（iPhone の wheel の Picker の見た目）。 */
@Composable
fun WheelPicker(values: List<Int>, selected: Int, label: (Int) -> String, onSelect: (Int) -> Unit,
                modifier: Modifier = Modifier, enabled: Boolean = true) {
    val rowH = 32.dp
    val visible = 5
    val index = values.indexOf(selected).coerceAtLeast(0)
    val state = rememberLazyListState(initialFirstVisibleItemIndex = index)
    val fling = rememberSnapFlingBehavior(state)
    LaunchedEffect(selected) {
        val i = values.indexOf(selected)
        if (i >= 0 && !state.isScrollInProgress && state.firstVisibleItemIndex != i) state.animateScrollToItem(i)
    }
    LaunchedEffect(state) {
        snapshotFlow { state.isScrollInProgress }.collect { scrolling ->
            if (!scrolling) {
                val i = state.firstVisibleItemIndex + if (state.firstVisibleItemScrollOffset > 0 &&
                    state.firstVisibleItemScrollOffset > state.layoutInfo.visibleItemsInfo.firstOrNull()?.size?.div(2) ?: 0) 1 else 0
                val v = values.getOrNull(i.coerceIn(0, values.lastIndex))
                if (v != null && v != selected) onSelect(v)
            }
        }
    }
    Box(modifier.height(rowH * visible)) {
        Box(Modifier.align(Alignment.Center).fillMaxWidth().padding(horizontal = 4.dp).height(rowH)
            .clip(RoundedCornerShape(8.dp)).background(Theme.sunken))
        LazyColumn(state = state, flingBehavior = fling, userScrollEnabled = enabled,
            contentPadding = androidx.compose.foundation.layout.PaddingValues(vertical = rowH * (visible / 2)),
            modifier = Modifier.fillMaxSize()) {
            items(values.size) { i ->
                Box(Modifier.fillMaxWidth().height(rowH), contentAlignment = Alignment.Center) {
                    val v = values[i]
                    T(label(v), 20, if (v == selected) W.semibold else W.regular,
                        if (!enabled) Theme.inkFaint else if (v == selected) Theme.ink else Theme.inkSoft)
                }
            }
        }
    }
}

/** 確認の小窓（iPhone の alert / confirmationDialog の代わり。Android 標準の形）。 */
@Composable
fun Confirm(title: String, message: String? = null, buttons: List<Pair<String, () -> Unit>>, cancel: String = "キャンセル",
            destructiveFirst: Boolean = false, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = Theme.surface,
        title = { T(title, 18, W.bold) },
        text = if (message != null) { { T(message, 14, color = Theme.inkSoft) } } else null,
        confirmButton = {
            Column(horizontalAlignment = Alignment.End) {
                buttons.forEachIndexed { i, (label, run) ->
                    TextButton(onClick = { onDismiss(); run() }) {
                        T(label, 15, W.bold, if (destructiveFirst && i == 0) Theme.danger else Theme.tealDeep)
                    }
                }
            }
        },
        dismissButton = if (cancel.isEmpty()) null else {
            { TextButton(onClick = onDismiss) { T(cancel, 15, W.semibold, Theme.inkSoft) } }
        },
    )
}
