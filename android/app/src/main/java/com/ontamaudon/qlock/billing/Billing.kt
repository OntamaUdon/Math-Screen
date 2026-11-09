package com.ontamaudon.qlock.billing

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import com.android.billingclient.api.AcknowledgePurchaseParams
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.BillingClientStateListener
import com.android.billingclient.api.BillingFlowParams
import com.android.billingclient.api.BillingResult
import com.android.billingclient.api.PendingPurchasesParams
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.Purchase
import com.android.billingclient.api.QueryProductDetailsParams
import com.android.billingclient.api.QueryPurchasesParams
import com.ontamaudon.qlock.data.AppModel
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * 解くロックプランの課金（Google Play Billing）。月額300円・年額2,400円・初めての人は7日間無料。
 * 価格と無料期間は、Play Console の商品の設定で決まる（ここでは、Play から受け取った値を出すだけ）。
 *
 * Play Console で作る商品（定期購入）：
 *   商品 ID   com.ontamaudon.qlock.plan
 *   基本プラン monthly（1か月・自動更新）、yearly（1年・自動更新）
 *   特典      それぞれの基本プランに、7日間の無料試用（新規ユーザーのみ）
 */
object Billing {
    const val PRODUCT_ID = "com.ontamaudon.qlock.plan"
    const val MONTHLY = "monthly"
    const val YEARLY = "yearly"

    enum class State { unknown, subscribed, notSubscribed }

    /** 画面に出す、1つのプラン。 */
    data class Plan(val basePlanId: String, val price: String, val priceMicros: Long, val hasTrial: Boolean, val offerToken: String)

    var state by mutableStateOf(State.unknown); private set
    val isSubscribed: Boolean get() = state == State.subscribed
    var plans by mutableStateOf<List<Plan>>(emptyList()); private set
    var message by mutableStateOf<String?>(null); private set
    var busy by mutableStateOf(false); private set
    var loading by mutableStateOf(false); private set

    private var details: ProductDetails? = null
    private var client: BillingClient? = null

    fun start(ctx: Context) {
        if (client != null) return
        val c = BillingClient.newBuilder(ctx.applicationContext)
            .setListener { result, purchases -> onPurchases(result, purchases) }
            .enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
            .enableAutoServiceReconnection()
            .build()
        client = c
        c.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(result: BillingResult) {
                if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                    refresh()
                    load()
                } else {
                    message = "Google Play に接続できませんでした。（${result.responseCode}）"
                }
            }
            override fun onBillingServiceDisconnected() {}
        })
    }

    /** いまの契約の状態を確かめる。 */
    fun refresh() {
        val c = client ?: return
        c.queryPurchasesAsync(QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.SUBS).build()) { result, purchases ->
            if (result.responseCode != BillingClient.BillingResponseCode.OK) return@queryPurchasesAsync
            handle(purchases)
        }
    }

    /** 商品（価格と無料期間）を読み込む。 */
    fun load() {
        val c = client ?: return
        loading = true
        message = null
        val product = QueryProductDetailsParams.Product.newBuilder()
            .setProductId(PRODUCT_ID).setProductType(BillingClient.ProductType.SUBS).build()
        c.queryProductDetailsAsync(QueryProductDetailsParams.newBuilder().setProductList(listOf(product)).build()) { result, res ->
            AppModel.scope.launchMain {
                loading = false
                val pd = res.productDetailsList.firstOrNull()
                if (result.responseCode != BillingClient.BillingResponseCode.OK || pd == null) {
                    message = "プランの情報を読み込めませんでした。"
                    return@launchMain
                }
                details = pd
                plans = listOf(MONTHLY, YEARLY).mapNotNull { base -> plan(pd, base) }
            }
        }
    }

    private fun plan(pd: ProductDetails, base: String): Plan? {
        val offers = pd.subscriptionOfferDetails?.filter { it.basePlanId == base } ?: return null
        if (offers.isEmpty()) return null
        // 無料の期間がある特典（受けられる人にだけ、Play が返す）を優先する
        val trial = offers.firstOrNull { o -> o.pricingPhases.pricingPhaseList.any { it.priceAmountMicros == 0L } }
        val offer = trial ?: offers.firstOrNull { it.offerId == null } ?: offers.first()
        val last = offer.pricingPhases.pricingPhaseList.last()
        return Plan(base, last.formattedPrice, last.priceAmountMicros, trial != null, offer.offerToken)
    }

    fun purchase(activity: Activity, plan: Plan) {
        val c = client ?: return
        val pd = details ?: return
        busy = true
        message = null
        val params = BillingFlowParams.newBuilder().setProductDetailsParamsList(listOf(
            BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(pd).setOfferToken(plan.offerToken).build()
        )).build()
        val r = c.launchBillingFlow(activity, params)
        if (r.responseCode != BillingClient.BillingResponseCode.OK) {
            busy = false
            message = "購入の画面を開けませんでした。（${r.responseCode}）"
        }
    }

    private fun onPurchases(result: BillingResult, purchases: List<Purchase>?) {
        AppModel.scope.launchMain {
            busy = false
            when (result.responseCode) {
                BillingClient.BillingResponseCode.OK -> handle(purchases ?: emptyList())
                BillingClient.BillingResponseCode.USER_CANCELED -> {}
                else -> message = "購入できませんでした。（${result.responseCode}）"
            }
        }
    }

    private fun handle(purchases: List<Purchase>) {
        val c = client
        val active = purchases.filter { PRODUCT_ID in it.products && it.purchaseState == Purchase.PurchaseState.PURCHASED }
        for (p in active) {
            if (!p.isAcknowledged && c != null) {
                c.acknowledgePurchase(AcknowledgePurchaseParams.newBuilder().setPurchaseToken(p.purchaseToken).build()) {}
            }
        }
        AppModel.scope.launchMain {
            state = if (active.isNotEmpty()) State.subscribed else State.notSubscribed
            AppModel.refresh()
        }
    }

    /** 購入の復元。Play では、同じ Google アカウントなら自動で引きつがれるので、状態を確かめ直すだけ。 */
    fun restore() {
        message = null
        refresh()
    }

    /** Google Play の「定期購入」の画面（解約など）。 */
    fun openManage(ctx: Context) {
        val uri = Uri.parse("https://play.google.com/store/account/subscriptions?sku=$PRODUCT_ID&package=${ctx.packageName}")
        runCatching { ctx.startActivity(Intent(Intent.ACTION_VIEW, uri).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) }
    }
}

private fun CoroutineScope.launchMain(block: () -> Unit) {
    launch(Dispatchers.Main) { block() }
}
