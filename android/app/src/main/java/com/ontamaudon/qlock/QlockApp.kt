package com.ontamaudon.qlock

import android.app.Application
import com.ontamaudon.qlock.billing.Billing
import com.ontamaudon.qlock.data.ProblemBank
import com.ontamaudon.qlock.data.UnitCatalog
import com.ontamaudon.qlock.guard.ChallengeNotification

class QlockApp : Application() {
    override fun onCreate() {
        super.onCreate()
        instance = this
        // 問題データ（約7MB）の読み込みを、画面を出しながら裏で始める
        Thread {
            ProblemBank.all
            UnitCatalog.problemCount
            UnitCatalog.categories
        }.start()
        ChallengeNotification.ensureChannel(this)
        Billing.start(this)
    }

    companion object {
        lateinit var instance: QlockApp
            private set
    }
}
