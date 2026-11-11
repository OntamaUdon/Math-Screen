"""端末の登録なしで TestFlight 用に署名するための、一時的な証明書とプロファイルの作成・削除。

App Store Connect API（Admin の API キー）を使う。
  python tools/ci_signing.py setup    … 配布用の証明書を1つ作り、4つの Bundle ID の App Store 用プロファイルを作ってインストール
  python tools/ci_signing.py cleanup  … このとき作った証明書とプロファイルを削除（ビルドが失敗しても必ず実行する）
環境変数: KEY_PATH（.p8 のパス）, ASC_KEY_ID, ASC_ISSUER_ID, RUNNER_TEMP
作った ID は $RUNNER_TEMP/ci_signing.json に記録し、削除はその ID だけを対象にする。
"""
import base64, json, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
import jwt  # PyJWT

API = "https://api.appstoreconnect.apple.com/v1"
TEMP = os.environ.get("RUNNER_TEMP", "/tmp")
STATE = os.path.join(TEMP, "ci_signing.json")
KEYCHAIN = os.path.join(TEMP, "ci-signing.keychain-db")
KEYCHAIN_PW = "ci-signing-pw"
OPENSSL = "/usr/bin/openssl"            # macOS 標準（LibreSSL）。p12 が macOS の security で読める形式になる
BUNDLES = {                             # Bundle ID: project.yml の PROVISIONING_PROFILE_SPECIFIER と同じ名前
    "com.ontamaudon.qlock": "QLockCI app",
    "com.ontamaudon.qlock.monitor": "QLockCI monitor",
    "com.ontamaudon.qlock.shieldconfig": "QLockCI shieldconfig",
    "com.ontamaudon.qlock.shieldaction": "QLockCI shieldaction",
}


def token():
    now = int(time.time())
    key = open(os.environ["KEY_PATH"]).read()
    return jwt.encode({"iss": os.environ["ASC_ISSUER_ID"], "iat": now, "exp": now + 900, "aud": "appstoreconnect-v1"},
                      key, algorithm="ES256", headers={"kid": os.environ["ASC_KEY_ID"]})


def call(method, path, body=None):
    url = path if path.startswith("http") else API + path
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read()
        return e.code, (json.loads(raw) if raw else {})


def must(status, res, what, ok=(200, 201, 204)):
    if status not in ok:
        print(f"::error::{what} に失敗しました（{status}）: {json.dumps(res, ensure_ascii=False)[:800]}")
        sys.exit(1)
    return res


def sh(*args, **kw):
    return subprocess.run(args, check=True, **kw)


