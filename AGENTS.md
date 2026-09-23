# 検証

## 領域の参照

作業開始時に [領域AGENTS.md](/Users/koma/Products/AGENTS.md) と [参照案内](/Users/koma/Products/sources.md) を明示して読み、この案件の指示と併用する。領域の親指示が自動で読み込まれたと仮定しない。
この案件はArchiveで保管している。通常の現役検索からは外し、過去参照または明示依頼で扱う。旧文書を現行の実行指示として無条件に採用しない。


旧 Mac 配列を変更するときは、原本fixtureとの一致とv2ハードウェア設定を確認するため、次を実行する。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
git diff --check
```

`config/mona2.keymap` は `tests/fixtures/old-main.keymap` とバイト単位で一致する復元対象である。意図的なZMK互換名の正規化が必要になった場合は、原本のSHA-256、変更理由、置換前後を `docs/original-mac-layout.md` に記載し、テストもその例外を明示する。
