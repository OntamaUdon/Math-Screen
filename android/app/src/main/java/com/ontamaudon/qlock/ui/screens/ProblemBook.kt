package com.ontamaudon.qlock.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Cancel
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.ScreenshotMode
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.Community
import com.ontamaudon.qlock.data.MasteryLevel
import com.ontamaudon.qlock.data.MasteryStore
import com.ontamaudon.qlock.data.Problem
import com.ontamaudon.qlock.data.ProblemBank
import com.ontamaudon.qlock.data.ProblemMark
import com.ontamaudon.qlock.data.ProblemMarkStore
import com.ontamaudon.qlock.data.Subject
import com.ontamaudon.qlock.data.UnitCatalog
import com.ontamaudon.qlock.data.UnitInfo
import com.ontamaudon.qlock.ui.Card
import com.ontamaudon.qlock.ui.IsoBackground
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.components.MapNode
import com.ontamaudon.qlock.ui.components.MindMap
import com.ontamaudon.qlock.ui.components.ProblemSolver
import com.ontamaudon.qlock.ui.components.Sheet
import com.ontamaudon.qlock.ui.well
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext

/** マインドマップの木をつくる（iPhone 版の BookMap）。 */
object BookMap {
    private val stages = listOf("小学", "中学", "高校", "ノンジャンル")

    private fun subjectNodes(unitNode: (UnitInfo, Subject) -> MapNode): List<MapNode> = Subject.entries.mapNotNull { s ->
        val units = UnitCatalog.units(s)
        if (units.isEmpty()) return@mapNotNull null
        val stageNodes = stages.mapNotNull { st ->
            val list = units.filter { it.stage == st }
            if (list.isEmpty()) return@mapNotNull null
            val unitNodes = list.map { unitNode(it, s) }
            var kids = unitNodes
            if (list.size > 10) {
                val order = list.map { it.group ?: "その他" }.distinct()
                kids = order.map { g ->
                    val members = list.indices.filter { (list[it].group ?: "その他") == g }
                    MapNode("gr:${s.name}:$st:$g", g, "${members.size}単元", s, members.map { unitNodes[it] })
                }
            }
            MapNode("st:${s.name}:$st", st, "${list.size}単元", s, kids)
        }
        val children = if (s == Subject.general) (stageNodes.firstOrNull()?.children ?: emptyList()) else stageNodes
        MapNode("sub:${s.name}", s.label, "${units.size}単元", s, children)
    }

    /** 問題集：教科 → 小学・中学・高校・ノンジャンル → 単元。 */
    fun browse(): MapNode = MapNode("root", "問題集", children = subjectNodes { u, s ->
        val n = UnitCatalog.problemCount[u.id] ?: 0
        val pr = MasteryStore.progress(u.id)
        MapNode("u:${u.id}", u.name, if (pr.level == MasteryLevel.none) "${n}問" else "${n}問 ・ ${pr.level.label}", s, progress = pr)
    })

    /** ルールの出題範囲を選ぶ。 */
    fun selector(): MapNode = MapNode("root", "出題する範囲", children = subjectNodes { u, s ->
        MapNode("u:${u.id}", u.name, "${UnitCatalog.problemCount[u.id] ?: 0}問", s)
    })
}

object ProblemBook {
    fun matches(p: Problem, tokens: List<String>): Boolean {
        if (tokens.isEmpty()) return true
        val unitName = p.unit?.let { UnitCatalog.info(it)?.name } ?: ""
        val hay = (p.plain + " " + p.title + " " + unitName + " " + p.categoryInfo.label).lowercase()
        return tokens.all { it in hay }
    }
}

