#!/bin/bash

# WireGuardのインストール
echo "WireGuardをインストールしています..."
sudo apt update
sudo apt install -y wireguard

# 必要な情報をユーザーから取得
read -p "サーバーのグローバルIPアドレスを入力してください: " SERVER_IP
read -p "WireGuardのリスニングポートを入力してください (デフォルト: 51820): " LISTEN_PORT
LISTEN_PORT=${LISTEN_PORT:-51820}
read -p "VPN用のサブネットを入力してください (例: 10.0.0.1/24): " VPN_SUBNET

# サーバーのエンドポイント情報を保存 (qrcode.shで利用)
echo "${SERVER_IP}:${LISTEN_PORT}" | sudo tee /etc/wireguard/server_endpoint_info > /dev/null

# サーバーの秘密鍵と公開鍵を生成
echo "サーバー用のキーペアを生成しています..."
wg genkey | sudo tee /etc/wireguard/privatekey | wg pubkey | sudo tee /etc/wireguard/publickey
PRIVATE_KEY=$(sudo cat /etc/wireguard/privatekey)

# サーバー設定ファイルを作成
echo "サーバー設定ファイルを作成しています..."
sudo tee /etc/wireguard/wg0.conf > /dev/null <<EOL
[Interface]
Address = ${VPN_SUBNET}
SaveConfig = true
ListenPort = ${LISTEN_PORT}
PrivateKey = ${PRIVATE_KEY}
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
EOL

# WireGuardを起動
echo "WireGuardを起動しています..."
sudo wg-quick up wg0

# システム起動時にWireGuardが自動的に起動するように設定
sudo systemctl enable wg-quick@wg0

echo ""
echo "WireGuardサーバーのセットアップが完了しました。"
echo "クライアント設定を追加するには、'wg set wg0 peer <クライアント公開鍵> allowed-ips <クライアントIP>' を実行してください。"
echo "例: wg set wg0 peer ABC...= allowed-ips 10.0.0.2/32"
