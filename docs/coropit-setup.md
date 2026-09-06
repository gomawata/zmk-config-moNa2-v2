# COROPIT セットアップ

この専用ブランチのファームウェアはまだ生成・ビルド検証していない。GitHub Actionsでの検証はpush許可待ち。ローカルテストは設定選択とソース設定の読み合わせのみで、Kconfig評価・コンパイル・実機検証を代替しない。

## 書き込むファームウェア

- Actionsが成功したら、成果物 `firmware` のZIPを取得する。
- 右側: ZIP内の `mona2_r-coropit*.uf2`。
- 左側: 同じZIP内の `mona2_l*.uf2`（共通版）。
- Central（中央／親機）は RIGHT。

USB接続中にリセットを2回押してブートローダーへ入り、左右それぞれに一致する UF2 をコピーする。Chrome / Edgeで [DYA Studio](https://studio.dya.cormoran.works/) を開き、右側のUSBから接続する。現在は `CONFIG_ZMK_STUDIO_LOCKING=n` なのでアンロック操作を必須としない。Custom Settings に保存済みの値がある場合は、`coropit.conf` の初期値より保存値が優先される。

`settings_reset` は設定とボンドを消去するため、通常は使わない。意図的な復旧時だけ使う。書き込み後は、まず有線でポインターの X/Y、クリック、全キー、エンコーダーを確認し、BLE は最後に確認する。

`coropit` はセンサー CPI を 600 から 3200 にし、同じ移動量で得られるセンサーカウントを約 5.33 倍にする（OS 全体のカーソル速度が正確に 5.33 倍になるという意味ではない）。DYA Studio に CPI の保存値がある場合はそちらが優先されるため、既に設定済みなら「トラックボールセンサー」でセンサー CPI を 3200 に設定する。

## 向きの根拠

この構成の明示値は X反転=`y`、Y反転=`n`、XY入替=`n`。README にある COROPIT の Y反転という説明は、現行ドライバーに対しては古く誤っている。旧ドライバーの `ORIENTATION_0` は `x=-raw_x, y=raw_y`。現行ドライバーで上記の値を指定すると、この軸変換に相当する。設定名自体を移植しない。実際の上下左右は到着後に確認する。

- ベンダー: https://booth.pm/ja/items/6830658
- 旧ドライバーの `ORIENTATION_0`: https://github.com/sayu-hub/zmk-pmw3610-driver/blob/main/src/pmw3610.c#L662-L682
- ベンダーリンクの旧コミット: https://github.com/black-trooper/zmk-config-moNa2/commit/c1f7dcc5453e3a5b96738811c68e6c66e976c586
- 現代の swap→invert: https://github.com/cormoran/zmk-driver-pmw3610-with-custom-studio-rpc/blob/5c34ea0eec246a1c986111417cd779b53144629a/src/pmw3610.c#L611-L625

## ロールバック

変更を保存してから、ローカルで元の `feature/dya-studio-support` に切り替える。元のファームウェアは、出所が確認できる既知のものがある場合だけ復元する。
