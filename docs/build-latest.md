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

## 最終ビルド結果

生成元は `99b7222279c13c7d27b6c964a629c5d3a9456ebd`。3件とも
`xiao_ble/nrf52840/zmk` で `-p always` を使って別ディレクトリへクリーンビルドした。
全UF2は Nordic NRF52840 family ID `0xADA52840`、開始アドレス `0x27000`、payload 256 bytes
である。

| Target | UF2 relative to workspace `zmk/` | SHA-256 | Size | FLASH | RAM |
| --- | --- | --- | ---: | ---: | ---: |
| LEFT `mona2_l rgbled_adapter` | `build/final-99b722-mona2_l/zephyr/zmk.uf2` | `f20d798fc60255dd21ad1ce37745e09ec3f0a8677189d3d0289f636e7d2c1578` | 438272 B | 218980 / 788 KB (27.14%) | 65700 / 256 KB (25.06%) |
| RIGHT COROPIT `mona2_r rgbled_adapter`, `studio-rpc-usb-uart`, `coropit.conf`, `coropit.overlay` | `build/final-99b722-mona2_r-coropit/zephyr/zmk.uf2` | `19168415231786809aa258c518810f35676df7b90b7a6e9a93c01e45dfd6dffb` | 784384 B | 392020 / 788 KB (48.58%) | 150840 / 256 KB (57.54%) |
| `settings_reset` | `build/final-99b722-settings_reset/zephyr/zmk.uf2` | `5836a10e7337fb83f0df22c2ad19a675b9b8a5410224fee5813fb6dc7e6fefce` | 118272 B | 59012 / 788 KB (7.31%) | 17456 / 256 KB (6.66%) |

RIGHTの生成済みKconfig/DTSで `CONFIG_PMW3610_INVERT_X=y`、
`CONFIG_PMW3610_INVERT_Y=n`、`CONFIG_PMW3610_SWAP_XY=n`、および
`cormoran,pmw3610` の `cpi = <3200>` を確認した。LEFT/RIGHTの生成keymapは
`Maclayer`、`layer_1`、`layer_3`、`layer_4` の42 bindingずつ、計4レイヤーである。

## CPI 1600への変更

上記の`99b722`のCPI 3200ビルド結果は履歴として保持する。現在のCOROPIT初期値は
`config/coropit.overlay`でCPI 1600へ変更した。X反転=`y`、Y反転=`n`、XY入替=`n`、
4レイヤーMac keymap、固定manifestは変更しない。CPI 1600の右側COROPIT再現ビルド結果は
build workspaceの専用レポートに記録する。
