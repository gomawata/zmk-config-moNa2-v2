# zmk-config-moNa2

<img src="keymap-drawer/mona2_01.svg">

## このworktreeの位置づけ

これは `main` の moNa2 v2 設定です。Mac/COROPIT の現用候補や旧Mac復元版をここへ自動で取り込まず、用途ごとに別worktreeと配布証跡を維持します。どれを標準にするかは、対象機器・配列・CPI・実機確認をそろえてから決めます。

- [Mac/COROPIT 1600 CPI候補](../zmk-config-moNa2-mac-20260913/README.md): `feature/mac-voice-capture-latest` の設定とMac向け手順
- [旧Mac復元版](../zmk-config-moNa2-original-mac/README.md): `restore/original-mac` の配列一致契約
- [キーマップ変更履歴サイト](../mona2-keymap-site/README.md): 履歴を保存するWebツール。firmwareは更新しない
- [2026-09-13 Mac/COROPIT配布物](../mona2-mac-firmware-delivery/2026-09-13/README.md) と [旧Mac配布物](../mona2-original-mac-delivery/README.md): source、hash、復旧手順を含む固定証跡

ソースを採用する場合は、対象のworktreeでlockに基づくビルド、UF2 hash、左右・配列・CPI・Studio保存を確認します。README上のリンクは設定や配布を変更しません。

# COROPITを使用するへ

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
