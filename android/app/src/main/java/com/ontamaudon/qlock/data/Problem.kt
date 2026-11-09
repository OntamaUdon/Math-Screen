package com.ontamaudon.qlock.data

import com.ontamaudon.qlock.QlockApp
import kotlinx.serialization.Serializable
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json

/** 問題（problems.json の1件）。iPhone 版と同じデータ。 */
@Serializable
data class Problem(
    val id: String,
    val category: String,
    val difficulty: Int,
    val title: String,
    val body: String,          // LaTeX 混じり（$...$ が数式）
    val plain: String,         // 文字だけの問題文
    val answer: Int,           // 整数の問題は正解の数、4択は正解の番号（0〜3）
    val explanation: String,
    val choices: List<String>? = null,
    val unit: String? = null,
    val family: String? = null,
    val rate: Double? = null,  // 10人中、何人が1発で正解できそうか（0〜10）
) {
    val isChoice: Boolean get() = choices != null
    val answerText: String get() = if (isChoice) CHOICE_MARKS[answer.coerceIn(0, 3)] else "$answer"
    val categoryInfo: ProblemCategory get() = ProblemCategory.from(category)

    companion object {
        val CHOICE_MARKS = listOf("①", "②", "③", "④")
    }
}

/** 教科。 */
enum class Subject(val label: String) {
    math("数学"), english("英語"), social("社会"), science("理科"), japanese("国語"), general("ノンジャンル");

    val categories: List<ProblemCategory> get() = ProblemCategory.entries.filter { it.subject == this }
}

/** 問題の分野。problems.json の category と同じ文字。 */
enum class ProblemCategory(val subject: Subject, val label: String) {
    elem(Subject.math, "小学算数"),
    junior(Subject.math, "中学数学"),
    math1a(Subject.math, "数学I・A"),
    math2b(Subject.math, "数学II・B"),
    math3c(Subject.math, "数学III・C"),
    eng_word(Subject.english, "英単語"),
    eng_sentence(Subject.english, "英文法・和訳"),
    soc_geo(Subject.social, "地理"),
    soc_hist(Subject.social, "歴史"),
    soc_civ(Subject.social, "公民"),
    sci_bio(Subject.science, "生物"),
    sci_chem(Subject.science, "化学"),
    sci_phys(Subject.science, "物理"),
    sci_earth(Subject.science, "地学"),
    ja_kanji(Subject.japanese, "漢字"),
    ja_idiom(Subject.japanese, "語句"),
    ja_classic(Subject.japanese, "古文"),
    ja_grammar(Subject.japanese, "国語文法"),
    triv_gen(Subject.general, "どれにも当てはまらない"),
    triv_math(Subject.math, "ノンジャンル"),
    triv_eng(Subject.english, "ノンジャンル"),
    triv_soc(Subject.social, "ノンジャンル"),
    triv_sci(Subject.science, "ノンジャンル"),
    triv_ja(Subject.japanese, "ノンジャンル");

    companion object {
        fun from(raw: String): ProblemCategory = entries.firstOrNull { it.name == raw } ?: junior
    }
}

/** 単元（units.json）。 */
@Serializable
data class UnitInfo(
    val id: String,
    val subject: String,
    val stage: String,
    val name: String,
    val order: Int,
    val prereqs: List<String> = emptyList(),
    val group: String? = null,
) {
    val subjectInfo: Subject get() = Subject.entries.firstOrNull { it.name == subject } ?: Subject.math
}

private val json = Json { ignoreUnknownKeys = true }

/** アプリ内蔵の問題データベース。 */
object ProblemBank {
    val all: List<Problem> by lazy {
        runCatching {
            QlockApp.instance.assets.open("problems.json").bufferedReader().use { json.decodeFromString<List<Problem>>(it.readText()) }
        }.getOrDefault(emptyList())
    }
    private val byId: Map<String, Problem> by lazy { all.associateBy { it.id } }

    fun find(id: String): Problem? = byId[id]

    /** 最近出した問題をなるべく避けてランダムに1問選ぶ。 */
    fun pick(categories: Set<String>, excluding: String? = null): Problem? {
        var pool = all.filter { it.category in categories }
        if (pool.isEmpty()) pool = all
        val recent = Store.recentProblemIDs.toSet()
        val fresh = pool.filter { it.id !in recent && it.id != excluding }
        val chosen = (fresh.ifEmpty { pool.filter { it.id != excluding } }).randomOrNull() ?: pool.randomOrNull()
        chosen?.let { Store.appendRecent(it.id) }
        return chosen
    }
}

object UnitCatalog {
    val all: List<UnitInfo> by lazy {
        runCatching {
            QlockApp.instance.assets.open("units.json").bufferedReader().use { json.decodeFromString<List<UnitInfo>>(it.readText()) }
        }.getOrDefault(emptyList())
    }
    private val byId: Map<String, UnitInfo> by lazy { all.associateBy { it.id } }

    /** 単元ごとの問題数。 */
    val problemCount: Map<String, Int> by lazy { ProblemBank.all.groupingBy { it.unit ?: "" }.eachCount() }

    /** 単元ごとの、問題の分野。 */
    val categories: Map<String, Set<String>> by lazy {
        ProblemBank.all.groupBy { it.unit ?: "" }.mapValues { (_, v) -> v.map { it.category }.toSet() }
    }

    /** 問題が1つ以上ある単元だけ。 */
    val available: List<UnitInfo> by lazy { all.filter { (problemCount[it.id] ?: 0) > 0 } }

    fun info(id: String): UnitInfo? = byId[id]
    fun units(subject: Subject): List<UnitInfo> = available.filter { it.subject == subject.name }
}
