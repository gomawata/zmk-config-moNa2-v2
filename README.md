# zmk-config-moNa2

<img src="keymap-drawer/mona2_01.svg">

## このworktreeの位置づけ

このcheckoutはmainの基準variantで、Mac向け正本そのものではありません。ユーザーが選定した現行firmware sourceは、Mac/COROPIT 1600 CPI系統のfeature/mac-voice-capture-latest（コードcommit e9f95de）です。旧Mac復元variantはArchiveに分け、どちらもこの共通Gitから独立worktreeとして保持します。

- [選定されたMac/COROPIT 1600 CPI正本](../zmk-config-moNa2-mac-20260913/README.md): feature/mac-voice-capture-latest、コードcommit e9f95de
- [Archiveの旧Mac復元版](../Archive/zmk-config-moNa2-original-mac/README.md): restore/original-macの配列一致契約
- [キーマップ変更履歴サイト](../mona2-keymap-site/README.md): 履歴を保存するWebツール。firmwareは更新しない
- [選定された1600 CPI配布物](../mona2-mac-firmware-delivery/2026-09-13-1600CPI/README.txt) と [同日3200 CPIの前版](../mona2-mac-firmware-delivery/2026-09-13/README.md)。旧Mac配布物は[Archive](../Archive/mona2-original-mac-delivery/README.md)に保持

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
