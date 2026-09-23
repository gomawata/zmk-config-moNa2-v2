# 検証

## 領域の参照

作業開始時に [領域AGENTS.md](/Users/koma/Products/AGENTS.md) と [参照案内](/Users/koma/Products/sources.md) を明示して読み、この案件の指示と併用する。領域の親指示が自動で読み込まれたと仮定しない。


```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
git diff --check
```

原本fixtureは不変とし、`config/mona2.keymap` にはテストで明示した許容差分だけを適用する。
このチェックはソース構成を検証するもので、ZMKをコンパイルしない。
Use `.github/workflows/build.yml` on the target branch for firmware build verification.
Hardware checks require the matching physical keyboard and sensor.
