# zmk-config-moNa2

<img src="docs/original-mac-layout.svg" alt="復元した旧moNa2 Mac配列">

## 旧 Mac 配列を使う

旧設定から復元した配列、右側のBackspace／Enter／マウスキー、COROPITトラックボールの扱いは
[旧 Mac 配列の復元](docs/original-mac-layout.md) を参照してください。

配列原本は保持し、ユーザー指定の差分として右トラックボールのCPIだけを600からドライバ上限の3200へ変更しています。

# COROPITを使用するへ

この復元ブランチではCOROPIT用の設定（`cpi = <3200>`、X/Y反転）がすでに適用済みです。
PMW3610ドライバとDevicetree bindingのCPI範囲は200〜3200（200刻み）で、3200が上限です。
右手用UF2を書き換えるだけでよく、通常は設定リセットを行う必要はありません。配列とBluetooth接続登録は保持されます。
以下は設定内容の参照です。

mona2_r.overlay

旧設定（600 CPI）
```
  trackball_central: trackball_central@0 {
        status = "okay";
        compatible = "pixart,pmw3610";  //トラボセンサ用のドライバとバインド
        reg = <0>;
        spi-max-frequency = <2000000>;
        irq-gpios = <&gpio0 2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>; //P0.02を指定(MOTION)
        cpi = <600>;
        //swap-xy;
        invert-x; //COROPIT版で有効
        invert-y; //COROPIT版で有効
        evt-type = <INPUT_EV_REL>;
        x-input-code = <INPUT_REL_X>;
        y-input-code = <INPUT_REL_Y>;
    };
};

```
**現在の設定（3200 CPI）**
```
  trackball_central: trackball_central@0 {
        status = "okay";
        compatible = "pixart,pmw3610";  //トラボセンサ用のドライバとバインド
        reg = <0>;
        spi-max-frequency = <2000000>;
        irq-gpios = <&gpio0 2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>; //P0.02を指定(MOTION)
        cpi = <3200>;
        //swap-xy;
        invert-x; //COROPIT版ではコメントアウトを外す
        invert-y; //COROPIT版ではコメントアウトを外す
        evt-type = <INPUT_EV_REL>;
        x-input-code = <INPUT_REL_X>;
        y-input-code = <INPUT_REL_Y>;
    };
};

```
