#!/bin/bash

# openvpn-install.sh スクリプトをダウンロードして実行
# このスクリプトはOpenVPNサーバーのインストールと設定を自動化します。
# https://github.com/Nyr/openvpn-install

echo "OpenVPNサーバーのセットアップを開始します。"
echo "Nyr/openvpn-install スクリプトをダウンロードして実行します。"

# スクリプトのダウンロード
wget -O openvpn-install.sh https://raw.githubusercontent.com/Nyr/openvpn-install/master/openvpn-install.sh

# 実行権限の付与
chmod +x openvpn-install.sh

# スクリプトの実行
sudo ./openvpn-install.sh

# ダウンロードしたスクリプトを削除 (任意)
rm openvpn-install.sh

echo "OpenVPNサーバーのセットアップが完了しました。"
