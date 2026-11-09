package com.ontamaudon.qlock.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.ontamaudon.qlock.ui.Card
import com.ontamaudon.qlock.ui.IsoTextButton
import com.ontamaudon.qlock.ui.Kind
import com.ontamaudon.qlock.ui.SectionLabel
import com.ontamaudon.qlock.ui.T
import com.ontamaudon.qlock.ui.Theme
import com.ontamaudon.qlock.ui.W

/**
 * ユーザー補助サービスを使う前の説明と同意（Google Play のルールで必要な「目立つ説明」）。
 * 何を受け取り、何に使い、外へ送らないことを、オンにする前に見せる。同意しなくても、問題集と記録は使える。
 */
@Composable
fun GuardDisclosureContent() {
    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
        T("「見守り」には、Android の「ユーザー補助」の機能を使います。", 16, color = Theme.inkSoft)
        Card {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                SectionLabel("受け取る情報")
                Line(true, "いま前に出ているアプリの名前（例：「YouTube が開いた」）")
                SectionLabel("使いみち")
                Line(true, "決めたアプリを使った時間を数える")
                Line(true, "時間になったら、そのアプリの上に問題の画面を出す")
                SectionLabel("しないこと")
                Line(false, "画面に表示されている文字や、入力した内容（パスワードなど）は読み取りません")
                Line(false, "受け取った情報を、外へ送ったり、ほかの人に渡したりしません（この端末の中だけで使います）")
            }
        }
        T("「同意して設定を開く」を押すと、Android の設定が開きます。「インストール済みのアプリ」（または「ダウンロードしたアプリ」）の中の「解くロック（見守り）」をオンにしてください。オフにすれば、いつでもやめられます。",
            13, color = Theme.inkSoft)
        T("同意しなくても、問題集と記録は使えます。アプリのロックだけが使えません。", 13, color = Theme.inkSoft)
    }
}

@Composable
private fun Line(ok: Boolean, text: String) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.Top) {
        Icon(if (ok) Icons.Filled.Check else Icons.Filled.Close, null, tint = if (ok) Theme.tealDeep else Theme.coralDeep,
            modifier = Modifier.padding(top = 2.dp).size(16.dp))
        T(text, 15, modifier = Modifier.weight(1f))
    }
}

/** 設定の画面から開く、説明と同意の画面。 */
@Composable
fun GuardDisclosureSheet(onAgree: () -> Unit, onDecline: () -> Unit) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp).padding(bottom = 32.dp),
        verticalArrangement = Arrangement.spacedBy(18.dp)) {
        SheetHeader("見守りをオンにする", onAction = onDecline)
        GuardDisclosureContent()
        IsoTextButton("同意して設定を開く", onAgree)
        IsoTextButton("同意しない", onDecline, kind = Kind.quiet)
    }
}

@Suppress("unused")
private val keepW = W.bold
