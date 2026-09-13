# 配列と許容差分

`tests/fixtures/old-main.keymap`は旧Mac配列の原本で、SHA-256は`adfcddcf616d63021b3a818f0aad10ebeb40b1a86a2926e1ad8f23588dd85348`です。fixture自体は変更しません。テストは4レイヤー各42キーとセンサーbindingを照合し、以下だけを許容します。

| レイヤー | 位置 | 元のbinding | 現在のbinding | 用途 |
| --- | ---: | --- | --- | --- |
| `Maclayer` | 15 | `&atSlash` | `&kp LC(LS(NUMBER_4))` | CleanShot範囲撮影 |
| `layer_3` | 3 | `&trans` | `&kp LG(LC(V))` | 音声再貼付 |
| `layer_3` | 4 | `&trans` | `&kp LC(LA(LG(T)))` | CleanShot OCR |
| `layer_3` | 5 | `&trans` | `&kp LC(LA(LG(LEFT_ARROW)))` | 左半分 |
| `layer_3` | 6 | `&trans` | `&kp LC(LA(LG(F)))` | 画面全体に表示 |
| `layer_3` | 7 | `&trans` | `&kp LC(LA(LG(RIGHT_ARROW)))` | 右半分 |
| `layer_3` | 8 | `&trans` | `&kp LC(LA(LG(C)))` | 中央 |
| `layer_3` | 9 | `&trans` | `&kp LC(LA(LG(R)))` | 前のサイズに戻す |
| `layer_3` | 25 | `&trans` | `&kp LC(LA(LG(B)))` | Clipboard History |

数字層`layer_1`の位置14にある`&kp LS(LC(NUMBER_4))`と、通常層の位置35にある`&kp F13`は原本どおりです。SpaceまたはEnterを長押しして`layer_3`へ入り、上表の編集補助を使います。`/`長押しの`layer_4`にはBLE選択、bootloader、Bluetooth消去を維持しています。

原本には未使用の`atSlash`マクロと範囲外レイヤーを示す`MOUSE`/`SCROLL`定義があります。現在は位置15のショートカットへ置き換えたため、未使用のマクロと定義を削除しています。
