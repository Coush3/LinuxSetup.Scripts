import json
import os
import subprocess
import sys
import curses

def main():
    # コマンドライン引数を確認
    if len(sys.argv) > 1:
        # 引数があれば、それを機能IDとして直接実行
        function_id = sys.argv[1]
        execute_function(function_id)
    else:
        # 引数がなければ、メニューを表示
        function_id = curses.wrapper(show_menu)
        if function_id:
            execute_function(function_id)

def show_menu(stdscr):
    # cursesの初期設定
    curses.curs_set(0)
    stdscr.nodelay(0)
    stdscr.timeout(-1)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # メニューデータの読み込み
    with open("menu.yaml", "r", encoding="utf-8") as f:
        menu_data = yaml.safe_load(f)
    
    # メニュー階層を管理するスタック
    menu_stack = [menu_data["menu"]]
    # 選択中の行を管理するスタック
    row_stack = [0]
    # パンくずリストのためのタイトルスタック
    title_stack = ["Home"]

    while True:
        stdscr.clear()
        
        # パンくずリストの表示
        breadcrumb = " > ".join(title_stack)
        stdscr.addstr(0, 0, breadcrumb)
        stdscr.addstr(1, 0, "=" * (len(breadcrumb) + 4))

        # 現在のメニュー項目を取得
        current_menu_items = menu_stack[-1]
        current_row = row_stack[-1]

        for i, item in enumerate(current_menu_items):
            if i == current_row:
                stdscr.addstr(i + 3, 0, f"> {item['title']}", curses.color_pair(1))
            else:
                stdscr.addstr(i + 3, 0, f"  {item['title']}")
        
        # 説明の表示
        description = current_menu_items[current_row].get('description', '')
        stdscr.addstr(len(current_menu_items) + 5, 0, description)
        
        stdscr.refresh()

        key = stdscr.getch()
        
        current_row = row_stack[-1]

        if key == curses.KEY_UP:
            row_stack[-1] = (current_row - 1) % len(current_menu_items)
        elif key == curses.KEY_DOWN:
            row_stack[-1] = (current_row + 1) % len(current_menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            selected_item = current_menu_items[current_row]
            if "items" in selected_item:
                # サブメニューに移動
                menu_stack.append(selected_item["items"])
                row_stack.append(0)
                title_stack.append(selected_item["title"])
            elif "id" in selected_item:
                # 実行するIDを返す
                return selected_item["id"]
        elif key == 27: # ESCキー
            if len(menu_stack) > 1:
                # 親メニューに戻る
                menu_stack.pop()
                row_stack.pop()
                title_stack.pop()
            else:
                # ルートメニューでESCなら終了
                return None


def execute_function(function_id):
    if function_id == "system_update":
        print("システムアップデートを実行します...")
        try:
            # apt update && apt upgrade を実行
            subprocess.run("sudo apt update && sudo apt upgrade -y", shell=True, check=True)
            print("システムアップデートが完了しました。")
        except subprocess.CalledProcessError as e:
            print(f"エラーが発生しました: {e}")

    elif function_id == "samba_install_and_share":
        print("Sambaのインストールと共有設定を開始します...")
        try:
            # Sambaがインストールされているか確認
            subprocess.run("dpkg -l | grep samba", shell=True, check=True, capture_output=True)
            print("Sambaは既にインストールされています。")
        except subprocess.CalledProcessError:
            print("Sambaをインストールします...")
            subprocess.run("sudo apt update && sudo apt install -y samba", shell=True, check=True)

        # 共有フォルダのパスをユーザーに要求
        share_path = input("共有したいフォルダのフルパスを入力してください: ")

        # パスが存在するか確認
        if not os.path.isdir(share_path):
            print(f"エラー: 指定されたパス '{share_path}' は存在しないか、フォルダではありません。")
            return

        # 共有名を設定 (フォルダ名から)
        share_name = os.path.basename(share_path)

        # smb.confに設定を追記
        smb_conf_path = "/etc/samba/smb.conf"
        share_config = f"""
[{share_name}]
path = {share_path}
read only = no
guest ok = yes
"""

        print(f"'{smb_conf_path}' に以下の設定を追記します:")
        print(share_config)

        try:
            with open(smb_conf_path, "a") as f:
                # sudo を使って書き込むために、teeコマンドを利用
                subprocess.run(f'echo "{share_config}" | sudo tee -a {smb_conf_path}', shell=True, check=True)
            print("設定を追記しました。")

            # Sambaサービスを再起動
            print("Sambaサービスを再起動します...")
            subprocess.run("sudo systemctl restart smbd", shell=True, check=True)
            print("Sambaサービスを再起動しました。")

        except Exception as e:
            print(f"エラーが発生しました: {e}")

    elif function_id == "install_ms_edit":
        print("Microsoft Editのインストールを開始します...")
        try:
            # zstdがインストールされているか確認
            subprocess.run("dpkg -l | grep zstd", shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("zstdをインストールします...")
            subprocess.run("sudo apt update && sudo apt install -y zstd", shell=True, check=True)

    try:
        # ダウンロードと展開
        download_url = "https://github.com/microsoft/edit/releases/download/v1.2.0/edit-1.2.0-x86_64-linux-gnu.tar.zst"
        file_name = download_url.split("/")[-1]
        
        print(f"{download_url} から {file_name} をダウンロードします...")
        subprocess.run(f"wget {download_url}", shell=True, check=True)

        print(f"{file_name} を展開します...")
        subprocess.run(f"tar -I zstd -xf {file_name}", shell=True, check=True)

        # インストール
        print("editを /usr/local/bin にインストールします...")
        subprocess.run("sudo mv edit /usr/local/bin/", shell=True, check=True)

        # クリーンアップ
        print(f"{file_name} を削除します...")
        os.remove(file_name)

        print("Microsoft Editのインストールが完了しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    else:
        print(f"未定義の機能IDです: {function_id}")

if __name__ == "__main__":
    main()