package com.ontamaudon.qlock.ui.components

import android.annotation.SuppressLint
import android.graphics.Color as AColor
import android.os.Handler
import android.os.Looper
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.matchParentSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.ontamaudon.qlock.ui.Theme
import org.json.JSONObject

/** LaTeX 混じりの文（`$...$` が数式）を KaTeX で表示する（iPhone 版の MathText と同じ。KaTeX はアプリ内蔵）。 */
@Composable
fun MathText(source: String, fontSize: Int = 19, color: Color = Theme.ink, spoken: String? = null, modifier: Modifier = Modifier) {
    var height by remember { mutableIntStateOf(48) }
    val css = String.format("#%06X", color.toArgb() and 0xFFFFFF)
    Box(modifier.fillMaxWidth().height(height.dp).semantics { contentDescription = spoken ?: source.replace("$", "") }) {
        AndroidView(
            modifier = Modifier.fillMaxWidth().height(height.dp),
            factory = { ctx -> KatexView(ctx) { h -> if (h > 0 && h != height) height = h } },
            update = { it.show(source, fontSize, css) },
        )
        // 指の操作は、数式の上ではなく、外側（ボタンなど）で受ける
        Box(Modifier.matchParentSize().pointerInput(Unit) {})
    }
}

@SuppressLint("SetJavaScriptEnabled", "ViewConstructor")
private class KatexView(ctx: android.content.Context, val onHeight: (Int) -> Unit) : WebView(ctx) {
    private var loaded = false
    private var pending: Triple<String, Int, String>? = null
    private var applied: String? = null
    private val main = Handler(Looper.getMainLooper())

    init {
        setBackgroundColor(AColor.TRANSPARENT)
        settings.javaScriptEnabled = true
        settings.allowFileAccess = true
        @Suppress("DEPRECATION")
        settings.allowFileAccessFromFileURLs = true
        isVerticalScrollBarEnabled = false
        isHorizontalScrollBarEnabled = false
        overScrollMode = OVER_SCROLL_NEVER
        isFocusable = false
        addJavascriptInterface(object {
            @JavascriptInterface fun height(h: Int) { main.post { onHeight(h) } }
        }, "Qlock")
        webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                loaded = true
                apply()
            }
        }
        loadUrl("file:///android_asset/katex/android.html")
    }

    fun show(src: String, size: Int, color: String) {
        pending = Triple(src, size, color)
        apply()
    }

    private fun apply() {
        val (src, size, color) = pending ?: return
        if (!loaded) return
        val key = "$src|$size|$color"
        if (key == applied) return
        applied = key
        // 文字列は JSON にして JavaScript に渡す（バックスラッシュや引用符をそのまま安全に運ぶ）
        val literal = JSONObject.quote(src)
        evaluateJavascript("render($literal, $size, '$color')", null)
    }
}
