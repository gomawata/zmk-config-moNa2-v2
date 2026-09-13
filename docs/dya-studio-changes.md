# DYA Studio 基盤

この構成はZMK Studio/DYA Studioの通信、トラックボールのカスタム設定、ランタイムエンコーダ設定を維持します。キーマップはMac専用の4レイヤーで、OS自動選択、Windows配列、自動クリック層、マウスジェスチャーは有効にしません。

Studioに保存されたキーマップはコンパイル済みのキーマップを上書きするため、配列を更新した後は右側USB接続で[Restore Stock Settings](https://zmk.dev/docs/features/studio)を実行してください。PMW3610設定への影響は未確認です。

Runtime Input Processorのmouse設定はキーマップと別に保存されます。更新後、使い始める前にmouseの一時レイヤーと`xy-to-scroll`が無効であることを確認し、必要なら無効にして保存します。レイヤー指定も4レイヤー配列と矛盾しない値にします。Restore後は右側を再起動して確認してください。
