package com.ontamaudon.qlock.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.ScreenshotMode
import com.ontamaudon.qlock.billing.Billing
import com.ontamaudon.qlock.data.AppModel
import com.ontamaudon.qlock.ui.Card
import com.ontamaudon.qlock.ui.Divider
import com.ontamaudon.qlock.ui.IsoButton
import com.ontamaudon.qlock.ui.IsoTextButton
import com.ontamaudon.qlock.ui.Kind
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W
import com.ontamaudon.qlock.ui.components.findActivity
import com.ontamaudon.qlock.ui.kindInk

/** 解くロックプランの案内と購入の画面。 */
@Composable
fun PlanScreen(onClose: () -> Unit) {
    val ctx = LocalContext.current
    val sample = ScreenshotMode.active
    val img = remember { runCatching { ctx.assets.open("img/plan-lock.png").use { android.graphics.BitmapFactory.decodeStream(it) } }.getOrNull() }
    LaunchedEffect(Unit) { if (Billing.plans.isEmpty()) Billing.load() }
    LaunchedEffect(Billing.isSubscribed) { if (Billing.isSubscribed) { AppModel.refresh(); onClose() } }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp).padding(bottom = 40.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)) {
        SheetHeader("解くロックプラン", size = 24, onAction = onClose)
        img?.let { Image(it.asImageBitmap(), null, Modifier.fillMaxWidth().height(150.dp), contentScale = ContentScale.Fit) }

        if (Billing.isSubscribed) {
            Card {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Icon(Icons.Filled.CheckCircle, null, tint = Theme.tealDeep, modifier = Modifier.size(20.dp))
                        T("プランを利用中です", 17, W.bold, Theme.tealDeep)
                    }
                    T("解約や、お支払いの確認は、下のボタンから行えます。", 13, color = Theme.inkSoft)
                    IsoTextButton("プランの管理（解約など）", { Billing.openManage(ctx) }, kind = Kind.secondary)
                }
            }
        } else {
            Card {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    T("無料で使えるもの", 14, W.bold, Theme.inkSoft)
                    T("問題集（見る・探す・解く）と、記録。", 15)
                    Divider()
                    T("プランで使えるもの", 14, W.bold, Theme.inkSoft)
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Feature("アプリロック（使いすぎたら問題が出て、解くまでロック）")
                        Feature("ロック中の「別の問題」")
                        Feature("保護者用設定（ルールや設定を、パスコードで守る）")
                    }
                }
            }
            when {
                sample -> Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    PlanButton("月額　¥300 / 月", "最初の7日間は無料", false) {}
                    PlanButton("年額　¥2,400 / 年", "最初の7日間は無料（月あたり約200円）", true) {}
                }
                Billing.plans.isEmpty() -> Card {
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        T(if (Billing.message == null) "プランの情報を読み込み中です…" else "プランの情報を読み込めませんでした。", 14, color = Theme.inkSoft)
                        IsoTextButton("もう一度読み込む", { Billing.load() }, kind = Kind.secondary)
                    }
                }
                else -> Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    for (p in Billing.plans) {
                        val yearly = p.basePlanId == Billing.YEARLY
                        var detail = if (p.hasTrial) "最初の7日間は無料" else "いつでも解約できます"
                        if (yearly) detail += "（月あたり約${Math.round(p.priceMicros / 1_000_000.0 / 12)}円）"
                        PlanButton("${if (yearly) "年額" else "月額"}　${p.price} / ${if (yearly) "年" else "月"}", detail, yearly, enabled = !Billing.busy) {
                            ctx.findActivity()?.let { Billing.purchase(it, p) }
                        }
                    }
                }
            }
        }
        Billing.message?.let { T(it, 13, W.semibold, Theme.danger) }
        IsoTextButton("購入を復元", { Billing.restore() }, kind = Kind.quiet, enabled = !Billing.busy)

        // 購入の前に見せる説明（Google Play のサブスクのルールに合わせる）
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            T("・無料トライアルのあとは、選んだプランの料金が、Google Play に登録したお支払い方法に請求されます。", 12, color = Theme.inkSoft)
            T("・解約しない限り、自動で更新されます。無料トライアルの期間中に解約すると、請求されません。", 12, color = Theme.inkSoft)
            T("・解約は、Google Play ストアのアプリの「お支払いと定期購入」→「定期購入」から行えます。", 12, color = Theme.inkSoft)
            Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                T("利用規約", 13, W.semibold, Theme.tealDeep, Modifier.clickable { openUrl(ctx, LegalLinks.TERMS) })
                T("プライバシーポリシー", 13, W.semibold, Theme.tealDeep, Modifier.clickable { openUrl(ctx, LegalLinks.PRIVACY) })
            }
        }
    }
}

private fun openUrl(ctx: android.content.Context, url: String) {
    runCatching { ctx.startActivity(android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse(url))) }
}

@Composable
private fun Feature(text: String) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Icon(Icons.Filled.Check, null, tint = Theme.tealDeep, modifier = Modifier.padding(top = 3.dp).size(15.dp))
        T(text, 15, modifier = Modifier.weight(1f))
    }
}

@Composable
private fun PlanButton(title: String, detail: String, primary: Boolean, enabled: Boolean = true, onClick: () -> Unit) {
    val kind = if (primary) Kind.primary else Kind.secondary
    IsoButton(onClick, kind = kind, enabled = enabled) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(2.dp)) {
            T(title, 17, W.bold, kindInk(kind))
            T(detail, 13, color = kindInk(kind).copy(alpha = 0.9f))
        }
    }
}
