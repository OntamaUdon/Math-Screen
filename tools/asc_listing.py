"""App Store Connect に、掲載情報（説明・キーワード・サポートURL など）とスクリーンショットを入れる。

  python tools/asc_listing.py listing  … store/LISTING_DRAFT.md の内容を、バージョン 1.0 に入れる（なければ作る）
  python tools/asc_listing.py shots    … store/screenshots の5枚を、6.9インチ用として入れる（すでにあれば入れ替える）
  python tools/asc_listing.py check    … 読むだけ

審査には出さない。審査担当者への連絡先（氏名・電話番号など）は、個人情報なので入れない（本人が入力する）。
環境変数: KEY_PATH（.p8 のパス）, ASC_KEY_ID, ASC_ISSUER_ID
"""
import hashlib, os, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ci_signing import call, must
from asc_subscriptions import find_app, get_all, put_bytes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = "1.0"
SHOTS = ["solve", "home", "book", "stats", "plan"]       # 見せる順番


def sections():
    """LISTING_DRAFT.md を、「## 見出し」ごとに分ける。見出しの（…）の部分は無視する。"""
    text = open(os.path.join(ROOT, "store", "LISTING_DRAFT.md"), encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.S | re.M):
        key = re.sub(r"（.*?）", "", m.group(1)).strip()
        body = "\n".join(l for l in m.group(2).splitlines() if not l.startswith(">"))   # 「> 」で始まる行は、メモなので入れない
        out[key] = body.strip()
    return out


def version_id(app_id, create=False):
    vs = get_all(f"/apps/{app_id}/appStoreVersions?filter[platform]=IOS&limit=50")
    for v in vs:
        if v["attributes"]["versionString"] == VERSION:
            return v["id"], v["attributes"]["appStoreState"]
    if not create:
        return None, None
    res = must(*call("POST", "/appStoreVersions", {"data": {"type": "appStoreVersions",
        "attributes": {"platform": "IOS", "versionString": VERSION},
        "relationships": {"app": {"data": {"type": "apps", "id": app_id}}}}}), "バージョンの作成")
    print(f"バージョン {VERSION} を作りました")
    return res["data"]["id"], res["data"]["attributes"]["appStoreState"]


def primary_locale(app_id):
    st, res = call("GET", f"/apps/{app_id}")
    must(st, res, "アプリの情報")
    return res["data"]["attributes"].get("primaryLocale") or "ja"


def listing():
    sec = sections()
    app_id = find_app()
    loc_name = primary_locale(app_id)
    vid, state = version_id(app_id, create=True)
    print("バージョンの状態:", state)
    # バージョンの文：著作権
    must(*call("PATCH", f"/appStoreVersions/{vid}", {"data": {"type": "appStoreVersions", "id": vid,
        "attributes": {"copyright": sec["著作権表示"]}}}), "著作権")
    # 説明・キーワード・サポートURL
    locs = get_all(f"/appStoreVersions/{vid}/appStoreVersionLocalizations")
    loc = next((l for l in locs if l["attributes"]["locale"] == loc_name), None)
    attrs = {"description": sec["説明"], "keywords": sec["キーワード"].replace("\n", ""), "promotionalText": sec["プロモーション用テキスト"],
             "supportUrl": sec["サポートURL"], "marketingUrl": sec["サポートURL"]}
    if loc:
        must(*call("PATCH", f"/appStoreVersionLocalizations/{loc['id']}", {"data": {"type": "appStoreVersionLocalizations", "id": loc["id"],
            "attributes": attrs}}), "説明など")
    else:
        must(*call("POST", "/appStoreVersionLocalizations", {"data": {"type": "appStoreVersionLocalizations",
            "attributes": dict(attrs, locale=loc_name),
            "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": vid}}}}}), "説明などの作成")
    print("説明・キーワード・プロモーション用テキスト・サポートURL・著作権を入れました")
    # アプリ情報：サブタイトル・プライバシーポリシーのURL・カテゴリ
    infos = get_all(f"/apps/{app_id}/appInfos")
    info = infos[0]
    il = get_all(f"/appInfos/{info['id']}/appInfoLocalizations")
    cur = next((l for l in il if l["attributes"]["locale"] == loc_name), None)
    ia = {"subtitle": sec["サブタイトル"], "privacyPolicyUrl": sec["プライバシーポリシーのURL"]}
    if cur:
        must(*call("PATCH", f"/appInfoLocalizations/{cur['id']}", {"data": {"type": "appInfoLocalizations", "id": cur["id"],
            "attributes": ia}}), "サブタイトル")
    else:
        must(*call("POST", "/appInfoLocalizations", {"data": {"type": "appInfoLocalizations",
            "attributes": dict(ia, locale=loc_name, name=sec["アプリ名"]),
            "relationships": {"appInfo": {"data": {"type": "appInfos", "id": info["id"]}}}}}), "サブタイトルの作成")
    must(*call("PATCH", f"/appInfos/{info['id']}", {"data": {"type": "appInfos", "id": info["id"], "relationships": {
        "primaryCategory": {"data": {"type": "appCategories", "id": "EDUCATION"}},
        "secondaryCategory": {"data": {"type": "appCategories", "id": "LIFESTYLE"}}}}}), "カテゴリ")
    print("サブタイトル・プライバシーポリシーのURL・カテゴリを入れました")
    # 審査メモ（連絡先は入れない）
    st, res = call("GET", f"/appStoreVersions/{vid}/appStoreReviewDetail")
    note = sec["審査担当者へのメモ（アプリの審査用）"] if "審査担当者へのメモ（アプリの審査用）" in sec else sec["審査担当者へのメモ"]
    detail = res.get("data") if st == 200 else None
    if detail:
        must(*call("PATCH", f"/appStoreReviewDetails/{detail['id']}", {"data": {"type": "appStoreReviewDetails", "id": detail["id"],
            "attributes": {"notes": note, "demoAccountRequired": False}}}), "審査メモ")
    else:
        must(*call("POST", "/appStoreReviewDetails", {"data": {"type": "appStoreReviewDetails",
            "attributes": {"notes": note, "demoAccountRequired": False},
            "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": vid}}}}}), "審査メモの作成")
    print("審査メモを入れました（連絡先の氏名・電話番号は、入れていません）")


