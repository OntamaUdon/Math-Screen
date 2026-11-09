package com.ontamaudon.qlock.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.AddBox
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.LibraryAddCheck
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.outlined.Hub
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.GuardRule
import com.ontamaudon.qlock.data.Subject
import com.ontamaudon.qlock.data.UnitCatalog
import com.ontamaudon.qlock.guard.AppCatalog
import com.ontamaudon.qlock.ui.Card
import com.ontamaudon.qlock.ui.Divider
import com.ontamaudon.qlock.ui.IsoBackground
import com.ontamaudon.qlock.ui.IsoButton
import com.ontamaudon.qlock.ui.Kind
import com.ontamaudon.qlock.ui.SectionLabel
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Tag
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.components.AppIcon
import com.ontamaudon.qlock.ui.components.CheckState
import com.ontamaudon.qlock.ui.components.Confirm
import com.ontamaudon.qlock.ui.components.FullScreen
import com.ontamaudon.qlock.ui.components.MapNode
import com.ontamaudon.qlock.ui.components.MindMap
import com.ontamaudon.qlock.ui.components.Sheet
import com.ontamaudon.qlock.ui.components.WheelPicker
import com.ontamaudon.qlock.ui.well

@Composable
fun RuleEditor(initial: GuardRule, isNew: Boolean, onClose: () -> Unit) {
    var rule by remember { mutableStateOf(initial) }
    var showPicker by remember { mutableStateOf(false) }
    var confirmDelete by remember { mutableStateOf(false) }
    var showRangeMap by remember { mutableStateOf(false) }
    var sel by remember {
        mutableStateOf(
            if (initial.units.isEmpty()) UnitCatalog.available.filter { (UnitCatalog.categories[it.id] ?: emptySet()).all { c -> c in initial.categories } }.map { it.id }.toSet()
            else initial.units
        )
    }
    fun apply(s: Set<String>) {
        if (s.isEmpty()) return
        val real = s.filter { UnitCatalog.categories[it] != null }.toSet()
        val cats = real.flatMap { UnitCatalog.categories[it] ?: emptySet() }.toSet()
        if (cats.isEmpty()) return
        val closure = UnitCatalog.available.filter { (UnitCatalog.categories[it.id] ?: emptySet()).all { c -> c in cats } }.map { it.id }.toSet()
        rule = rule.copy(categories = cats, units = if (real == closure) emptySet() else real)
    }
    LaunchedEffect(sel) { apply(sel) }
    val canSave = rule.itemCount > 0 && sel.isNotEmpty()

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp).padding(bottom = 40.dp),
        verticalArrangement = Arrangement.spacedBy(22.dp)) {
        SheetHeader(if (isNew) "ルールを追加" else "ルールを編集", action = "保存", actionColor = if (canSave) Theme.tealDeep else Theme.inkFaint,
            actionWeight = W.bold, actionEnabled = canSave) { AppModel.save(rule); onClose() }

        Section("制限するアプリ") {
            IsoButton({ showPicker = true }, kind = if (rule.itemCount == 0) Kind.alert else Kind.primary) {
                Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    Icon(if (rule.itemCount == 0) Icons.Filled.AddBox else Icons.Filled.LibraryAddCheck, null, tint = Color.White, modifier = Modifier.size(28.dp))
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        T(if (rule.itemCount == 0) "制限するアプリを選ぶ" else "${rule.itemCount}件を選択中", 20, W.heavy, Color.White)
                        if (rule.itemCount > 0) T("タップして変更", 12, W.semibold, Color.White.copy(alpha = 0.85f))
                    }
                    Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Color.White, modifier = Modifier.size(22.dp))
                }
            }
            T("「解くロック」自身は、選んでも対象になりません。", 12, color = Theme.inkSoft)
            if (rule.packages.isNotEmpty() || rule.appCategories.isNotEmpty()) {
                Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(10.dp),
                    verticalAlignment = Alignment.CenterVertically) {
                    for (c in rule.appCategories) Tag(AppCatalog.categoryLabel(c), true)
                    for (p in rule.packages) AppIcon(p, 32.dp)
                }
            }
        }

        Section("どれだけ使うごとに") {
            Card(padding = 10.dp) {
                Row {
                    WheelPicker((0..12).toList(), rule.thresholdMinutes / 60, { "${it}時間" }, { h ->
                        rule = rule.copy(thresholdMinutes = (h * 60 + rule.thresholdMinutes % 60).coerceIn(1, GuardRule.MAX_MINUTES))
                    }, Modifier.weight(1f))
                    WheelPicker((0 until 60).toList(), rule.thresholdMinutes % 60, { "${it}分" }, { mm ->
                        rule = rule.copy(thresholdMinutes = (rule.thresholdMinutes / 60 * 60 + mm).coerceIn(1, GuardRule.MAX_MINUTES))
                    }, Modifier.weight(1f), enabled = rule.thresholdMinutes < GuardRule.MAX_MINUTES)
                }
            }
        }

        Section("何問出すか") {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for (v in 1..5) {
                    Box(Modifier.weight(1f).clickable { rule = rule.copy(questionCount = v) }) {
                        Tag("${v}問", rule.questionCount == v, Modifier.fillMaxWidth())
                    }
                }
            }
        }

        Section("出題する範囲") {
            Box(Modifier.clickable { showRangeMap = true }) {
                Card(padding = 14.dp) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        Icon(Icons.Outlined.Hub, null, tint = Theme.tealDeep, modifier = Modifier.size(24.dp))
                        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            T(rangeSummary(sel), 15, W.bold)
                            T("マップで教科・単元を選ぶ", 12, color = Theme.inkSoft)
                        }
                        Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = Theme.inkFaint, modifier = Modifier.size(18.dp))
                    }
                }
            }
            T(if (rule.units.isEmpty()) "教科をまるごと選ぶと、苦手な単元から出します。慣れてきたら、むずかしい問題や次の単元にも進みます。" else "選んだ単元だけが出ます。",
                12, color = Theme.inkSoft)
        }

        val d = GuardRule.durationText(rule.thresholdMinutes)
        T("選んだアプリを合計 $d 使うとロックされます。${rule.questionCount}問に正解すれば、また使えます。そのあと $d 使うと、またロックされます。（時間と問題数が同じルールは、ひとつにまとまります）",
            13, color = Theme.inkSoft)

        if (!isNew) {
            Box(Modifier.fillMaxWidth().clickable { confirmDelete = true }.padding(8.dp), contentAlignment = Alignment.Center) {
                T("このルールを削除", 15, W.semibold, Theme.danger)
            }
        }
    }

    if (showPicker) {
        Sheet({ showPicker = false }) {
            AppPicker(rule.packages, rule.appCategories) { p, c -> rule = rule.copy(packages = p, appCategories = c); showPicker = false }
        }
    }
    if (showRangeMap) {
        FullScreen({ showRangeMap = false }) { RangeMap(sel, { sel = it }) { showRangeMap = false } }
    }
    if (confirmDelete) {
        Confirm("このルールを削除しますか？", buttons = listOf("削除" to { AppModel.delete(rule); onClose() }), destructiveFirst = true) { confirmDelete = false }
    }
}

