# zmk-config-moNa2

> **`standard-keymap` ブランチについて**
> このブランチは配布・動作確認用に、default_layer を一般的なキー配列へ戻したもの。
> 配列の内容・ファームの入手方法・確認手順は [STANDARD_KEYMAP.md](STANDARD_KEYMAP.md) を参照。

<img src="keymap-drawer/mona2_01.svg">

# COROPITを使用するへ

> **注記**: このリポジトリの `main` および `standard-keymap` では、この編集は
> **すでに適用済み**（`invert-x` / `invert-y` が有効）。COROPIT 以外のトラックボール
> モジュールを使う場合は、逆にこの2行をコメントアウトに戻すこと。

COROPITを使用する方は以下のようにコードを編集してください。

mona2_r.overlay

修正前
```
  trackball_central: trackball_central@0 {
        status = "okay";
        compatible = "pixart,pmw3610";  //トラボセンサ用のドライバとバインド
        reg = <0>;
        spi-max-frequency = <2000000>;
        irq-gpios = <&gpio0 2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>; //P0.02を指定(MOTION)
        cpi = <600>;
        //swap-xy;
        //invert-x; //COROPIT版ではコメントアウトを外す
        //invert-y; //COROPIT版ではコメントアウトを外す
        evt-type = <INPUT_EV_REL>;
        x-input-code = <INPUT_REL_X>;
        y-input-code = <INPUT_REL_Y>;
    };
};

```
**修正後**
```
  trackball_central: trackball_central@0 {
        status = "okay";
        compatible = "pixart,pmw3610";  //トラボセンサ用のドライバとバインド
        reg = <0>;
        spi-max-frequency = <2000000>;
        irq-gpios = <&gpio0 2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>; //P0.02を指定(MOTION)
        cpi = <600>;
        //swap-xy;
        invert-x; //COROPIT版ではコメントアウトを外す
        invert-y; //COROPIT版ではコメントアウトを外す
        evt-type = <INPUT_EV_REL>;
        x-input-code = <INPUT_REL_X>;
        y-input-code = <INPUT_REL_Y>;
    };
};

```
