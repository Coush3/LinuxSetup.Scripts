#!/bin/bash

# スクリプトが設置されているディレクトリを取得
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
LOCK_FILE="$SCRIPT_DIR/.install_lock"

# 初回起動かどうかをチェック
if [ ! -f "$LOCK_FILE" ]; then
    echo "初回セットアップを実行します..."

    # 1. 必要なPythonモジュールをインストール
    echo "python3-pipをインストールします..."
    sudo apt update
    sudo apt install -y python3-pip
    if [ $? -ne 0 ]; then
        echo "エラー: python3-pipのインストールに失敗しました。"
        exit 1
    fi

    echo "必要なモジュール (PyYAML, Flask) をインストールします..."
    # pipがシステムにインストールされている場所に依存しないようにpython3 -m pipを使用
    python3 -m pip install PyYAML Flask
    if [ $? -ne 0 ]; then
        echo "エラー: モジュールのインストールに失敗しました。"
        exit 1
    fi

    # 2. menu.py を実行する menu スクリプトを作成
    echo "起動スクリプト 'menu' を作成します..."
    cat <<'EOF' > "$SCRIPT_DIR/menu"
#!/bin/bash
# このスクリプト自身のディレクトリを取得し、そこにあるmenu.pyを実行
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
python3 "$SCRIPT_DIR/menu.py" "$@"
EOF

    # 3. menu スクリプトに実行権限を付与
    chmod +x "$SCRIPT_DIR/menu"
    echo "'menu' に実行権限を付与しました。"

    # 4. リポジトリを更新する update スクリプトを作成
    echo "更新スクリプト 'update' を作成します..."
    cat <<'EOF' > "$SCRIPT_DIR/update"
#!/bin/bash
# このスクリプト自身のディレクトリに移動し、git pullを実行
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
cd "$SCRIPT_DIR"
git pull
EOF

    # 5. update スクリプトに実行権限を付与
    chmod +x "$SCRIPT_DIR/update"
    echo "'update' に実行権限を付与しました。"

    # 6. webmenu.py を実行する webmenu スクリプトを作成
    echo "起動スクリプト 'webmenu' を作成します..."
    cat <<'EOF' > "$SCRIPT_DIR/webmenu"
#!/bin/bash
# このスクリプト自身のディレクトリを取得し、そこにあるwebmenu.pyを実行
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
python3 "$SCRIPT_DIR/webmenu.py" "$@"
EOF

    # 7. webmenu スクリプトに実行権限を付与
    chmod +x "$SCRIPT_DIR/webmenu"
    echo "'webmenu' に実行権限を付与しました。"

    # 8. ロックファイルを作成
    touch "$LOCK_FILE"

    echo "セットアップが完了しました。"
    echo "今後は ./menu コマンドでアプリケーションを起動できます。"

    # ホームディレクトリにシンボリックリンクを作成するかの確認
    echo
    read -p "ホームディレクトリ (~/) に 'menu' と 'webmenu' のショートカットを作成しますか？ (y/N): " answer
    case ${answer:0:1} in
        y|Y )
            echo "ショートカットを作成します..."
            # menu
            if [ -f "$HOME/menu" ]; then
                echo "警告: ~/menu は既に存在します。上書きはしませんでした。"
            else
                ln -s "$SCRIPT_DIR/menu" "$HOME/menu"
                echo "~/menu を作成しました。"
            fi
            # webmenu
            if [ -f "$HOME/webmenu" ]; then
                echo "警告: ~/webmenu は既に存在します。上書きはしませんでした。"
            else
                ln -s "$SCRIPT_DIR/webmenu" "$HOME/webmenu"
                echo "~/webmenu を作成しました。"
            fi
            echo "今後はターミナルのどこからでも 'menu' または 'webmenu' コマンドで起動できます。"
        ;;
        * )
            echo "ショートカットは作成しませんでした。"
        ;;
    esac

else
    echo "セットアップは既に完了しています。"
    echo "./menu コマンドでアプリケーションを起動してください。"
fi