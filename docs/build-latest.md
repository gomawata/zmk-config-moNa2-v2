# 2026-09-13 の再現ビルド

この構成は、2026-09-13 時点で取得した cormoran の DYA 向け開発系を固定する。
これは公式の安定版リリース名ではない。直接依存23件は同日時点の対応ブランチHEADを
完全SHAへ置換済みで、`config/west.lock.yml` は ZMK の import を含むアクティブな
実ビルド依存78件を `west manifest --freeze --active-only` で記録したものになる。
`babblesim` グループはこのnRF52840ファームウェアに不要なため、lock対象外である。

## 固定された基盤

- ZMK: `cormoran/zmk` `main+dya` → `e5c9b6915b56801193e359dd9bad4a167ce0d1b8`
- Zephyr: ZMK import → `10ba6d0cb38bc3d258775d27982f707599320085` (4.1.0)
- SDK: Zephyr SDK 0.17.0、`arm-zephyr-eabi` のみ
- ホスト: macOS arm64、Python 3.12.14、west 1.5.0、CMake 3.31.10、Ninja 1.13.2、
  arm-zephyr-eabi-gcc 12.2.0

Zephyr 4.1の `FindZephyr-sdk.cmake` は CMake 4.4で構文非互換を起こしたため、CMakeは
3系を使う。SDKの公式`setup.sh`はmacOSでも`wget`を検査する。SDK自体はworkspace内へ
入れ、`wget`がなければ同等のローカルラッパーをPATHに置くか、別途導入する。
`west sdk install` はCMake package registryへSDKを1件登録するが、以下のビルドは
`ZEPHYR_SDK_INSTALL_DIR`と`Zephyr_DIR`を明示し、その登録には依存しない。

## 新規workspaceの作成

既存workspaceの`.west`を使わず、設定repoを子ディレクトリにcloneしてから初期化する。

```zsh
WORKSPACE=/absolute/path/mona2-mac-latest-build
PYTHON=/absolute/path/to/python3
git clone /absolute/path/to/zmk-config-moNa2-mac-20260913 "$WORKSPACE/config"
"$PYTHON" -m venv "$WORKSPACE/.venv"
"$WORKSPACE/.venv/bin/pip" install --upgrade pip west 'cmake>=3.20,<4' ninja
"$WORKSPACE/.venv/bin/west" init -l --mf config/west.yml "$WORKSPACE/config"
cd "$WORKSPACE"
PATH="$WORKSPACE/.venv/bin:$PATH" "$WORKSPACE/.venv/bin/west" update --stats
PATH="$WORKSPACE/.venv/bin:$PATH" "$WORKSPACE/.venv/bin/west" packages pip --install
PATH="$WORKSPACE/.venv/bin:$PATH" "$WORKSPACE/.venv/bin/west" sdk install \
  --version 0.17.0 --install-dir "$WORKSPACE/sdk" --toolchains arm-zephyr-eabi
```

依存解決後は次で、checkoutの解決状態がcommitted lockと一致することを確認できる。

```zsh
PATH="$WORKSPACE/.venv/bin:$PATH" "$WORKSPACE/.venv/bin/west" \
  manifest --freeze --active-only
```

## ビルド共通環境

`SOURCE`は最終配布前にcommit済みの設定repoを指す。各targetは別build directoryを使う。

```zsh
SOURCE=/absolute/path/to/zmk-config-moNa2-mac-20260913
export PATH="$WORKSPACE/.venv/bin:$PATH"
export ZEPHYR_TOOLCHAIN_VARIANT=zephyr
export ZEPHYR_SDK_INSTALL_DIR="$WORKSPACE/sdk"
COMMON=(
  "-DZephyr_DIR=$WORKSPACE/zephyr/share/zephyr-package/cmake"
  "-DZMK_CONFIG=$SOURCE/config"
  "-DZMK_EXTRA_MODULES=$SOURCE"
)
```

```zsh
cd "$WORKSPACE/zmk"
west build -s app -d build/mona2_l -p always -b xiao_ble/nrf52840/zmk -- \
  "${COMMON[@]}" -DSHIELD='mona2_l rgbled_adapter'
west build -s app -d build/mona2_r-coropit -p always -b xiao_ble/nrf52840/zmk -- \
  "${COMMON[@]}" -DSHIELD='mona2_r rgbled_adapter' -DSNIPPET=studio-rpc-usb-uart \
  -DEXTRA_CONF_FILE="$SOURCE/config/coropit.conf" \
  -DEXTRA_DTC_OVERLAY_FILE="$SOURCE/config/coropit.overlay"
west build -s app -d build/settings_reset -p always -b xiao_ble/nrf52840/zmk -- \
  "${COMMON[@]}" -DSHIELD=settings_reset
```

成功時のUF2、SHA-256、サイズ、メモリ使用量、生成元commitは最終ビルド時にこの文書へ
追記する。実機への書込みはこの手順に含めない。