def setup():
    state = {"certificate": None, "profiles": []}
    save = lambda: json.dump(state, open(STATE, "w"))

    # 前回の失敗で残った同名のプロファイルがあれば消す（名前が重複すると作れないため）
    for name in BUNDLES.values():
        st, res = call("GET", "/profiles?" + urllib.parse.urlencode({"filter[name]": name, "limit": 50}))
        if st == 200:
            for p in res.get("data", []):
                if p["attributes"]["name"] == name:
                    call("DELETE", f"/profiles/{p['id']}")

    # 前回までの CI 用の証明書を片づける（配布用の証明書は数に上限があり、残っていると新しく作れない）。
    # 注意：審査に出したビルドの証明書を、審査が終わる前に消すと、署名が無効と判断されることがある。
    #       審査中は、新しいビルドを作らないこと。公開済みのアプリは Apple が署名し直すので、消しても影響しない。
    st, res = call("GET", "/certificates?" + urllib.parse.urlencode({"filter[certificateType]": "IOS_DISTRIBUTION", "limit": 50}))
    if st == 200:
        mine = []
        for c in res.get("data", []):
            try:
                der = base64.b64decode(c["attributes"]["certificateContent"])
                out = subprocess.run([OPENSSL, "x509", "-inform", "der", "-noout", "-subject", "-enddate"],
                                     input=der, capture_output=True, check=True).stdout.decode()
            except Exception:
                continue
            if "QLock CI" in out:
                mine.append((c["id"], c["attributes"].get("expirationDate") or "", out))
        mine.sort(key=lambda x: x[1])
        for cid, _, _ in mine:
            st2, _ = call("DELETE", f"/certificates/{cid}")
            print("古い CI 用の証明書を削除:", cid, st2)

    # 1. 鍵と CSR
    key, csr = os.path.join(TEMP, "ci.key"), os.path.join(TEMP, "ci.csr")
    sh(OPENSSL, "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", key, "-out", csr,
       "-subj", "/CN=QLock CI/O=QLock/C=JP")

    # 2. 配布用の証明書
    res = must(*call("POST", "/certificates", {"data": {"type": "certificates", "attributes": {
        "certificateType": "IOS_DISTRIBUTION", "csrContent": open(csr).read()}}}), "配布用証明書の作成")
    cert_id = res["data"]["id"]
    state["certificate"] = cert_id; save()
    cer = os.path.join(TEMP, "ci.cer"); pem = os.path.join(TEMP, "ci.pem"); p12 = os.path.join(TEMP, "ci.p12")
    open(cer, "wb").write(base64.b64decode(res["data"]["attributes"]["certificateContent"]))
    sh(OPENSSL, "x509", "-inform", "der", "-in", cer, "-out", pem)
    sh(OPENSSL, "pkcs12", "-export", "-inkey", key, "-in", pem, "-out", p12, "-passout", f"pass:{KEYCHAIN_PW}")

    # 3. 一時キーチェーンに取り込む
    sh("security", "create-keychain", "-p", KEYCHAIN_PW, KEYCHAIN)
    sh("security", "set-keychain-settings", "-lut", "21600", KEYCHAIN)
    sh("security", "unlock-keychain", "-p", KEYCHAIN_PW, KEYCHAIN)
    sh("security", "import", p12, "-k", KEYCHAIN, "-P", KEYCHAIN_PW, "-T", "/usr/bin/codesign", "-T", "/usr/bin/security")
    sh("security", "set-key-partition-list", "-S", "apple-tool:,apple:", "-s", "-k", KEYCHAIN_PW, KEYCHAIN,
       stdout=subprocess.DEVNULL)
    sh("security", "list-keychains", "-d", "user", "-s", KEYCHAIN, os.path.expanduser("~/Library/Keychains/login.keychain-db"))

    # 4. Bundle ID ごとに App Store 用プロファイル
    pdir = os.path.expanduser("~/Library/MobileDevice/Provisioning Profiles")
    os.makedirs(pdir, exist_ok=True)
    for bundle, name in BUNDLES.items():
        st, res = call("GET", "/bundleIds?" + urllib.parse.urlencode({"filter[identifier]": bundle, "limit": 50}))
        must(st, res, f"Bundle ID {bundle} の検索")
        found = [b for b in res["data"] if b["attributes"]["identifier"] == bundle]
        if not found:
            print(f"::error::Bundle ID {bundle} が Apple Developer に登録されていません。docs/SETUP.md の 1. を確認してください。")
            sys.exit(1)
        res = must(*call("POST", "/profiles", {"data": {
            "type": "profiles",
            "attributes": {"name": name, "profileType": "IOS_APP_STORE"},
            "relationships": {
                "bundleId": {"data": {"type": "bundleIds", "id": found[0]["id"]}},
                "certificates": {"data": [{"type": "certificates", "id": cert_id}]}}}}),
            f"プロファイル {name} の作成")
        state["profiles"].append(res["data"]["id"]); save()
        uuid = res["data"]["attributes"]["uuid"]
        open(os.path.join(pdir, f"{uuid}.mobileprovision"), "wb").write(
            base64.b64decode(res["data"]["attributes"]["profileContent"]))
        print(f"プロファイルを作成: {name} ({bundle})")
    print("署名の準備ができました。")


def cleanup():
    if not os.path.exists(STATE):
        print("片づけるものはありません。"); return
    state = json.load(open(STATE))
    for pid in state.get("profiles", []):
        st, _ = call("DELETE", f"/profiles/{pid}")
        print("プロファイル削除:", pid, st)
    # 証明書は消さない。審査の提出のときに、署名が有効である必要があるため。
    # 古いものは、次のビルドの setup が片づける。
    if state.get("certificate"):
        print("証明書は残します:", state["certificate"])
    subprocess.run(["security", "delete-keychain", KEYCHAIN], check=False)


if __name__ == "__main__":
    {"setup": setup, "cleanup": cleanup}[sys.argv[1]]()