/** 問題集：マインドマップをたどって、問題を探す。キーワードで探すこともできる。 */
@Composable
fun ProblemBookScreen() {
    var query by remember { mutableStateOf("") }
    var results by remember { mutableStateOf<List<Problem>>(emptyList()) }
    var unit by remember { mutableStateOf<String?>(null) }
    var selected by remember { mutableStateOf<Problem?>(null) }
    val trimmed = query.trim()
    LaunchedEffect(query) {
        delay(300)
        val tokens = trimmed.lowercase().split(" ", "　").filter { it.isNotEmpty() }
        results = if (tokens.isEmpty()) emptyList() else withContext(Dispatchers.Default) {
            ProblemBank.all.asSequence().filter { ProblemBook.matches(it, tokens) }.take(300).toList()
        }
    }
    val tick = AppModel.tick
    IsoBackground {
        Column(Modifier.fillMaxSize().statusBarsPadding(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Column(Modifier.padding(horizontal = 20.dp).padding(top = 12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                T("問題集", 28, W.bold)
                T(if (trimmed.isEmpty()) "枝をタップして広げ、単元を選んで挑戦。" else "検索結果", 14, color = Theme.inkSoft)
            }
            Row(Modifier.padding(horizontal = 20.dp).fillMaxWidth().well().padding(12.dp), verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Icon(Icons.Filled.Search, null, tint = Theme.inkFaint, modifier = Modifier.size(20.dp))
                Box(Modifier.weight(1f)) {
                    if (query.isEmpty()) T("問題・単語・単元を検索", 16, color = Theme.inkFaint)
                    BasicTextField(query, { query = it }, singleLine = true, textStyle = Theme.font(16), modifier = Modifier.fillMaxWidth())
                }
                if (query.isNotEmpty()) Icon(Icons.Filled.Cancel, "検索をクリア", tint = Theme.inkFaint, modifier = Modifier.size(20.dp).clickable { query = "" })
            }
            if (trimmed.isEmpty()) {
                val root = remember(tick) { BookMap.browse() }
                val shot = ScreenshotMode.scene == "book"
                MindMap(root, Modifier.weight(1f),
                    openPath = if (shot) listOf("root", "sub:math", "st:math:中学", "gr:math:中学:数と式") else listOf("root"),
                    initialScale = if (shot) 0.6f else 1f) { node -> if (node.id.startsWith("u:")) unit = node.id.drop(2) }
            } else {
                LazyColumn(Modifier.weight(1f), contentPadding = PaddingValues(start = 20.dp, end = 20.dp, bottom = 96.dp),
                    verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    item {
                        if (results.isEmpty()) T("見つかりませんでした。ほかのキーワードで探してみてください。", 15, color = Theme.inkSoft,
                            modifier = Modifier.fillMaxWidth().well().padding(20.dp))
                        else T("該当 ${results.size} 問", 12, W.semibold, Theme.inkSoft)
                    }
                    items(results, key = { it.id }) { p ->
                        Box(Modifier.clickable { selected = p }) { ProblemCard(p, ProblemMarkStore.mark(p.id)) }
                    }
                }
            }
        }
    }
    unit?.let { u -> Sheet({ unit = null }) { ProblemList(u, onClose = { unit = null }) } }
    selected?.let { p -> Sheet({ selected = null; AppModel.refresh() }) { ProblemDetail(p) { selected = null; AppModel.refresh() } } }
}

@Composable
fun ProblemCard(p: Problem, mark: ProblemMark?) {
    Card(padding = 14.dp) {
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                if (mark != null) T(mark.symbol, 18, W.heavy, when (mark) {
                    ProblemMark.perfect -> Theme.gold
                    ProblemMark.once -> Theme.tealDeep
                    ProblemMark.many -> Theme.teal
                    ProblemMark.skipped -> Theme.coral
                })
                T(p.title, 16, W.bold)
            }
            T(p.categoryInfo.label, 12, W.semibold, Theme.inkSoft)
            T(p.plain, 14, color = Theme.inkSoft, maxLines = 2)
        }
    }
}

/** マップで選んだ単元の問題一覧。 */
@Composable
private fun ProblemList(unitID: String, onClose: () -> Unit) {
    val info = UnitCatalog.info(unitID)
    var selected by remember { mutableStateOf<Problem?>(null) }
    val tick = AppModel.tick
    val items = remember(unitID) {
        ProblemBank.all.filter { it.unit == unitID }.withIndex()
            .sortedWith(compareByDescending<IndexedValue<Problem>> { it.value.rate ?: 5.0 }.thenBy { it.index }).map { it.value }
    }
    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(start = 20.dp, end = 20.dp, bottom = 40.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)) {
        item {
            Row(Modifier.fillMaxWidth().padding(top = 24.dp), verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    T(info?.name ?: "単元", 22, W.bold)
                    info?.let { T("${it.subjectInfo.label} ・ ${it.stage}", 13, color = Theme.inkSoft) }
                }
                Box(Modifier.clickable(onClick = onClose).padding(8.dp)) { T("閉じる", 15, W.semibold, Theme.inkSoft) }
            }
        }
        item { T("☆ 1発正解　◎ 1回まちがえて正解　〇 2回以上まちがえて正解　△ 解かずに変更", 11, color = Theme.inkSoft) }
        item {
            if (items.isEmpty()) T("この単元には、まだ問題がありません。", 15, color = Theme.inkSoft, modifier = Modifier.fillMaxWidth().well().padding(20.dp))
            else T("${items.size} 問", 12, W.semibold, Theme.inkSoft)
        }
        items(items, key = { it.id }) { p ->
            Box(Modifier.clickable { selected = p }) { ProblemCard(p, ProblemMarkStore.mark(p.id).takeIf { tick >= 0 }) }
        }
    }
    selected?.let { p -> Sheet({ selected = null; AppModel.refresh() }) { ProblemDetail(p) { selected = null; AppModel.refresh() } } }
}

/** 問題を解く（問題集から）。 */
@Composable
fun ProblemDetail(p: Problem, onClose: () -> Unit) {
    var stats by remember { mutableStateOf<Pair<Int, Int>?>(null) }
    LaunchedEffect(p.id) { stats = Community.stats(p.id) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp).padding(bottom = 40.dp),
        verticalArrangement = Arrangement.spacedBy(18.dp)) {
        SheetHeader(p.title, size = 20, onAction = onClose)
        val s = stats
        if (s != null && s.first >= 5) T("みんなの正答率 ${Math.round(s.second.toDouble() / s.first * 100)}%（${s.first}人が挑戦）", 13, W.semibold, Theme.inkSoft)
        else T("みんなの正答率：集計中", 13, color = Theme.inkFaint)
        ProblemSolver(p, onCorrect = {}, continueLabel = "とじる", onContinue = onClose)
    }
}
