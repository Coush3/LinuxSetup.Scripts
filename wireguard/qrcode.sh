#!/bin/bash

HISTORY_DIR=~/.wireguard_clients
mkdir -p "$HISTORY_DIR"

# サーバーの公開鍵ファイルが存在するか確認
SERVER_PUBLIC_KEY_PATH="/etc/wireguard/publickey"
SERVER_ENDPOINT_INFO_PATH="/etc/wireguard/server_endpoint_info"

if [ ! -f "$SERVER_PUBLIC_KEY_PATH" ] || [ ! -f "$SERVER_ENDPOINT_INFO_PATH" ]; then
    echo "エラー: WireGuardサーバーの公開鍵ファイルまたはエンドポイント情報ファイルが見つかりません。"
    echo "先に setup.sh を実行してWireGuardサーバーをセットアップしてください。"
    exit 1
fi

# サーバーの公開鍵を読み込む
SERVER_PUBLIC_KEY=$(sudo cat "$SERVER_PUBLIC_KEY_PATH")

# サーバーのエンドポイントを読み込む
SERVER_ENDPOINT=$(sudo cat "$SERVER_ENDPOINT_INFO_PATH")

# qrencodeがインストールされているか確認
if ! command -v qrencode &> /dev/null
then
    echo "qrencode がインストールされていません。"
    read -p "インストールしますか？ (y/n): " INSTALL_QRENCODE
    if [ "$INSTALL_QRENCODE" = "y" ]; then
        sudo apt update
        sudo apt install -y qrencode
    else
        echo "QRコードを生成できませんでした。"
        exit 1
    fi
fi

# QRコードと追加コマンドを表示する関数
display_config() {
    local config_content="$1"
    local add_command="$2"

    echo ""
    echo "------------------------------------------------------------"
    echo "クライアント設定のQRコード:"
    qrencode -t ansiutf8 <<< "$config_content"
    echo "------------------------------------------------------------"
    echo ""
    echo "サーバーにこのクライアントを追加するには、以下のコマンドを実行してください:"
    echo "$add_command"
    echo "------------------------------------------------------------"
}

# 新しいクライアントを作成する関数
generate_new_client() {
    read -p "このクライアント設定に名前を付けてください (例: my-phone): " CLIENT_NAME
    if [ -z "$CLIENT_NAME" ]; then
        echo "エラー: クライアント名は必須です。" >&2
        exit 1
    fi

    # 必要な情報をユーザーから取得
    local client_private_key=$(wg genkey)
    local client_public_key=$(echo "$client_private_key" | wg pubkey)

    read -p "クライアントのVPN内IPアドレスを入力してください (例: 10.0.0.2): " CLIENT_IP

    # クライアント設定を作成
    local client_config="[Interface]\nPrivateKey = $client_private_key\nAddress = $CLIENT_IP/32\nDNS = 8.8.8.8\n\n[Peer]\nPublicKey = $SERVER_PUBLIC_KEY\nAllowedIPs = 0.0.0.0/0\nEndpoint = $SERVER_ENDPOINT"
    local add_command="sudo wg set wg0 peer $client_public_key allowed-ips $CLIENT_IP/32"

    # 履歴ファイルに保存
    echo -e "$client_config" > "$HISTORY_DIR/$CLIENT_NAME.conf"
    echo "$add_command" > "$HISTORY_DIR/$CLIENT_NAME.sh"

    echo ""
    echo "新しいクライアント '$CLIENT_NAME' を作成し、保存しました。"
    display_config "$client_config" "$add_command"
}

# 履歴を表示する関数
show_history() {
    echo ""
    echo "保存されているクライアント設定:"
    # confファイルの一覧を表示 (拡張子なし)
    find "$HISTORY_DIR" -name "*.conf" -printf "%f\n" | sed 's/\.conf$//'
    echo ""

    read -p "再表示するクライアントの名前を入力してください: " CLIENT_TO_SHOW

    if [ -f "$HISTORY_DIR/$CLIENT_TO_SHOW.conf" ] && [ -f "$HISTORY_DIR/$CLIENT_TO_SHOW.sh" ]; then
        local config_content=$(cat "$HISTORY_DIR/$CLIENT_TO_SHOW.conf")
        local add_command=$(cat "$HISTORY_DIR/$CLIENT_TO_SHOW.sh")
        display_config "$config_content" "$add_command"
    else
        echo "エラー: クライアント '$CLIENT_TO_SHOW' が見つかりません。"
    fi
}

# クライアント設定を削除する関数
delete_client() {
    echo ""
    echo "保存されているクライアント設定:"
    find "$HISTORY_DIR" -name "*.conf" -printf "%f\n" | sed 's/\.conf$//'
    echo ""

    read -p "削除するクライアントの名前を入力してください: " CLIENT_TO_DELETE

    if [ -f "$HISTORY_DIR/$CLIENT_TO_DELETE.conf" ]; then
        read -p "本当にクライアント '$CLIENT_TO_DELETE' を削除しますか？ (y/n): " CONFIRM_DELETE
        if [ "$CONFIRM_DELETE" = "y" ]; then
            rm "$HISTORY_DIR/$CLIENT_TO_DELETE.conf"
            rm "$HISTORY_DIR/$CLIENT_TO_DELETE.sh"
            echo "クライアント '$CLIENT_TO_DELETE' を削除しました。"
        else
            echo "削除を中止しました。"
        fi
    else
        echo "エラー: クライアント '$CLIENT_TO_DELETE' が見つかりません。"
    fi
}


# メインロジック
clear
echo "WireGuard クライアント設定ジェネレーター"
echo "======================================"
echo "操作を選択してください:"
echo "  1) 新しいクライアント設定を作成する"
echo "  2) 既存のクライアント設定を再表示する"
echo "  3) 既存のクライアント設定を削除する"
read -p "選択 (1-3): " choice

case $choice in
    1)
        generate_new_client
        ;;
    2)
        show_history
        ;;
    3)
        delete_client
        ;;
    *)
        echo "無効な選択です。"
        exit 1
        ;;
esac
