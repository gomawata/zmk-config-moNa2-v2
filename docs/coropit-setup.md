# COROPIT セットアップ

右側は`mona2_r-coropit`、左側は`mona2_l`のUF2を書き込む。通常は両側を更新するだけでよく、`settings_reset`は不要です。UF2更新では[ZMK Settings](https://zmk.dev/docs/config/settings)のpersistent settingsが残ります。

右側をUSB接続し、DYA StudioでCPIを3200、X反転を有効、Y反転とXY入替を無効にしていることを確認する。必要なら上書きして保存し、10秒以上電源を維持する。Studioに保存済みのキーマップがある場合は、右側で[Restore Stock Settings](https://zmk.dev/docs/features/studio)を実行して、コンパイル済みの4レイヤー配列を有効にする。この操作がPMW3610のカスタム設定まで消去するかは未確認です。

Runtime Input Processorの保存済みマウス設定は、キーマップを保存していない個体にも残ることがある。更新後、使い始める前にDYA Studioでmouseの一時レイヤーと`xy-to-scroll`が無効であることを確認し、必要なら無効にして保存する。レイヤー指定など、4レイヤー配列に干渉する設定も確認する。Restore Stock Settings後は設定変更イベントで実行中のRuntime Input Processor設定が再適用されないため、右側を再起動してから同じ項目を再確認する。

左右が接続できないなど必要な場合だけ、両側に`settings_reset`を書き込んでから、各側へ通常UF2を書き込む。その後、Macに残る旧Bluetooth登録を忘れて再ペアリングする。[接続トラブルシューティング](https://zmk.dev/docs/troubleshooting/connection-issues)も参照する。

旧0.3系Custom Settingsの移行は保証しておらず、実機でも未検証です。
