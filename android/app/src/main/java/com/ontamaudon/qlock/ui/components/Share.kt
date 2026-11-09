package com.ontamaudon.qlock.ui.components

import android.app.Activity
import android.content.Context
import android.content.ContextWrapper
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Rect
import android.graphics.Typeface
import android.os.Handler
import android.os.Looper
import android.view.PixelCopy
import androidx.core.content.FileProvider
import com.ontamaudon.qlock.data.Store
import com.ontamaudon.qlock.data.ParentLock
import com.ontamaudon.qlock.ui.Theme
import androidx.compose.ui.graphics.toArgb
import java.io.File

/** 問題の共有（X や LINE など）。保護者用設定がオンの家庭では、初期状態ではオフ（iPhone 版と同じ）。 */
object ShareSetting {
    val isAllowed: Boolean
        get() = if (Store.prefs.contains("share.allowed")) Store.prefs.getBoolean("share.allowed", true)
        else !(ParentLock.isEnabled && ParentLock.hasPasscode)

    fun set(on: Boolean) = Store.prefs.edit().putBoolean("share.allowed", on).apply()

    /** 共有する文に入れるアプリの URL。Google Play の URL が決まったら、ここに入れる。空なら入れない。 */
    const val APP_URL = ""
}

enum class ShareKind {
    ask, solved;

    val message: String
        get() {
            val head = if (this == ask) "この問題、どう考えればいいか、ヒントをください。" else "この問題、解けた！みんなは解けるかな？"
            var s = head + "\n（解くまでアプリが開かなくなる「解くロック」の問題です）\n#解くロック"
            if (ShareSetting.APP_URL.isNotEmpty()) s += "\n" + ShareSetting.APP_URL
            return s
        }
}

fun Context.findActivity(): Activity? {
    var c: Context? = this
    while (c is ContextWrapper) {
        if (c is Activity) return c
        c = c.baseContext
    }
    return null
}

/** 問題のカードを画面から切り取り、アプリの名前を付けた画像にして、共有の画面を出す。 */
object ShareImage {
    fun share(ctx: Context, card: Rect, kind: ShareKind, onFail: () -> Unit) {
        val activity = ctx.findActivity() ?: return onFail()
        if (card.width() < 10 || card.height() < 10) return onFail()
        val crop = Bitmap.createBitmap(card.width(), card.height(), Bitmap.Config.ARGB_8888)
        PixelCopy.request(activity.window, card, crop, { result ->
            if (result != PixelCopy.SUCCESS) { onFail(); return@request }
            val out = compose(ctx, crop, kind)
            val dir = File(ctx.cacheDir, "share").apply { mkdirs() }
            val file = File(dir, "qlock-problem.png")
            file.outputStream().use { out.compress(Bitmap.CompressFormat.PNG, 100, it) }
            val uri = FileProvider.getUriForFile(ctx, ctx.packageName + ".share", file)
            val send = Intent(Intent.ACTION_SEND).apply {
                type = "image/png"
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_TEXT, kind.message)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            ctx.startActivity(Intent.createChooser(send, null))
        }, Handler(Looper.getMainLooper()))
    }

    private fun compose(ctx: Context, crop: Bitmap, kind: ShareKind): Bitmap {
        val density = ctx.resources.displayMetrics.density
        val footer = (48 * density).toInt()
        val out = Bitmap.createBitmap(crop.width, crop.height + footer, Bitmap.Config.ARGB_8888)
        val c = Canvas(out)
        c.drawColor(android.graphics.Color.WHITE)
        c.drawBitmap(crop, 0f, 0f, null)
        val bold = runCatching { Typeface.createFromAsset(ctx.assets, "fonts/mplus_rounded_extrabold.ttf") }.getOrDefault(Typeface.DEFAULT_BOLD)
        val p = Paint(Paint.ANTI_ALIAS_FLAG).apply { typeface = bold; textSize = 16 * density }
        val baseline = crop.height + footer / 2f + p.textSize / 3
        p.color = Theme.ink.toArgb()
        p.textAlign = Paint.Align.RIGHT
        c.drawText("解くロック", crop.width - 16 * density, baseline, p)
        if (kind == ShareKind.solved) {
            p.color = Theme.tealDeep.toArgb()
            p.textAlign = Paint.Align.LEFT
            c.drawText("✓ 正解", 16 * density, baseline, p)
        }
        return out
    }
}
