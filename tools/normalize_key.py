"""API キー(.p8)を、Apple のツールが確実に読める形（PKCS#8 の PEM、LF 改行、末尾に改行）に書き直す。

GitHub の Secret に貼り付けると改行の形式が変わることがあるため。中身（秘密）は表示しない。
環境変数: KEY_PATH
"""
import os, sys
from cryptography.hazmat.primitives import serialization

path = os.environ["KEY_PATH"]
raw = open(path, "rb").read()
print(f"キーのファイル: {len(raw)} バイト / CR={raw.count(b'\\r')} / LF={raw.count(b'\\n')} / "
      f"末尾が改行={raw.endswith(b'\\n')} / 先頭行={raw.splitlines()[0].decode(errors='replace') if raw else ''}")
try:
    key = serialization.load_pem_private_key(raw.strip(), password=None)
except Exception as e:
    print(f"::error::キーを読めませんでした: {type(e).__name__}"); sys.exit(1)
pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
open(path, "wb").write(pem)
print(f"書き直しました: {len(pem)} バイト / 末尾が改行={pem.endswith(b'\\n')}")
