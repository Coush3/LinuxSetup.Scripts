#!/bin/bash

# WireGuardがインストールされているか確認
if ! command -v wg &> /dev/null
then
    echo "エラー: WireGuardがインストールされていません。"
    echo "setup.sh を実行してWireGuardをインストールしてください。"
    exit 1
fi

# wg0 インターフェースが存在するか確認
if ! sudo wg show wg0 &> /dev/null
then
    echo "エラー: WireGuardインターフェース 'wg0' が見つからないか、起動していません。"
    echo "setup.sh を実行してWireGuardサーバーをセットアップしてください。"
    exit 1
fi

clear
echo "WireGuard 接続ステータス (wg0)"
echo "======================================"

# wg show コマンドの出力を整形して表示
sudo wg show wg0

echo "\n詳細情報:"
# 各ピアの情報をより詳細に表示
sudo wg show wg0 peers

# 転送量などの統計情報を表示
sudo wg show wg0 transfer

echo "\n======================================"
echo "上記は 'wg show wg0' コマンドの出力です。"
echo "各ピアの 'latest handshake' が最近であれば、接続がアクティブであることを示します。"
