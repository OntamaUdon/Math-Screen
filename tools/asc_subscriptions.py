"""App Store Connect API で、サブスクリプション（解くロックプラン）を作る。

  python tools/asc_subscriptions.py check   … 読むだけ。アプリ・既存の商品・日本の価格（300円・2,400円）があるかを調べる
  python tools/asc_subscriptions.py create  … グループ・月額・年額の商品、日本語の表示、価格、7日間の無料トライアル、販売地域（日本）を作る

作り直しても重複しないように、すでにあるものは作らない（製品IDで見分ける）。
環境変数: KEY_PATH（.p8 のパス）, ASC_KEY_ID, ASC_ISSUER_ID
"""
import hashlib, json, os, sys, urllib.error, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ci_signing import call, must

BUNDLE_ID = "com.ontamaudon.qlock"
GROUP_NAME = "解くロックプラン"
TERRITORY = "JPN"
PLANS = [
    # 製品ID, 参照名, 期間, 価格（円）, 表示名, 説明
    ("com.ontamaudon.qlock.plan.monthly", "解くロックプラン 月額", "ONE_MONTH", 300,
     "解くロックプラン（月額）", "アプリロックなど、すべての機能が使えます。"),
    ("com.ontamaudon.qlock.plan.yearly", "解くロックプラン 年額", "ONE_YEAR", 2400,
     "解くロックプラン（年額）", "アプリロックなど、すべての機能が使えます。"),
]


def get_all(path):
    """ページ送りをたどって、すべて取る。"""
    out, url = [], path
    for _ in range(40):
        st, res = call("GET", url)
        must(st, res, f"取得 {path}")
        out += res.get("data", [])
        url = res.get("links", {}).get("next")
        if not url:
            break
    return out


def find_app():
    st, res = call("GET", "/apps?" + urllib.parse.urlencode({"filter[bundleId]": BUNDLE_ID}))
    must(st, res, "アプリの検索")
    if not res.get("data"):
        print(f"::error::Bundle ID {BUNDLE_ID} のアプリが見つかりません"); sys.exit(1)
    return res["data"][0]["id"]


def existing(app_id):
    """既存のグループと商品を {グループ: id}, {製品ID: (id, グループid)} で返す。"""
    groups, subs = {}, {}
    for g in get_all(f"/apps/{app_id}/subscriptionGroups?limit=50"):
        groups[g["attributes"]["referenceName"]] = g["id"]
        for s in get_all(f"/subscriptionGroups/{g['id']}/subscriptions?limit=50"):
            subs[s["attributes"]["productId"]] = (s["id"], g["id"])
    return groups, subs


def price_point(sub_id, yen):
    q = urllib.parse.urlencode({"filter[territory]": TERRITORY, "limit": 200})
    for p in get_all(f"/subscriptions/{sub_id}/pricePoints?{q}"):
        try:
            if float(p["attributes"]["customerPrice"]) == float(yen):
                return p["id"]
        except (KeyError, ValueError):
            pass
    return None


def parts(sid):
    """商品に、すでに付いているもの。"""
    def safe(path):
        st, res = call("GET", path)
        return res.get("data") if st == 200 else None
    return {
        "localizations": get_all(f"/subscriptions/{sid}/subscriptionLocalizations"),
        "prices": get_all(f"/subscriptions/{sid}/prices?limit=50"),
        "offers": get_all(f"/subscriptions/{sid}/introductoryOffers?limit=50"),
        "availability": safe(f"/subscriptions/{sid}/subscriptionAvailability"),
    }


def detail(sid):
    st, res = call("GET", f"/subscriptions/{sid}")
    a = res.get("data", {}).get("attributes", {}) if st == 200 else {}
    print(f"  状態: {a.get('state')} ／ 期間: {a.get('subscriptionPeriod')} ／ 参照名: {a.get('name')}")
    pr = parts(sid)
    print("  日本語の表示名:", [(l["attributes"]["locale"], l["attributes"]["name"]) for l in pr["localizations"]] or "なし")
    print(f"  価格の設定: {len(pr['prices'])} 件")
    print("  無料トライアル:", [(o["attributes"].get("offerMode"), o["attributes"].get("duration")) for o in pr["offers"]] or "なし")
    av = pr["availability"]
    if av:
        terr = [t["id"] for t in get_all(f"/subscriptionAvailabilities/{av['id']}/availableTerritories?limit=200")]
        print(f"  販売地域: {len(terr)} か国・地域", "（日本だけ）" if terr == [TERRITORY] else "")
    else:
        print("  販売地域の設定: なし")


