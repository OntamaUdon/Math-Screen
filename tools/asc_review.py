"""App Store の審査の提出物を、読む／再提出する。

  python tools/asc_review.py status    … 読むだけ：提出物の状態、中身の項目、バージョンに付いているビルド、最新のビルド
  python tools/asc_review.py resubmit  … バージョン 1.0 に、処理が終わった最新のビルドを付けて、審査に再提出する

環境変数: KEY_PATH（.p8 のパス）, ASC_KEY_ID, ASC_ISSUER_ID
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ci_signing import call, must
from asc_subscriptions import find_app, get_all

VERSION = "1.0"


def version(app_id):
    for v in get_all(f"/apps/{app_id}/appStoreVersions?filter[platform]=IOS&limit=50"):
        if v["attributes"]["versionString"] == VERSION:
            return v
    return None


def attached_build(vid):
    st, res = call("GET", f"/appStoreVersions/{vid}/build")
    d = res.get("data") if st == 200 else None
    return d["attributes"]["version"] if d else None


def latest_valid_build(app_id):
    bs = get_all(f"/builds?filter[app]={app_id}&filter[preReleaseVersion.version]={VERSION}&limit=50")
    bs = [b for b in bs if b["attributes"].get("processingState") == "VALID" and not b["attributes"].get("expired")]
    bs.sort(key=lambda b: int(b["attributes"]["version"]))
    return bs[-1] if bs else None


def submissions(app_id):
    return get_all(f"/apps/{app_id}/reviewSubmissions?filter[platform]=IOS&limit=20")


def status():
    app_id = find_app()
    v = version(app_id)
    if not v:
        print("バージョンがありません"); return
    print(f"バージョン {VERSION}: {v['attributes']['appStoreState']} / 付いているビルド: {attached_build(v['id'])}")
    b = latest_valid_build(app_id)
    print("処理が終わった最新のビルド:", b["attributes"]["version"] if b else "なし")
    for s in submissions(app_id):
        a = s["attributes"]
        print(f"提出物 {s['id']}: {a.get('state')} / 提出日時 {a.get('submittedDate')}")
        for it in get_all(f"/reviewSubmissions/{s['id']}/items"):
            kind = next((k for k, r in (it.get("relationships") or {}).items() if (r.get("data") if isinstance(r, dict) else None)), "")
            print("   項目:", it["attributes"].get("state"), kind)


def resubmit():
    app_id = find_app()
    v = version(app_id)
    if not v:
        print("::error::バージョンがありません"); sys.exit(1)
    b = latest_valid_build(app_id)
    if not b:
        print("::error::処理が終わったビルドがありません（TestFlight の処理を待ってください）"); sys.exit(1)
    cur = attached_build(v["id"])
    if cur != b["attributes"]["version"]:
        must(*call("PATCH", f"/appStoreVersions/{v['id']}/relationships/build", {"data": {"type": "builds", "id": b["id"]}}),
             f"ビルド {b['attributes']['version']} を付ける")
        print(f"ビルドを {cur} から {b['attributes']['version']} に付けかえました")
    else:
        print(f"ビルド {cur} は、すでに付いています")
    subs = submissions(app_id)
    target = next((s for s in subs if s["attributes"].get("state") in ("UNRESOLVED_ISSUES", "READY_FOR_REVIEW")), None)
    if not target:
        print("::error::再提出できる提出物が見つかりません。状態:", [s["attributes"].get("state") for s in subs]); sys.exit(1)
    print("再提出する提出物:", target["id"], target["attributes"].get("state"))
    must(*call("PATCH", f"/reviewSubmissions/{target['id']}", {"data": {"type": "reviewSubmissions", "id": target["id"],
        "attributes": {"submitted": True}}}), "審査への再提出")
    print("審査に再提出しました")
    status()


if __name__ == "__main__":
    {"status": status, "resubmit": resubmit}[sys.argv[1] if len(sys.argv) > 1 else "status"]()
