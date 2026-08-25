# 配布用 標準キーマップ（`standard-keymap` ブランチ）

`main` のキーマップは作者の使い方に寄せた設定（コンボ限定の ESC/TAB、Z のホームロウ
モディファイア、日本語 IME 用の LANG1/LANG2、余りキーの F13〜F16）になっている。
このブランチは、**初めて moNa2 を触る人がそのまま動作確認できる**ことだけを目的に、
一般的なキー配列へ寄せたもの。レイヤー 1〜4 / MOUSE / SCROLL の構成は `main` のまま。

## default_layer（レイヤー0）

```
          左手                                      右手
 row1   Q     W     E     R     T                     Y     U     I     O     P
 row2   A     S     D     F     G              ESC    H     J     K     L     ;
 row3   Z     X     C     V     B     TAB      DEL    N     M     ,     .     /
 row4   Ctrl  GUI   Shift BS    Ent*  L3       L3     Spc*                    Alt
```

- `Ent*` … タップで **Enter**、長押しで **layer_2**（記号レイヤー）
- `Spc*` … タップで **Space**、長押しで **layer_1**（数字レイヤー）
- `L3` … 長押しで **layer_3**（カーソル / ウィンドウ操作）。左右どちらの親指キーでも同じ
- 左右の `L3` を**同時押し**すると **layer_4**（Bluetooth 設定・bootloader）
- 左手側のロータリーエンコーダー … 上下スクロール

## `main` からの変更点

| 位置 | main | このブランチ | 理由 |
| --- | --- | --- | --- |
| 右手 row2 内側 | `F13` | `ESC` | F13〜F16 は導通チェック用の埋め草で、一般の用途では何も起きない |
| 左手 row3 内側 | `F14` | `TAB` | 同上。TAB をコンボから実キーへ |
| 右手 row3 内側 | `F15` | `DEL` | 同上 |
| 左手 row4 3番目 | `F16` | `Shift` | Z のホームロウ mod を外したため、Shift の置き場所が必要 |
| 左手 row3 1番目 | `&mt LEFT_SHIFT Z` | `Z` | 押しっぱなしで Shift になる挙動は初見で戸惑うため解除 |
| 両親指 | `&lt_to_layer_0 3 LANG1/LANG2` | `&mo 3` | 日本語 IME 前提の かな/英数 を外し、素のレイヤーキーに |
| コンボ `S`+`D` | `TAB` | 削除 | TAB を実キーに出したため不要 |
| コンボ 両親指 | `&lt 4 ESC` | `&mo 4` | ESC を実キーに出したので、レイヤー4へ入る役割だけ残した |
| layer_1 の `A` 位置 | `&bt BT_PRV` | `&trans` | 作者個人の割り当てを撤去 |
| layer_2 の左下 | `&gresc` | `&trans` | 同上 |

日本語入力の かな/英数 切り替えが必要な場合は、両親指の `&mo 3` を
`&lt_to_layer_0 3 LANG1` / `&lt_to_layer_0 3 LANG2` に戻すと `main` と同じ挙動になる
（`lt_to_layer_0` の定義はこのブランチにも残してある）。

## ファームウェアの入手と書き込み

1. GitHub の **Actions → Build** から、このブランチの最新の成功したビルドを開く
2. Artifacts の `firmware` をダウンロードして展開する
3. 各 uf2 を書き込む
   - `mona2_l rgbled_adapter-seeeduino_xiao_ble-zmk.uf2` … 左手側
   - `mona2_r rgbled_adapter-seeeduino_xiao_ble-zmk.uf2` … 右手側（トラックボール側）
   - `settings_reset-seeeduino_xiao_ble-zmk.uf2` … 設定のリセット用（下記参照）
4. 書き込みは、XIAO のリセットボタンを素早く2回押してブートローダー（`XIAO-SENSE` ドライブ）
   を出し、uf2 をドラッグ＆ドロップ

## 先に settings_reset を当てる

このリポジトリは ZMK Studio 有効（`CONFIG_ZMK_STUDIO=y`）のため、**過去に ZMK Studio や
keymap editor で本体側に保存したキーマップが、ファームを焼き直しても残る**。
配布先で「このブランチの配列と違う」となる場合は、左右それぞれに
`settings_reset` の uf2 を先に書き込んでから、上記の左右ファームを書き込む。
Bluetooth のペアリング情報も消えるので、その後ホストとペアリングし直す。

## 動作確認のチェックリスト

- [ ] 左手 21 キー / 右手 21 キーがすべて反応する（レイヤー0 だけで全キーが文字か修飾キーを出す）
- [ ] `Ent*` `Spc*` をタップすると Enter / Space、長押し中に記号・数字が出る
- [ ] 左右どちらの親指 `L3` でもカーソルキーが使える
- [ ] 両親指同時押し → layer_4 で `&bt BT_SEL 0`〜`4`、`&bt BT_CLR` が効く
- [ ] 右手側トラックボールでポインタが動く（COROPIT 版として正しい向きか。反転していたら下記参照）
- [ ] 左手側ロータリーエンコーダーでスクロールする
- [ ] 左右が BLE で接続され、電池残量が OS 側に見える

## トラックボールは COROPIT 版前提

このブランチ（および `main`）の `boards/shields/mona2/mona2_r.overlay` は、
**COROPIT 版トラックボールモジュール向けに `invert-x` / `invert-y` を有効にした状態**。
COROPIT 付きの個体にそのまま焼けば、ポインタの上下左右は正しい向きで動く。

自作 PMW3610 など COROPIT 以外のモジュールに載せ替える場合は、この2行を
コメントアウトに戻す（README の「COROPIT を使用する方へ」の逆操作）。

```
        cpi = <600>;
        //swap-xy;
        invert-x; //COROPIT版ではコメントアウトを外す
        invert-y; //COROPIT版ではコメントアウトを外す
```
