package com.ontamaudon.qlock

import com.ontamaudon.qlock.data.GuardRule
import com.ontamaudon.qlock.data.Problem
import com.ontamaudon.qlock.data.ProblemCategory
import com.ontamaudon.qlock.data.UnitInfo
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

/** iPhone 版と同じ問題データを、Android 版の読み方で全部読めるかを確かめる。 */
class ProblemDataTest {
    private val json = Json { ignoreUnknownKeys = true }
    private val dir = File("../../mathscreen/Resources")

    @Test
    fun allProblemsParse() {
        val problems = json.decodeFromString<List<Problem>>(File(dir, "problems.json").readText())
        val units = json.decodeFromString<List<UnitInfo>>(File(dir, "units.json").readText()).map { it.id }.toSet()
        assertTrue("問題が少なすぎる：${problems.size}", problems.size > 10_000)
        assertEquals("id が重複している", problems.size, problems.map { it.id }.toSet().size)
        for (p in problems) {
            assertTrue("分野が不明：${p.id} ${p.category}", ProblemCategory.entries.any { it.name == p.category })
            p.choices?.let { assertTrue("4択の正解の番号が範囲外：${p.id}", p.answer in 0 until it.size) }
            p.unit?.let { assertTrue("単元が units.json にない：${p.id} $it", it in units) }
        }
    }

    @Test
    fun durationText() {
        assertEquals("45分", GuardRule.durationText(45))
        assertEquals("1時間30分", GuardRule.durationText(90))
        assertEquals("2時間", GuardRule.durationText(120))
    }
}
