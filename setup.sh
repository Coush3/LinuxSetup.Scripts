#!/bin/bash

# スクリプトが設置されているディレクトリを取得
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
LOCK_FILE="$SCRIPT_DIR/.install_lock"

# 初回起動かどうかをチェック
if [ ! -f "$LOCK_FILE" ]; then
    echo "初回セットアップを実行します..."

    # 1. 必要なPythonモジュールをインストール
    echo "必要なモジュール (PyYAML) をインストールします..."
    # pipがシステムにインストールされている場所に依存しないようにpython3 -m pipを使用
    python3 -m pip install PyYAML Flask
    if [ $? -ne 0 ]; then
        echo "エラー: モジュールのインストールに失敗しました。"
        exit 1
    fi

    # 2. main.py を実行する menu スクリプトを作成
    echo "起動スクリプト 'menu' を作成します..."
    cat <<EOF > "$SCRIPT_DIR/menu"
#!/bin/bash
# このスクリプト自身のディレクトリを取得し、そこにあるmain.pyを実行
SCRIPT_DIR=\$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
python3 "$SCRIPT_DIR/menu.py" "$@"
EOF

    # 3. menu スクリプトに実行権限を付与
    chmod +x "$SCRIPT_DIR/menu"
    echo "'menu' に実行権限を付与しました。"

    # 4. ロックファイルを作成
    touch "$LOCK_FILE"

    echo "セットアップが完了しました。"
    echo "今後は ./menu コマンドでアプリケーションを起動できます。"

else
    echo "セットアップは既に完了しています。"
    echo "./menu コマンドでアプリケーションを起動してください。"
fi