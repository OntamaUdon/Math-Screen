package com.ontamaudon.qlock.data

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import java.security.MessageDigest
import java.security.SecureRandom

/**
 * 保護者用設定（iPhone 版と同じ）。ルールの変更・設定画面・プランの管理を、4桁のパスコードで守る。
 * パスコードはこの端末の中だけに、ソルト付きのハッシュで保存する。
 */
object ParentLock {
    private val d get() = Store.prefs
    private const val OPEN_SECONDS = 180L
    private const val RESET_SECONDS = 6 * 3600L

    var hasPasscode by mutableStateOf(Store.prefs.getString("parent.hash", null) != null)
        private set
    var isEnabled by mutableStateOf(
        if (Store.prefs.contains("parent.enabled")) Store.prefs.getBoolean("parent.enabled", false)
        else Store.prefs.getString("parent.hash", null) != null
    )
        private set
    private var openUntil = 0L
    var showEntry by mutableStateOf(false)
    private var pending: (() -> Unit)? = null

    fun switchEnabled(on: Boolean) {
        if (on && !hasPasscode) return
        isEnabled = on
        d.edit().putBoolean("parent.enabled", on).apply()
    }

    val isActive: Boolean get() = isEnabled && hasPasscode && AppModel.isPremium
    val needsLock: Boolean get() = isActive && System.currentTimeMillis() >= openUntil

    fun request(action: () -> Unit) {
        if (needsLock) { pending = action; showEntry = true } else action()
    }

    fun cancelEntry() { pending = null; showEntry = false }
    fun lock() { openUntil = 0 }

    private fun nowS() = System.currentTimeMillis() / 1000

    val failures: Int
        get() {
            val last = d.getLong("parent.lastAttempt", 0)
            if (last > 0 && nowS() - last >= RESET_SECONDS) return 0
            return d.getInt("parent.failures", 0)
        }

    /** 待ち時間が終わる時刻（ミリ秒）。待ち時間でなければ null。 */
    val lockedUntil: Long?
        get() {
            val t = d.getLong("parent.lockedUntil", 0)
            return if (t > System.currentTimeMillis()) t else null
        }

    private fun wait(n: Int): Long? = when {
        n < 4 -> null
        n == 4 -> 60
        n == 5 -> 180
        else -> 3600
    }

    val warning: String?
        get() = when (failures) {
            in 0..2 -> null
            3 -> "次に間違えると1分間パスコードを打てなくなります。"
            4 -> "次に間違えると3分間パスコードを打てなくなります。"
            else -> "次に間違えると1時間パスコードを打てなくなります。"
        }

    val puzzle: String?
        get() = if (failures == 5) "のこりのコードは9995通り。\nこれから1時間に1回ずつ、重複なくコードを入力するとき、\n正しいパスコード1通りを見つけるまでにかかる時間[hour]の期待値を求めてみましょう。" else null

    enum class Result { ok, wrong, waiting, puzzleAnswer }

    fun verify(code: String): Result {
        if (lockedUntil != null) return Result.waiting
        if (hash(code) == d.getString("parent.hash", null)) {
            d.edit().putInt("parent.failures", 0).remove("parent.lockedUntil").remove("parent.lastAttempt").apply()
            openUntil = System.currentTimeMillis() + OPEN_SECONDS * 1000
            showEntry = false
            val run = pending
            pending = null
            run?.invoke()
            return Result.ok
        }
        if (failures == 5 && code == "4998") return Result.puzzleAnswer
        val n = failures + 1
        val e = d.edit().putInt("parent.failures", n).putLong("parent.lastAttempt", nowS())
        wait(n)?.let { e.putLong("parent.lockedUntil", System.currentTimeMillis() + it * 1000) }
        e.apply()
        return Result.wrong
    }

    fun setPasscode(code: String) {
        val bytes = ByteArray(16).also { SecureRandom().nextBytes(it) }
        val salt = bytes.joinToString("") { (it.toInt() and 0xff).toString(16) }
        d.edit().putString("parent.salt", salt).apply()
        d.edit().putString("parent.hash", hash(code)).putInt("parent.failures", 0).remove("parent.lockedUntil")
            .putBoolean("parent.enabled", true).apply()
        hasPasscode = true
        isEnabled = true
        openUntil = System.currentTimeMillis() + OPEN_SECONDS * 1000
    }

    fun clearPasscode() {
        d.edit().remove("parent.hash").remove("parent.salt").putInt("parent.failures", 0).remove("parent.lockedUntil")
            .putBoolean("parent.enabled", false).apply()
        hasPasscode = false
        isEnabled = false
    }

    private fun hash(code: String): String {
        val salt = d.getString("parent.salt", "") ?: ""
        return MessageDigest.getInstance("SHA-256").digest((salt + code).toByteArray()).joinToString("") { "%02x".format(it) }
    }
}