def check():
    app_id = find_app()
    print(f"アプリ: {app_id}")
    groups, subs = existing(app_id)
    print("既存のグループ:", list(groups) or "なし")
    print("既存の商品:", list(subs) or "なし")
    # 価格の確認は、商品がないと取れないので、既存の商品があれば確認する
    for pid, name, period, yen, *_ in PLANS:
        if pid in subs:
            print(f"【{pid}】")
            pp = price_point(subs[pid][0], yen)
            print(f"  日本の {yen} 円の価格（選べるか）: {'あり' if pp else '見つかりません'}")
            detail(subs[pid][0])
    print("確認は終わりました（確認だけで、何も変えていません）。")


REVIEW_NOTE = ("購入画面の見つけかた：アプリを開いて、設定タブの「プランを見る」、またはホームの「プランを見る」を押すと、"
               "解くロックプラン（月額300円・年額2,400円、初回7日間無料）の購入画面が開きます。"
               "無料で使えるのは、問題集（見る・解く）と記録です。アプリロックなどは、プランで使えます。")


def put_bytes(op, data):
    chunk = data[op["offset"]: op["offset"] + op["length"]]
    req = urllib.request.Request(op["url"], data=chunk, method=op["method"],
                                 headers={h["name"]: h["value"] for h in op.get("requestHeaders", [])})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status
    except urllib.error.HTTPError as e:
        print(f"::error::アップロードに失敗しました（{e.code}）"); sys.exit(1)