@Composable
private fun Section(title: String, content: @Composable () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        SectionLabel(title)
        content()
    }
}

/** 例：「数学（すべて）・英語（3単元）」 */
private fun rangeSummary(sel: Set<String>): String {
    if (sel.isEmpty()) return "範囲を選んでください"
    return Subject.entries.mapNotNull { s ->
        val all = UnitCatalog.units(s).map { it.id }
        val n = all.count { it in sel }
        if (n == 0) null else "${s.label}（${if (n == all.size) "すべて" else "${n}単元"}）"
    }.joinToString("・")
}

/** 制限するアプリを選ぶ画面（iPhone のスクリーンタイムの選択画面の代わり）。 */
@Composable
private fun AppPicker(initialPackages: Set<String>, initialCategories: Set<Int>, onDone: (Set<String>, Set<Int>) -> Unit) {
    val ctx = LocalContext.current
    val apps = remember { AppCatalog.launcherApps(ctx) }
    var picked by remember { mutableStateOf(initialPackages) }
    var cats by remember { mutableStateOf(initialCategories) }
    var query by remember { mutableStateOf("") }
    Column(Modifier.fillMaxSize().padding(horizontal = 20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        SheetHeader("制限するアプリ", action = "完了", actionColor = Theme.tealDeep, actionWeight = W.bold) { onDone(picked, cats) }
        T("制限するアプリを選んでください。種類を選ぶと、その種類のアプリがまとめて対象になります（あとから入れたアプリも含みます）。", 13, color = Theme.inkSoft)
        SectionLabel("アプリの種類")
        Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            for ((c, label) in AppCatalog.selectableCategories) {
                Box(Modifier.clickable { cats = if (c in cats) cats - c else cats + c }) { Tag(label, c in cats) }
            }
        }
        Row(Modifier.fillMaxWidth().well().padding(12.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Icon(Icons.Filled.Search, null, tint = Theme.inkFaint, modifier = Modifier.size(20.dp))
            Box(Modifier.weight(1f)) {
                if (query.isEmpty()) T("アプリを検索", 16, color = Theme.inkFaint)
                BasicTextField(query, { query = it }, singleLine = true, textStyle = Theme.font(16), modifier = Modifier.fillMaxWidth())
            }
        }
        SectionLabel("アプリ（${picked.size}件を選択中）")
        val shown = apps.filter { query.isBlank() || it.label.contains(query, ignoreCase = true) }
        Card(padding = 0.dp, modifier = Modifier.weight(1f)) {
            LazyColumn {
                items(shown, key = { it.pkg }) { a ->
                    val on = a.pkg in picked
                    Column {
                        Row(Modifier.fillMaxWidth().background(if (on) Theme.teal.copy(alpha = 0.12f) else Color.Transparent)
                            .clickable { picked = if (on) picked - a.pkg else picked + a.pkg }
                            .padding(horizontal = 16.dp, vertical = 10.dp),
                            verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            Icon(if (on) Icons.Filled.CheckCircle else Icons.Filled.RadioButtonUnchecked, null,
                                tint = if (on) Theme.tealDeep else Theme.inkFaint, modifier = Modifier.size(24.dp))
                            AppIcon(a.pkg, 32.dp)
                            T(a.label, 15, W.semibold, modifier = Modifier.weight(1f), maxLines = 1)
                        }
                        Divider(Modifier.padding(start = 16.dp))
                    }
                }
            }
        }
        Box(Modifier.padding(bottom = 16.dp))
    }
}

/** 出題範囲を、マインドマップで選ぶ画面。チェックを付けた単元が出題される。 */
@Composable
fun RangeMap(selected: Set<String>, onChange: (Set<String>) -> Unit, onClose: () -> Unit) {
    val initial = remember { selected }
    val root = remember { BookMap.selector() }
    fun leaves(n: MapNode): List<String> =
        if (n.children.isEmpty()) (if (n.id.startsWith("u:")) listOf(n.id.drop(2)) else emptyList()) else n.children.flatMap { leaves(it) }
    fun state(n: MapNode): CheckState {
        val ids = leaves(n)
        if (ids.isEmpty()) return CheckState.off
        val k = ids.count { it in selected }
        return if (k == 0) CheckState.off else if (k == ids.size) CheckState.on else CheckState.partial
    }
    fun toggle(n: MapNode) {
        val ids = leaves(n).toSet()
        onChange(if (state(n) == CheckState.on) selected - ids else selected + ids)
    }
    IsoBackground {
        Column(Modifier.fillMaxSize().statusBarsPadding(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Box(Modifier.padding(horizontal = 20.dp)) {
                SheetHeader("出題する範囲", action = if (selected.isEmpty()) "もとに戻す" else "完了", actionColor = Theme.tealDeep, actionWeight = W.bold) {
                    if (selected.isEmpty()) onChange(initial)
                    onClose()
                }
            }
            T(if (selected.isEmpty()) "出したい教科や単元に、チェックを付けてください。" else "選んだ単元：${selected.size}", 13, W.semibold,
                if (selected.isEmpty()) Theme.danger else Theme.tealDeep, Modifier.padding(horizontal = 20.dp))
            MindMap(root, Modifier.weight(1f), openPath = listOf("root"), checkState = { state(it) }, onCheck = { toggle(it) }) { toggle(it) }
        }
    }
}
