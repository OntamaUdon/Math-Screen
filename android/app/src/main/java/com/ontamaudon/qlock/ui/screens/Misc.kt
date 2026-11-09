package com.ontamaudon.qlock.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.data.ParentLock
import com.ontamaudon.qlock.data.Store
import com.ontamaudon.qlock.ui.Card
import com.ontamaudon.qlock.ui.Divider
import com.ontamaudon.qlock.ui.IsoTextButton
import com.ontamaudon.qlock.ui.Kind
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.components.PasscodeSetup
import com.ontamaudon.qlock.ui.components.Sheet

/** プランを始めたあとに、1回だけ出す、保護者用設定の案内。 */
@Composable
fun ParentSetupIntro(onClose: () -> Unit) {
    var showSetup by remember { mutableStateOf(false) }
    Column(Modifier.fillMaxSize().padding(horizontal = 20.dp), verticalArrangement = Arrangement.spacedBy(18.dp)) {
        SheetHeader("保護者用設定", size = 24, action = "あとで", onAction = onClose)
        Card {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Icon(Icons.Filled.Lock, null, tint = Theme.ink, modifier = Modifier.size(16.dp))
                    T("ルールや設定を、パスコードで守れます", 16, W.bold)
                }
                T("オンにすると、ルールの変更・設定・プランの管理に、4桁のパスコードが必要になります。使う人が知らない数字にしておくと、勝手に変えられません。", 14, color = Theme.inkSoft)
                T("あとから、設定の「保護者用設定」で、オン・オフを切りかえられます（オフにするにも、パスコードが必要です）。", 13, color = Theme.inkSoft)
            }
        }
        IsoTextButton("パスコードを決める", { showSetup = true })
        IsoTextButton("あとで、設定でやる", onClose, kind = Kind.quiet)
    }
    if (showSetup) Sheet({ showSetup = false }) { PasscodeSetup { showSetup = false; if (ParentLock.hasPasscode) onClose() } }
}

/** 診断：見守りの動きを確かめる。 */
@Composable
fun Diagnostics(onClose: () -> Unit) {
    val m = AppModel
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp).padding(bottom = 32.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)) {
        SheetHeader("診断", action = "とじる", onAction = onClose)
        Card(padding = 0.dp) {
            Column {
                Row2("見守り（ユーザー補助）", if (m.guardEnabled) "オン" else "オフ"); Divider()
                Row2("通知", if (m.notificationsAllowed) "許可済み" else "オフ"); Divider()
                Row2("ルール", "${m.rules.size}件"); Divider()
                Row2("ロック中のルール", "${m.lockedRuleIDs.size}件"); Divider()
                Row2("プラン", if (m.isPremium) "解くロックプラン" else "無料")
            }
        }
        Card(padding = 0.dp) {
            Column {
                for ((i, k) in listOf("service" to "見守りのサービス", "lock" to "ロック", "launch" to "問題の画面").withIndex()) {
                    if (i > 0) Divider()
                    Column(Modifier.fillMaxWidth().padding(horizontal = 18.dp, vertical = 12.dp), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        T(k.second, 15, color = Theme.inkSoft)
                        T(Store.diagNote(k.first) ?: "まだ動いていません", 14, W.semibold)
                    }
                }
            }
        }
        T("最後に動いた時刻です。「まだ動いていません」のままなら、その部分はまだ動いていません。", 12, color = Theme.inkSoft)
    }
}

@Composable
private fun Row2(title: String, value: String) {
    Row(Modifier.fillMaxWidth().padding(horizontal = 18.dp, vertical = 14.dp)) {
        T(title, 15, color = Theme.inkSoft, modifier = Modifier.weight(1f))
        T(value, 15, W.semibold)
    }
}
