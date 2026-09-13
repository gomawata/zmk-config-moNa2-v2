# 検証

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
git diff --check
```

原本fixtureは不変とし、`config/mona2.keymap` にはテストで明示した許容差分だけを適用する。
このチェックはソース構成を検証するもので、ZMKをコンパイルしない。
Use `.github/workflows/build.yml` on the target branch for firmware build verification.
Hardware checks require the matching physical keyboard and sensor.
