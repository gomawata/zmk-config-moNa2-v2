# 旧 Mac 配列の復元

`config/mona2.keymap` は、旧リポジトリ
[`gomawata/zmk-config-moNa2` の commit `8f7ceba8837831829b1525e3aee5c5124ca4d3c1` にある
`config/moNa2.keymap`](https://github.com/gomawata/zmk-config-moNa2/blob/8f7ceba8837831829b1525e3aee5c5124ca4d3c1/config/moNa2.keymap)
から取得した原本（SHA-256:
`adfcddcf616d63021b3a818f0aad10ebeb40b1a86a2926e1ad8f23588dd85348`）をバイト単位で復元しています。
ZMK 0.3 向けのキー名置換や配列の再設計はしていません。

この4月の原本コミットのGitHub Actionsは失敗しており、過去に実機へ書き込んだ設定だったことまでは証明できません。
2月の成功ビルド版にも右側のBackspace／Enter／常設クリックという骨格は同じです。

物理位置は `boards/shields/mona2/mona2.dtsi` の42キーの変換順です。主な右側の位置は、
30 が `MB1`、31 が `MB2`、39 が `Backspace`、40 がタップ `Enter`／ホールドで実レイヤー2です。

| 実レイヤー番号 | keymap ノード | 内容 | 到達方法 |
| --- | --- | --- | --- |
| 0 | `Maclayer` | Macの通常入力。右にBackspace、Enter、MB1、MB2 | 起動時 |
| 1 | `layer_1` | 数字・記号 | 位置38をホールド（タップは`LANGUAGE_1`） |
| 2 | `layer_3` | 矢印・編集・記号 | 位置37/40をホールド（それぞれタップは`SPACE`／`ENTER`） |
| 3 | `layer_4` | Bluetoothプロファイル、消去、bootloader | 位置26をホールド（タップは`SLASH`） |

実レイヤー2では、通常配列の`J`／`K`位置がそれぞれ`COMMA`／`PERIOD`になります。

この復元ブランチには、右トラックボールのCOROPIT用X/Y反転がすでに適用されています。
ユーザー指定の差分としてCPIだけを旧設定の `cpi = <600>` から `cpi = <3200>` に変更しました。
PMW3610ドライバとDevicetree bindingが定めるCPI範囲は200〜3200（200刻み）であり、3200が上限です。配列原本、レイヤー、クリック、マトリクス、接続登録は変更していません。
この変更では右手用UF2だけを書き換え、通常は設定リセットを行う必要はありません。
Bluetooth接続登録は保持されます。
以前のv2設定の
`scroller { layers = <3>; }` は、実レイヤー3がBluetooth設定であるこの配列に干渉するため削除しました。
通常のポインターとして動作し、コメントアウトされた自動マウスレイヤーも有効にしていません。

原本と現在の設定の一致、およびv2のマトリクス・GPIO・トラックボール設定は
`tests/test_original_layout.py` で確認します。