def review_shot():
    """審査用のスクリーンショット（store/screenshots/plan.png）と審査メモを、すべての商品に入れる。すでにあれば入れ替える。"""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "store", "screenshots", "plan.png")
    data = open(path, "rb").read()
    app_id = find_app()
    groups, subs = existing(app_id)
    # グループの日本語の表示名（なければ足す。ないと「メタデータ不足」のままになる）
    gid = groups.get(GROUP_NAME)
    if gid:
        if not get_all(f"/subscriptionGroups/{gid}/subscriptionGroupLocalizations"):
            must(*call("POST", "/subscriptionGroupLocalizations", {"data": {"type": "subscriptionGroupLocalizations",
                "attributes": {"name": GROUP_NAME, "customAppName": "解くロック", "locale": "ja"},
                "relationships": {"subscriptionGroup": {"data": {"type": "subscriptionGroups", "id": gid}}}}}), "グループの表示名")
            print("グループの日本語の表示名を入れました")
        else:
            print("グループの日本語の表示名は、すでにあります")
    for pid, *_ in PLANS:
        if pid not in subs:
            print(f"商品がありません: {pid}"); continue
        sid = subs[pid][0]
        # 日本語の説明を、いまの文に合わせる
        for loc in get_all(f"/subscriptions/{sid}/subscriptionLocalizations"):
            if loc["attributes"]["locale"] == "ja":
                desc = next(p[5] for p in PLANS if p[0] == pid)
                must(*call("PATCH", f"/subscriptionLocalizations/{loc['id']}", {"data": {"type": "subscriptionLocalizations",
                    "id": loc["id"], "attributes": {"description": desc}}}), f"説明 {pid}")
        # 審査メモ
        must(*call("PATCH", f"/subscriptions/{sid}", {"data": {"type": "subscriptions", "id": sid,
            "attributes": {"reviewNote": REVIEW_NOTE}}}), f"審査メモ {pid}")
        # すでにある画像は消して入れ替える
        st, res = call("GET", f"/subscriptions/{sid}/appStoreReviewScreenshot")
        old = res.get("data") if st == 200 else None
        if old:
            must(*call("DELETE", f"/subscriptionAppStoreReviewScreenshots/{old['id']}"), f"古い画像の削除 {pid}")
        res = must(*call("POST", "/subscriptionAppStoreReviewScreenshots", {"data": {"type": "subscriptionAppStoreReviewScreenshots",
            "attributes": {"fileName": "plan.png", "fileSize": len(data)},
            "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}}}}}), f"画像の予約 {pid}")
        shot = res["data"]
        for op in shot["attributes"]["uploadOperations"]:
            put_bytes(op, data)
        must(*call("PATCH", f"/subscriptionAppStoreReviewScreenshots/{shot['id']}", {"data": {
            "type": "subscriptionAppStoreReviewScreenshots", "id": shot["id"],
            "attributes": {"uploaded": True, "sourceFileChecksum": hashlib.md5(data).hexdigest()}}}), f"画像の確定 {pid}")
        print(f"{pid}: 審査用の画像と審査メモを入れました")


def japan_only():
    """すべての商品の販売地域を、日本だけにそろえる。"""
    app_id = find_app()
    groups, subs = existing(app_id)
    for pid, *_ in PLANS:
        if pid not in subs:
            print(f"商品がありません: {pid}"); continue
        sid = subs[pid][0]
        av = parts(sid)["availability"]
        before = [t["id"] for t in get_all(f"/subscriptionAvailabilities/{av['id']}/availableTerritories?limit=200")] if av else []
        if before == [TERRITORY]:
            print(f"{pid}: すでに日本だけです"); continue
        must(*call("POST", "/subscriptionAvailabilities", {"data": {"type": "subscriptionAvailabilities",
            "attributes": {"availableInNewTerritories": False},
            "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}},
                              "availableTerritories": {"data": [{"type": "territories", "id": TERRITORY}]}}}}), f"販売地域を日本だけに {pid}")
        print(f"{pid}: 販売地域を {len(before)} か国・地域から、日本だけにしました")


def create():
    app_id = find_app()
    groups, subs = existing(app_id)

    # 1. グループ
    gid = groups.get(GROUP_NAME)
    if not gid:
        res = must(*call("POST", "/subscriptionGroups", {"data": {"type": "subscriptionGroups",
            "attributes": {"referenceName": GROUP_NAME},
            "relationships": {"app": {"data": {"type": "apps", "id": app_id}}}}}), "グループの作成")
        gid = res["data"]["id"]
        print(f"グループを作りました: {GROUP_NAME}")
        must(*call("POST", "/subscriptionGroupLocalizations", {"data": {"type": "subscriptionGroupLocalizations",
            "attributes": {"name": GROUP_NAME, "customAppName": "解くロック", "locale": "ja"},
            "relationships": {"subscriptionGroup": {"data": {"type": "subscriptionGroups", "id": gid}}}}}), "グループの表示名")
    else:
        print(f"グループは、すでにあります: {GROUP_NAME}")

    for level, (pid, name, period, yen, title, desc) in enumerate(PLANS, start=1):
        # 2. 商品（すでにあれば、作らない。中身は変えない）
        if pid in subs:
            sid = subs[pid][0]
            print(f"商品は、すでにあります: {pid}（足りないものだけ足します）")
        else:
            res = must(*call("POST", "/subscriptions", {"data": {"type": "subscriptions",
                "attributes": {"name": name, "productId": pid, "subscriptionPeriod": period,
                               "familySharable": False, "groupLevel": 1},
                "relationships": {"group": {"data": {"type": "subscriptionGroups", "id": gid}}}}}), f"商品の作成 {pid}")
            sid = res["data"]["id"]
            print(f"商品を作りました: {pid}")
        have = parts(sid)
        # 3. 日本語の表示名・説明
        if not have["localizations"]:
            must(*call("POST", "/subscriptionLocalizations", {"data": {"type": "subscriptionLocalizations",
                "attributes": {"name": title, "description": desc, "locale": "ja"},
                "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}}}}}), f"表示名 {pid}")
            print("  日本語の表示名を入れました")
        # 4. 販売地域：日本
        if not have["availability"]:
            must(*call("POST", "/subscriptionAvailabilities", {"data": {"type": "subscriptionAvailabilities",
                "attributes": {"availableInNewTerritories": False},
                "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}},
                                  "availableTerritories": {"data": [{"type": "territories", "id": TERRITORY}]}}}}), f"販売地域 {pid}")
            print("  販売地域（日本）を設定しました")
        # 5. 価格（日本）
        if not have["prices"]:
            pp = price_point(sid, yen)
            if not pp:
                print(f"::error::日本の {yen} 円の価格が見つかりません（{pid}）。"); sys.exit(1)
            must(*call("POST", "/subscriptionPrices", {"data": {"type": "subscriptionPrices",
                "attributes": {"preserveCurrentPrice": False},
                "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}},
                                  "subscriptionPricePoint": {"data": {"type": "subscriptionPricePoints", "id": pp}},
                                  "territory": {"data": {"type": "territories", "id": TERRITORY}}}}}), f"価格 {pid}")
            print(f"  価格を設定しました: {yen} 円")
        # 6. 7日間の無料トライアル
        if not have["offers"]:
            must(*call("POST", "/subscriptionIntroductoryOffers", {"data": {"type": "subscriptionIntroductoryOffers",
                "attributes": {"duration": "ONE_WEEK", "offerMode": "FREE_TRIAL", "numberOfPeriods": 1},
                "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}},
                                  "territory": {"data": {"type": "territories", "id": TERRITORY}}}}}), f"無料トライアル {pid}")
            print("  無料トライアル（7日間）を付けました")
    print("完了しました。審査用のスクリーンショットは、まだ入っていません。")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"check": check, "create": create, "japan": japan_only, "review-shot": review_shot}[mode]()
