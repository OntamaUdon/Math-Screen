package com.ontamaudon.qlock.guard

import android.content.Context
import android.content.Intent
import android.content.pm.ApplicationInfo
import android.graphics.drawable.Drawable

/** 端末に入っているアプリ（ホーム画面に出るものだけ）。すべてのアプリの一覧の権限は使わない。 */
object AppCatalog {
    data class App(val pkg: String, val label: String, val category: Int)

    private val categoryCache = HashMap<String, Int>()

    fun launcherApps(ctx: Context): List<App> {
        val pm = ctx.packageManager
        val intent = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        return pm.queryIntentActivities(intent, 0)
            .map { it.activityInfo.applicationInfo }
            .distinctBy { it.packageName }
            .filter { it.packageName != ctx.packageName }
            .map { App(it.packageName, pm.getApplicationLabel(it).toString(), it.category) }
            .sortedBy { it.label }
    }

    fun label(ctx: Context, pkg: String): String =
        runCatching { ctx.packageManager.let { pm -> pm.getApplicationLabel(pm.getApplicationInfo(pkg, 0)).toString() } }.getOrDefault(pkg)

    fun icon(ctx: Context, pkg: String): Drawable? = runCatching { ctx.packageManager.getApplicationIcon(pkg) }.getOrNull()

    fun category(ctx: Context, pkg: String): Int = categoryCache.getOrPut(pkg) {
        runCatching { ctx.packageManager.getApplicationInfo(pkg, 0).category }.getOrDefault(ApplicationInfo.CATEGORY_UNDEFINED)
    }

    /** ルールで選べるアプリの種類。Android がアプリごとに持っている種類の情報を使う（アプリによっては、入っていない）。 */
    val selectableCategories: List<Pair<Int, String>> = listOf(
        ApplicationInfo.CATEGORY_SOCIAL to "SNS",
        ApplicationInfo.CATEGORY_GAME to "ゲーム",
        ApplicationInfo.CATEGORY_VIDEO to "動画",
        ApplicationInfo.CATEGORY_AUDIO to "音楽",
        ApplicationInfo.CATEGORY_NEWS to "ニュース",
        ApplicationInfo.CATEGORY_IMAGE to "写真",
    )

    fun categoryLabel(c: Int) = selectableCategories.firstOrNull { it.first == c }?.second ?: "その他"
}