def shots():
    app_id = find_app()
    loc_name = primary_locale(app_id)
    vid, _ = version_id(app_id, create=False)
    if not vid:
        print("::error::バージョンがありません。先に listing を実行してください"); sys.exit(1)
    locs = get_all(f"/appStoreVersions/{vid}/appStoreVersionLocalizations")
    loc = next((l for l in locs if l["attributes"]["locale"] == loc_name), None)
    if not loc:
        print("::error::言語の情報がありません。先に listing を実行してください"); sys.exit(1)
    sets = get_all(f"/appStoreVersionLocalizations/{loc['id']}/appScreenshotSets")
    s = next((x for x in sets if x["attributes"]["screenshotDisplayType"] == "APP_IPHONE_69"), None)
    if not s:
        s = must(*call("POST", "/appScreenshotSets", {"data": {"type": "appScreenshotSets",
            "attributes": {"screenshotDisplayType": "APP_IPHONE_69"},
            "relationships": {"appStoreVersionLocalization": {"data": {"type": "appStoreVersionLocalizations", "id": loc["id"]}}}}}), "画像のセット")["data"]
    for old in get_all(f"/appScreenshotSets/{s['id']}/appScreenshots"):
        must(*call("DELETE", f"/appScreenshots/{old['id']}"), "古い画像の削除")
    for name in SHOTS:
        data = open(os.path.join(ROOT, "store", "screenshots", f"{name}.png"), "rb").read()
        shot = must(*call("POST", "/appScreenshots", {"data": {"type": "appScreenshots",
            "attributes": {"fileName": f"{name}.png", "fileSize": len(data)},
            "relationships": {"appScreenshotSet": {"data": {"type": "appScreenshotSets", "id": s["id"]}}}}}), f"画像の予約 {name}")["data"]
        for op in shot["attributes"]["uploadOperations"]:
            put_bytes(op, data)
        must(*call("PATCH", f"/appScreenshots/{shot['id']}", {"data": {"type": "appScreenshots", "id": shot["id"],
            "attributes": {"uploaded": True, "sourceFileChecksum": hashlib.md5(data).hexdigest()}}}), f"画像の確定 {name}")
        print(f"入れました: {name}.png")


def check():
    app_id = find_app()
    vid, state = version_id(app_id)
    print("バージョン", VERSION, ":", vid or "まだありません", state or "")
    if not vid:
        return
    for l in get_all(f"/appStoreVersions/{vid}/appStoreVersionLocalizations"):
        a = l["attributes"]
        print(" ", a["locale"], "説明", len(a.get("description") or ""), "字 / キーワード", len(a.get("keywords") or ""), "字 / サポートURL", a.get("supportUrl"))
        for s in get_all(f"/appStoreVersionLocalizations/{l['id']}/appScreenshotSets"):
            n = len(get_all(f"/appScreenshotSets/{s['id']}/appScreenshots"))
            print("   ", s["attributes"]["screenshotDisplayType"], n, "枚")


if __name__ == "__main__":
    {"listing": listing, "shots": shots, "check": check}[sys.argv[1] if len(sys.argv) > 1 else "check"]()
