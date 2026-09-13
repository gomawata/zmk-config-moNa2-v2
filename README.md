# moNa2 v2 — Mac / COROPIT

moNa2 v2 をMac専用で使うためのZMK設定です。右側（Central）用のCOROPIT成果物は`mona2_r-coropit`、左側（Peripheral）用は`mona2_l`です。どちらも`xiao_ble/nrf52840/zmk`を対象にし、右側には`studio-rpc-usb-uart`を含みます。

## 配列

`config/mona2.keymap`は旧Mac配列を4レイヤーで維持し、原本との差分を[配列と許容差分](docs/mac-keymap.md)で明示しています。

| 実レイヤー | ノード | 内容 | 到達方法 |
| --- | --- | --- | --- |
| 0 | `Maclayer` | 通常入力、右側の常設クリック、Backspace、Enter | 起動時 |
| 1 | `layer_1` | 数字・記号 | かな（位置38）を長押し |
| 2 | `layer_3` | 編集補助、矢印、Macショートカット | Space（位置37）またはEnter（位置40）を長押し |
| 3 | `layer_4` | BLE、消去、bootloader | `/`（位置26）を長押し |

`F13`（位置35）は維持しています。`AUTO_MOUSE`、Windows配列、OS別デフォルトレイヤーはありません。

## Mac側の設定

- AquaVoiceに`F13`を追加する。既存のFn設定は維持する。
- CleanShot OCR: `Control + Option + Command + T`
- Raycast Clipboard History: `Control + Option + Command + B`
- macOSの「Appショートカット」で、次を設定する。

| メニュー操作 | ショートカット |
| --- | --- |
| ウインドウ → 移動とサイズ変更 → 左 | `Control + Option + Command + Left` |
| ウインドウ → 画面全体に表示 | `Control + Option + Command + F` |
| ウインドウ → 移動とサイズ変更 → 右 | `Control + Option + Command + Right` |
| ウインドウ → 中央に配置 | `Control + Option + Command + C` |
| ウインドウ → 移動とサイズ変更 → 前のサイズに戻す | `Control + Option + Command + R` |

標準のWindowメニューに対応しないアプリでは、これらのAppショートカットが動くか確認してください。Magnetは使いません。通常層の`Control + Shift + 4`と編集補助層の`Command + Control + V`は、現在のMac設定に合わせています。

## COROPITとDYA Studio

COROPITはCPI 3200、X反転有効、Y反転無効、XY入替無効です。DYA Studioに保存済みの値があればそちらが優先されるため、右側をUSB接続して値を確認し、必要なら上書きしてください。設定を保存したら少なくとも10秒は電源を維持します。

通常は左右それぞれに対応するUF2を書き込むだけで更新します。[ZMK Settings](https://zmk.dev/docs/config/settings)のとおり、UF2更新ではpersistent settingsは残ります。過去にStudioでキーマップを保存した場合は、右側をUSB接続して[ZMK StudioのRestore Stock Settings](https://zmk.dev/docs/features/studio)を実行し、コンパイル済み配列を有効にしてください。これでPMW3610のカスタム設定まで消えるかは未確認です。

キーマップを保存していなくても、Runtime Input Processorのマウス設定は残ることがあります。更新後、使い始める前にDYA Studioでmouseの一時レイヤーと`xy-to-scroll`が無効であることを確認し、必要なら無効にして保存してください。レイヤー指定など、4レイヤー配列に干渉する保存済み設定も確認します。Restore Stock Settingsだけでは実行中のRuntime Input Processor設定が設定変更イベントで再適用されないため、保存または復旧の後は右側を再起動して、同じ項目をもう一度確認します。

左右が接続できないなど必要な場合だけ、両側に`settings_reset`を書き込み、続けて各側へ通常UF2を書き込みます。その場合はMac側の旧Bluetooth登録を忘れて再ペアリングします。詳しくは[ZMKの接続トラブルシューティング](https://zmk.dev/docs/troubleshooting/connection-issues)を参照してください。旧0.3系のCustom Settingsからの移行は実機未検証です。

## 検証

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
git diff --check
```

これはソース選択・キーマップ差分の検証です。ZMKのコンパイルと実機確認は別途必要です。
