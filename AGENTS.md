# 検証

旧 Mac 配列を変更するときは、原本fixtureとの一致とv2ハードウェア設定を確認するため、次を実行する。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
git diff --check
```

`config/mona2.keymap` は `tests/fixtures/old-main.keymap` とバイト単位で一致する復元対象である。意図的なZMK互換名の正規化が必要になった場合は、原本のSHA-256、変更理由、置換前後を `docs/original-mac-layout.md` に記載し、テストもその例外を明示する。
