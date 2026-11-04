"""App Store Connect API で、サブスクリプション（解くロックプラン）を作る。

  python tools/asc_subscriptions.py check   … 読むだけ。アプリ・既存の商品・日本の価格（300円・2,400円）があるかを調べる
  python tools/asc_subscriptions.py create  … グループ・月額・年額の商品、日本語の表示、価格、7日間の無料トライアル、販売地域（日本）を作る

作り直しても重複しないように、すでにあるものは作らない（製品IDで見分ける）。
環境変数: KEY_PATH（.p8 のパス）, ASC_KEY_ID, ASC_ISSUER_ID
"""
import json, os, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ci_signing import call, must

BUNDLE_ID = "com.ontamaudon.qlock"
GROUP_NAME = "解くロックプラン"
TERRITORY = "JPN"
PLANS = [
    # 製品ID, 参照名, 期間, 価格（円）, 表示名, 説明
    ("com.ontamaudon.qlock.plan.monthly", "解くロックプラン 月額", "ONE_MONTH", 300,
     "解くロックプラン（月額）", "アプリロック、記録、投稿など、すべての機能が使えます。"),
    ("com.ontamaudon.qlock.plan.yearly", "解くロックプラン 年額", "ONE_YEAR", 2400,
     "解くロックプラン（年額）", "アプリロック、記録、投稿など、すべての機能が使えます。"),
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


def check():
    app_id = find_app()
    print(f"アプリ: {app_id}")
    groups, subs = existing(app_id)
    print("既存のグループ:", list(groups) or "なし")
    print("既存の商品:", list(subs) or "なし")
    # 価格の確認は、商品がないと取れないので、既存の商品があれば確認する
    for pid, name, period, yen, *_ in PLANS:
        if pid in subs:
            pp = price_point(subs[pid][0], yen)
            print(f"{pid}: 日本の {yen} 円の価格 → {'あり' if pp else '見つかりません'}")
    print("確認は終わりました（何も作っていません）。")


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
        # 2. 商品
        if pid in subs:
            sid = subs[pid][0]
            print(f"商品は、すでにあります: {pid}（中身は変えません）")
            continue
        res = must(*call("POST", "/subscriptions", {"data": {"type": "subscriptions",
            "attributes": {"name": name, "productId": pid, "subscriptionPeriod": period,
                           "familySharable": False, "groupLevel": 1},
            "relationships": {"group": {"data": {"type": "subscriptionGroups", "id": gid}}}}}), f"商品の作成 {pid}")
        sid = res["data"]["id"]
        print(f"商品を作りました: {pid}")
        # 3. 日本語の表示名・説明
        must(*call("POST", "/subscriptionLocalizations", {"data": {"type": "subscriptionLocalizations",
            "attributes": {"name": title, "description": desc, "locale": "ja"},
            "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}}}}}), f"表示名 {pid}")
        # 4. 販売地域：日本
        must(*call("POST", "/subscriptionAvailabilities", {"data": {"type": "subscriptionAvailabilities",
            "attributes": {"availableInNewTerritories": False},
            "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}},
                              "availableTerritories": {"data": [{"type": "territories", "id": TERRITORY}]}}}}), f"販売地域 {pid}")
        # 5. 価格（日本）
        pp = price_point(sid, yen)
        if not pp:
            print(f"::error::日本の {yen} 円の価格が見つかりません（{pid}）。商品は作成済みです。"); sys.exit(1)
        must(*call("POST", "/subscriptionPrices", {"data": {"type": "subscriptionPrices",
            "attributes": {"preserveCurrentPrice": False},
            "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}},
                              "subscriptionPricePoint": {"data": {"type": "subscriptionPricePoints", "id": pp}},
                              "territory": {"data": {"type": "territories", "id": TERRITORY}}}}}), f"価格 {pid}")
        print(f"価格を設定しました: {yen} 円")
        # 6. 7日間の無料トライアル
        must(*call("POST", "/subscriptionIntroductoryOffers", {"data": {"type": "subscriptionIntroductoryOffers",
            "attributes": {"duration": "ONE_WEEK", "offerMode": "FREE_TRIAL", "numberOfPeriods": 1},
            "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}},
                              "territory": {"data": {"type": "territories", "id": TERRITORY}}}}}), f"無料トライアル {pid}")
        print("無料トライアル（7日間）を付けました")
    print("完了しました。審査用のスクリーンショットは、まだ入っていません。")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"check": check, "create": create}[mode]()
