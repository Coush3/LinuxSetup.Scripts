import yaml
import os
import subprocess
import sys
import curses
import io
import argparse
import time
import re

# ヘルパー関数
def is_command_available(command):
    try:
        subprocess.run(f"which {command}", shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def is_package_installed(package_name):
    try:
        subprocess.run(f"dpkg -s {package_name}", shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def is_service_active(service_name):
    try:
        subprocess.run(f"systemctl is-active --quiet {service_name}", shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def is_process_running(process_name):
    if not process_name:
        return False
    # pgrep -f が自分自身を検知してしまうのを防ぐためのトリック
    # 例: "code serve-web" -> "[c]ode serve-web"
    pgrep_pattern = f"[{process_name[0]}]{process_name[1:]}"
    try:
        subprocess.run(f"pgrep -f '{pgrep_pattern}'", shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    parser = argparse.ArgumentParser(description="Linux Setup Menu CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # samba_delete_share コマンドのパーサー
    samba_delete_parser = subparsers.add_parser('samba_delete_share', help='Delete a Samba share')
    samba_delete_parser.add_argument('--share_name', type=str, help='Name of the Samba share to delete')

    # samba_install_and_share コマンドのパーサー
    samba_install_parser = subparsers.add_parser('samba_install_and_share', help='Install Samba and share a folder')
    samba_install_parser.add_argument('--share_path', type=str, help='Full path to the folder to share')

    # webmenu_reset_password コマンドのパーサー
    webmenu_reset_parser = subparsers.add_parser('webmenu_reset_password', help='Reset Webmenu password')

    # その他の直接実行可能なIDをここに追加
    # 例: system_update
    system_update_parser = subparsers.add_parser('system_update', help='Perform system update')

    # ufw_allow_8080
    ufw_allow_8080_parser = subparsers.add_parser('ufw_allow_8080', help='Allow 8080 port in ufw')
    # ufw_deny_8080
    ufw_deny_8080_parser = subparsers.add_parser('ufw_deny_8080', help='Deny 8080 port in ufw')
    # ufw_allow_8000
    ufw_allow_8000_parser = subparsers.add_parser('ufw_allow_8000', help='Allow 8000 port in ufw')
    # ufw_deny_8000
    ufw_deny_8000_parser = subparsers.add_parser('ufw_deny_8000', help='Deny 8000 port in ufw')
    # ufw_status
    ufw_status_parser = subparsers.add_parser('ufw_status', help='Show ufw status')

    # install_ms_edit
    install_ms_edit_parser = subparsers.add_parser('install_ms_edit', help='Install Microsoft Edit')
    # install_gh
    install_gh_parser = subparsers.add_parser('install_gh', help='Install GitHub CLI (gh)')
    # install_vscode_desktop
    install_vscode_desktop_parser = subparsers.add_parser('install_vscode_desktop', help='Install Visual Studio Code (Desktop)')
    # install_code_server
    install_code_server_parser = subparsers.add_parser('install_code_server', help='Install Code Server')
    # install_vscode_remote_server_deps
    install_vscode_remote_server_deps_parser = subparsers.add_parser('install_vscode_remote_server_deps', help='Install VS Code Remote - SSH Server dependencies')
    # screen_start
    screen_start_parser = subparsers.add_parser('screen_start', help='Start a new Screen session')
    # screen_resume
    screen_resume_parser = subparsers.add_parser('screen_resume', help='Resume an existing Screen session')
    # start_vscode_web_server
    start_vscode_web_server_parser = subparsers.add_parser('start_vscode_web_server_background', help='Start VS Code Web server in background')
    # get_vscode_web_server_url
    get_vscode_web_server_url_parser = subparsers.add_parser('get_vscode_web_server_url', help='Get VS Code Web server URL')
    # stop_vscode_web_server
    stop_vscode_web_server_parser = subparsers.add_parser('stop_vscode_web_server', help='Stop VS Code Web server')
    # code_server_start_manual
    code_server_start_manual_parser = subparsers.add_parser('code_server_start_manual', help='Start Code Server manually')
    # code_server_enable_and_start_service
    code_server_enable_and_start_service_parser = subparsers.add_parser('code_server_enable_and_start_service', help='Enable and start Code Server service')
    # code_server_disable_and_stop_service
    code_server_disable_and_stop_service_parser = subparsers.add_parser('code_server_disable_and_stop_service', help='Disable and stop Code Server service')
    # code_server_show_password
    code_server_show_password_parser = subparsers.add_parser('code_server_show_password', help='Show Code Server password')
    # code_server_set_password
    code_server_set_password_parser = subparsers.add_parser('code_server_set_password', help='Set Code Server password')
    code_server_set_password_parser.add_argument('--password', type=str, help='New password for Code Server')

    args = parser.parse_args()

    if args.command:
        function_id = args.command
        input_data = {}
        if hasattr(args, 'share_name') and args.share_name:
            input_data['share_name'] = args.share_name
        if hasattr(args, 'share_path') and args.share_path:
            input_data['share_path'] = args.share_path
        if hasattr(args, 'password') and args.password:
            input_data['password'] = args.password
        
        captured_output = execute_function(function_id, input_data=input_data)
        print(captured_output)
    else:
        # 引数がなければ、メニューを表示
        selected_function_id = curses.wrapper(show_menu)
        if selected_function_id:
            captured_output = execute_function(selected_function_id, input_data=None)
            print(captured_output)

def show_menu(stdscr):
    # cursesの初期設定
    curses.curs_set(0)
    stdscr.nodelay(0)
    stdscr.timeout(-1)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK) # 非活性項目用の色 (グレー)

    # メニューデータの読み込み
    script_dir = os.path.dirname(os.path.abspath(__file__))
    menu_yaml_path = os.path.join(script_dir, "menu.yaml")
    with open(menu_yaml_path, "r", encoding="utf-8") as f:
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
            status = get_menu_item_status(item.get('id')) # メニュー項目の状態を取得
            display_text = f"  {item['title']}"
            if status['reason']:
                display_text += f" ({status['reason']})"

            if i == current_row:
                if status['active']:
                    stdscr.addstr(i + 3, 0, f"> {display_text.strip()}", curses.color_pair(1))
                else:
                    stdscr.addstr(i + 3, 0, f"> {display_text.strip()}", curses.color_pair(2) | curses.A_DIM)
            else:
                if status['active']:
                    stdscr.addstr(i + 3, 0, f"  {display_text.strip()}")
                else:
                    stdscr.addstr(i + 3, 0, f"  {display_text.strip()}", curses.color_pair(2) | curses.A_DIM)
        
        # 説明の表示
        description = current_menu_items[current_row].get('description', '')
        status = get_menu_item_status(current_menu_items[current_row].get('id'))
        if status['reason']:
            description += f" (状態: {status['reason']})"
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
            status = get_menu_item_status(selected_item.get('id'))
            if not status['active']:
                continue # 非活性な項目は選択できない

            if "items" in selected_item:
                # サブメニューに移動
                title_stack.append(selected_item["title"])
                menu_stack.append(selected_item["items"])
                row_stack.append(0)
            elif "id" in selected_item:
                # 実行するIDを返す
                return selected_item["id"]
        elif key == 27: # ESCキー
            if len(menu_stack) > 0:
                # 親メニューに戻る
                current_menu_items = menu_stack.pop()
                current_row = row_stack.pop()
                title_stack.pop()
            else:
                # ルートメニューでESCなら終了
                return None


def get_menu_item_status(item_id):
    """メニュー項目の活性・非活性状態を判断する"""
    status = {'active': True, 'reason': ''}

    if item_id == "install_ms_edit":
        if is_command_available("edit"): # editコマンドが既に存在すれば非活性
            status = {'active': False, 'reason': 'インストール済み'}
    elif item_id == "install_gh":
        if is_command_available("gh"): # ghコマンドが既に存在すれば非活性
            status = {'active': False, 'reason': 'インストール済み'}
    elif item_id == "install_vscode_desktop":
        if is_command_available("code"): # codeコマンドが既に存在すれば非活性
            status = {'active': False, 'reason': 'インストール済み'}
    elif item_id == "install_code_server":
        if is_command_available("code-server"): # code-serverコマンドが既に存在すれば非活性
            status = {'active': False, 'reason': 'インストール済み'}
    elif item_id == "start_vscode_web_server_background":
        if not is_command_available("code"): # codeコマンドがなければ非活性
            status = {'active': False, 'reason': 'VS Code (Desktop) が未インストール'}
        elif is_process_running("code serve-web"): # 既に実行中なら非活性
            status = {'active': False, 'reason': '既に実行中'}
    elif item_id == "get_vscode_web_server_url":
        if not is_process_running("code serve-web"): # 実行中でなければ非活性
            status = {'active': False, 'reason': 'VS Code Webサーバーが未起動'}
    elif item_id == "stop_vscode_web_server":
        if not is_process_running("code serve-web"): # 実行中でなければ非活性
            status = {'active': False, 'reason': 'VS Code Webサーバーが未起動'}
    elif item_id == "samba_install_and_share":
        if is_package_installed("samba"): # Sambaがインストール済みなら非活性
            status = {'active': False, 'reason': 'Sambaインストール済み'}
    elif item_id == "samba_delete_share":
        if not is_package_installed("samba"): # Sambaが未インストールなら非活性
            status = {'active': False, 'reason': 'Sambaが未インストール'}

    # 他のメニュー項目に対するロジックを追加

    return status


def execute_function(function_id, input_data=None):
    # 標準出力をキャプチャするための設定
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    try:
        if function_id == "system_update":
            print("システムアップデートを実行します...")
            try:
                result = subprocess.run("sudo apt update && sudo apt upgrade -y", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("システムアップデートが完了しました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
        elif function_id == "ufw_allow_8080":
            print("8080ポートを開放します...")
            try:
                result = subprocess.run("sudo ufw allow 8080/tcp", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("8080ポートが開放されました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
        elif function_id == "ufw_deny_8080":
            print("8080ポートを閉じます...")
            try:
                result = subprocess.run("sudo ufw deny 8080/tcp", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("8080ポートが閉じられました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
        elif function_id == "ufw_allow_8000":
            print("8000ポートを開放します...")
            try:
                result = subprocess.run("sudo ufw allow 8000/tcp", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("8000ポートが開放されました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
        elif function_id == "ufw_deny_8000":
            print("8000ポートを閉じます...")
            try:
                result = subprocess.run("sudo ufw deny 8000/tcp", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("8000ポートが閉じられました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
        elif function_id == "ufw_status":
            print("ファイアウォールステータスを表示します...")
            try:
                result = subprocess.run("sudo ufw status", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")

        elif function_id == "samba_install_and_share":
            print("Sambaのインストールと共有設定を開始します...")
            try:
                result = subprocess.run("dpkg -l | grep samba", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("Sambaは既にインストールされています。")
            except subprocess.CalledProcessError:
                print("Sambaをインストールします...")
                try:
                    result = subprocess.run("sudo apt update && sudo apt install -y samba", shell=True, check=True, capture_output=True, text=True)
                    print(result.stdout)
                except subprocess.CalledProcessError as e:
                    print(f"エラー: Sambaのインストールに失敗しました: {e}")
                    print(f"標準出力: {e.stdout}")
                    print(f"標準エラー: {e.stderr}")

            # 共有フォルダのパスをinput_dataから取得
            share_path = input_data.get("share_path") if input_data else None

            if not share_path:
                share_path = input("共有したいフォルダのフルパスを入力してください: ")

            if not share_path:
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
                # sudo を使って書き込むために、teeコマンドを利用
                result = subprocess.run(f'echo "{share_config}" | sudo tee -a {smb_conf_path}', shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("設定を追記しました。")

                # Sambaサービスを再起動
                result = subprocess.run("sudo systemctl restart smbd", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("Sambaサービスを再起動しました。")

            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
            except Exception as e:
                print(f"エラーが発生しました: {e}")

        elif function_id == "install_ms_edit":
            print("Microsoft Editのインストールを開始します...")
            try:
                result = subprocess.run("dpkg -l | grep zstd", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
            except subprocess.CalledProcessError:
                print("zstdをインストールします...")
                try:
                    result = subprocess.run("sudo apt update && sudo apt install -y zstd", shell=True, check=True, capture_output=True, text=True)
                    print(result.stdout)
                except subprocess.CalledProcessError as e:
                    print(f"エラー: zstdのインストールに失敗しました: {e}")
                    print(f"標準出力: {e.stdout}")
                    print(f"標準エラー: {e.stderr}")
            
            try:
                # ダウンロードと展開
                download_url = "https://github.com/microsoft/edit/releases/download/v1.2.0/edit-1.2.0-x86_64-linux-gnu.tar.zst"
                file_name = download_url.split("/")[-1]
                
                print(f"{download_url} から {file_name} をダウンロードします...")
                result = subprocess.run(f"wget {download_url}", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)

                print(f"{file_name} を展開します...")
                result = subprocess.run(f"tar -I zstd -xf {file_name}", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)

                # インストール
                print("editを /usr/local/bin にインストールします...")
                result = subprocess.run("sudo mv edit /usr/local/bin/", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)

                # クリーンアップ
                print(f"{file_name} を削除します...")
                os.remove(file_name)

                print("Microsoft Editのインストールが完了しました。")

            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
            except Exception as e:
                print(f"エラーが発生しました: {e}")

        elif function_id == "install_gh":
            print("GitHub CLI (gh) のインストールを開始します...")
            try:
                # ghがインストールされているか確認
                result = subprocess.run("gh --version", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("GitHub CLIは既にインストールされています。")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("GitHub CLIをインストールします...")
                try:
                    # 公式のインストールスクリプトを実行
                    install_command = '''
                    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
                    && sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
                    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
                    && sudo apt update \
                    && sudo apt install gh -y
                    '''
                    result = subprocess.run(install_command, shell=True, check=True, capture_output=True, text=True)
                    print(result.stdout)
                    print("GitHub CLIのインストールが完了しました。")
                except subprocess.CalledProcessError as e:
                    print(f"エラー: GitHub CLIのインストールに失敗しました: {e}")
                    print(f"標準出力: {e.stdout}")
                    print(f"標準エラー: {e.stderr}")

        elif function_id == "install_vscode_desktop":
            print("Visual Studio Code (Desktop) のインストールを開始します...")
            try:
                # VS CodeのGPGキーをインポートとリポジトリの追加
                print("VS CodeのGPGキーをインポートし、リポジトリを追加しています...")
                # GPGキーのインポート
                result = subprocess.run("curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(f"標準エラー: {result.stderr}")

                # リポジトリの追加
                result = subprocess.run("echo \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(f"標準エラー: {result.stderr}")

                # パッケージリストを更新してVS Codeをインストール
                print("パッケージリストを更新しています...")
                result = subprocess.run("sudo apt update", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(f"標準エラー: {result.stderr}")

                print("VS Codeをインストールしています...")
                result = subprocess.run("sudo apt install -y code", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(f"標準エラー: {result.stderr}")

                print("Visual Studio Code (Desktop) のインストールが完了しました。")
            except subprocess.CalledProcessError as e:
                print(f"エラー: Visual Studio Code (Desktop) のインストールに失敗しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {e}")

        elif function_id == "install_code_server":
            print("Code Serverのインストールを開始します...")
            try:
                # code-serverがインストールされているか確認
                result = subprocess.run("code-server --version", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("Code Serverは既にインストールされています。")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Code Serverをインストールします...")
                try:
                    # 公式のインストールスクリプトを実行
                    install_command = '''
                    curl -fsSL https://code-server.dev/install.sh | sh
                    '''
                    result = subprocess.run(install_command, shell=True, check=True, capture_output=True, text=True)
                    print(result.stdout)
                    print("Code Serverのインストールが完了しました。")
                except subprocess.CalledProcessError as e:
                    print(f"エラー: Code Serverのインストールに失敗しました: {e}")
                    print(f"標準出力: {e.stdout}")
                    print(f"標準エラー: {e.stderr}")

        elif function_id == "install_vscode_remote_server_deps":
            print("VS Code Remote - SSH Serverの依存関係をインストールします...")
            packages = ["curl", "wget", "tar", "gzip", "rsync", "python3"]
            missing_packages = []
            for pkg in packages:
                try:
                    subprocess.run(f"which {pkg}", shell=True, check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    missing_packages.append(pkg)
            
            if missing_packages:
                print(f"以下のパッケージをインストールします: {', '.join(missing_packages)}")
                try:
                    result = subprocess.run(f"sudo apt update && sudo apt install -y {' '.join(missing_packages)}", shell=True, check=True, capture_output=True, text=True)
                    print(result.stdout)
                    print("依存関係のインストールが完了しました。")
                except subprocess.CalledProcessError as e:
                    print(f"エラー: 依存関係のインストールに失敗しました: {e}")
                    print(f"標準出力: {e.stdout}")
                    print(f"標準エラー: {e.stderr}")
            else:
                print("必要な依存関係はすべてインストールされています。")
            print("これで、ローカルのVS CodeからSSH接続を試みてください。VS Codeが自動的にリモートサーバーにVS Code Serverをインストールします。")

        elif function_id == "samba_delete_share":
            # Webから呼び出す場合はinput_dataに削除する共有名が含まれる
            share_name_to_delete = input_data.get("share_name") if input_data else None
            if share_name_to_delete:
                delete_samba_share(share_name_to_delete)
            else:
                # CLIから呼び出す場合、cursesで選択メニューを表示
                shares = get_samba_shares()
                if not shares:
                    print("共有が見つかりません。")
                    return
                
                # cursesで選択メニューを表示
                try:
                    selected_share_name = curses.wrapper(select_share_menu, shares)
                    if selected_share_name:
                        delete_samba_share(selected_share_name)
                    else:
                        print("共有の選択がキャンセルされました。")
                except Exception as e:
                    print(f"エラー: 共有選択メニューの表示に失敗しました: {e}")
                    print("CLIから実行する場合は、`menu.py samba_delete_share --share_name <共有名>` のように指定してください。")
        elif function_id == "screen_start":
            print("新しいScreenセッションを開始します...")
            try:
                # screen -S <セッション名> で新しいセッションを開始
                # セッション名は適当に 'my_session' とする
                result = subprocess.run("screen -S my_session", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("Screenセッションが開始されました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
        elif function_id == "screen_resume":
            print("Screenセッションを再開します...")
            try:
                # screen -r で既存のセッションを再開
                # 複数のセッションがある場合は、リストが表示され選択を促される
                result = subprocess.run("screen -r", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("Screenセッションを再開しました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
        elif function_id == "start_vscode_web_server_background":
            print("VS Code Webサーバーをバックグラウンドで起動します...")
            log_file_path = "/tmp/vscode_web_server.log"
            try:
                # 既存のプロセスを終了 (念のため)
                subprocess.run("pkill -f 'code serve-web'", shell=True, capture_output=True, text=True)
                # ログファイルも削除
                if os.path.exists(log_file_path):
                    os.remove(log_file_path)

                # rootユーザーとしてcode serve-webをバックグラウンドで実行し、ログをファイルにリダイレクト
                command = f"nohup code serve-web --host 0.0.0.0 --server-data-dir /root/.vscode-server-data > {log_file_path} 2>&1 &"
                subprocess.run(command, shell=True, check=True)

                print("サーバーの起動を待っています...")
                # サーバーがURLをログに出力するまで最大10秒待機
                for _ in range(10):
                    time.sleep(1)
                    if os.path.exists(log_file_path):
                        with open(log_file_path, 'r') as f:
                            if "Web UI available at" in f.read():
                                print("VS Code Webサーバーが起動しました。")
                                print(f"ログは {log_file_path} を確認してください。")
                                print("メニューからURLを取得してください。")
                                return # 正常に起動したら関数を抜ける
                
                print("サーバーの起動がタイムアウトしました。ログファイルを確認してください。")

            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {e}")
        elif function_id == "get_vscode_web_server_url":
            print("VS Code WebサーバーのURLを取得します...")
            log_file_path = "/tmp/vscode_web_server.log"
            try:
                if os.path.exists(log_file_path):
                    with open(log_file_path, 'r') as f:
                        log_content = f.read()
                        match = re.search(r"Web UI available at (http://[0-9a-fA-F\.:]+:[0-9]+\?tkn=[a-f0-9-]+)", log_content)
                        if match:
                            base_url = match.group(1) # 例: http://0.0.0.0:8000?tkn=...

                            # IPv4アドレスを取得
                            ip_output = subprocess.run("ip a", shell=True, capture_output=True, text=True, check=True).stdout
                            ipv4_addresses = re.findall(r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/\d+", ip_output)

                            # ループバックアドレスを除外
                            ipv4_addresses = [ip for ip in ipv4_addresses if ip != "127.0.0.1"]

                            if ipv4_addresses:
                                print("アクセスURL:")
                                for ip in ipv4_addresses:
                                    # 0.0.0.0 を実際のIPアドレスに置き換える
                                    display_url = base_url.replace("0.0.0.0", ip)
                                    print(f"  - {display_url}")
                            else:
                                print("IPv4アドレスを検出できませんでした。")
                                print(f"ベースURL: {base_url}") # デバッグ用にベースURLも表示
                        else:
                            print("アクセスURLを検出できませんでした。ログファイルを確認してください。")
                else:
                    print("ログファイルが見つかりません。VS Code Webサーバーが起動しているか確認してください。")
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {e}")
        elif function_id == "stop_vscode_web_server":
            print("VS Code Webサーバーを停止します...")
            try:
                result = subprocess.run("pkill -f 'code serve-web'", shell=True, capture_output=True, text=True)
                if result.returncode == 0 or result.returncode == -15:
                    print("VS Code Webサーバーを停止しました。")
                elif result.returncode == 1: # pkill returns 1 if no processes were matched
                    print("VS Code Webサーバーは実行されていませんでした。")
                else:
                    print(f"VS Code Webサーバーの停止中に予期せぬエラーが発生しました。終了コード: {result.returncode}")
                    print(f"標準出力: {result.stdout}")
                    print(f"標準エラー: {result.stderr}")
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                print(f"詳細: {e}")
        elif function_id == "show_vscode_web_server_log":
            print("VS Code Webサーバーのログを表示します...")
            log_file_path = "/tmp/vscode_web_server.log"
            try:
                if os.path.exists(log_file_path):
                    with open(log_file_path, 'r') as f:
                        print(f.read())
                else:
                    print("ログファイルが見つかりません。")
            except Exception as e:
                print(f"エラーが発生しました: {e}")
        elif function_id == "code_server_start_manual":
            print("Code Serverを手動で起動します... (Ctrl+Cで終了)")
            try:
                result = subprocess.run("code-server --bind-addr 0.0.0.0:8080", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
        elif function_id == "code_server_enable_and_start_service":
            print("Code Serverをサービスとして登録し起動します...")
            try:
                # 実行ユーザーの特定 (sudoの場合も考慮)
                current_user = os.environ.get('SUDO_USER') or os.getlogin()
                
                # ユーザーのsystemdサービスファイルパス
                user_service_dir = os.path.expanduser(f"~{current_user}/.config/systemd/user")
                user_service_file = os.path.join(user_service_dir, "code-server.service")

                # システムサービスファイルパス
                system_service_file = "/etc/systemd/system/code-server.service"

                if not os.path.exists(user_service_file):
                    print(f"エラー: Code Serverのユーザーサービスファイルが見つかりません: {user_service_file}")
                    print("Code Serverが正しくインストールされているか確認してください。")
                    return

                # ユーザーサービスファイルを読み込み、User/Groupを設定してシステムサービスとしてコピー
                with open(user_service_file, 'r') as f:
                    service_content = f.read()

                # User=%i と Group=%i を実際のユーザー名に置き換える
                # %i はインスタンス名 (ユーザー名) に置き換えられるが、システムサービスでは明示的に指定
                service_content = service_content.replace("User=%i", f"User={current_user}")
                service_content = service_content.replace("Group=%i", f"Group={current_user}")

                # システムサービスとして書き込み
                with open("/tmp/code-server.service.tmp", "w") as f:
                    f.write(service_content)
                subprocess.run(f"sudo mv /tmp/code-server.service.tmp {system_service_file}", shell=True, check=True)
                print(f"Code Serverサービスファイルを {system_service_file} にコピーしました。")

                # systemdデーモンをリロード
                subprocess.run("sudo systemctl daemon-reload", shell=True, check=True)
                print("systemdデーモンをリロードしました。")

                # サービスを有効化して起動
                subprocess.run("sudo systemctl enable --now code-server", shell=True, check=True)
                print("Code Serverサービスが登録され、起動しました。")

            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}\n標準エラー: {e.stderr}")
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {e}")
        elif function_id == "code_server_disable_and_stop_service":
            print("Code Serverサービスを停止し削除します...")
            try:
                current_user = os.getlogin() # 現在のユーザー名を取得
                result = subprocess.run(f"sudo systemctl disable --now code-server@{current_user}", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print("Code Serverサービスが停止され、登録解除されました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
        elif function_id == "code_server_show_password":
            print("Code Serverのパスワードを表示します...")
            try:
                config_path = "/root/.config/code-server/config.yaml"
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        config = yaml.safe_load(f)
                        if "password" in config:
                            print(f"現在のパスワード: {config['password']}")
                        else:
                            print("config.yamlにパスワードが設定されていません。")
                else:
                    print("config.yamlが見つかりません。Code Serverがインストールされていないか、設定ファイルが作成されていません。")
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                print(f"詳細: {e}")
        elif function_id == "code_server_set_password":
            print("Code Serverのパスワードを設定します...")
            try:
                # config_path を動的に取得
                # os.path.expanduser('~') は、スクリプトを実行しているユーザーのホームディレクトリを返す
                # sudo で実行している場合は /root を返す
                config_dir = os.path.join(os.path.expanduser("~"), ".config", "code-server")
                config_path = os.path.join(config_dir, "config.yaml")

                # ディレクトリが存在しない場合は作成
                if not os.path.exists(config_dir):
                    os.makedirs(config_dir, exist_ok=True)
                    print(f"設定ディレクトリを作成しました: {config_dir}")

                # config.yaml が存在しない場合は空のファイルを作成
                if not os.path.exists(config_path):
                    with open(config_path, "w") as f:
                        yaml.safe_dump({}, f) # 空のYAMLファイルを作成
                    print(f"設定ファイルを作成しました: {config_path}")

                new_password = input_data.get("password") if input_data and "password" in input_data else None
                if not new_password:
                    new_password = input("新しいパスワードを入力してください: ")

                with open(config_path, "r") as f:
                    config = yaml.safe_load(f) or {} # ファイルが空の場合に備えて空の辞書をデフォルトにする
                config["password"] = new_password
                with open(config_path, "w") as f:
                    yaml.safe_dump(config, f)
                print("パスワードを設定しました。Code Serverを再起動してください。")
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                print(f"詳細: {e}")
        elif function_id == "webmenu_reset_password":
            print("Webメニューのパスワードをリセットします...")
            try:
                web_password_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.webmenu_password')
                if os.path.exists(web_password_file):
                    os.remove(web_password_file)
                    print("Webメニューのパスワードがリセットされました。次回Webメニュー起動時に新しいパスワードを設定してください。")
                else:
                    print("Webメニューのパスワードファイルが見つかりません。")
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                print(f"詳細: {e}")
        else:
            print(f"未定義の機能IDです: {function_id}")

    finally:
        # 標準出力を元に戻す
        sys.stdout = old_stdout
    
    return redirected_output.getvalue() # キャプチャした出力を返す


def get_samba_shares():
    """smb.confから共有設定のリストを取得する（curses非依存）"""
    smb_conf_path = "/etc/samba/smb.conf"
    shares = []
    try:
        with open(smb_conf_path, "r") as f:
            content = f.read()
        
        # 正規表現で共有セクションを抽出
        # [share_name]形式のセクション名をキャプチャする
        # ただし、[global]や[printers]などは除外
        share_sections = re.findall(r"^\s*\[((?!global|printers|print\$)[^\]]+)\]", content, re.MULTILINE)
        
        for share_name in share_sections:
            shares.append({"name": share_name})
            
        return shares

    except FileNotFoundError:
        return [] # ファイルが見つからない場合は空リストを返す
    except Exception as e:
        print(f"Samba共有の読み込み中にエラーが発生しました: {e}")
        return []

def delete_samba_share(share_name_to_delete):
    smb_conf_path = "/etc/samba/smb.conf"
    
    try:
        with open(smb_conf_path, "r") as f:
            content = f.read()

        # 正規表現で指定された共有セクションを検索
        # セクションの開始から次のセクションの開始までをマッチさせる
        pattern = re.compile(r"^\s*\[" + re.escape(share_name_to_delete) + r"\](.*?)(?=\n^\s*\[|$)", re.DOTALL | re.MULTILINE)
        
        match = pattern.search(content)

        if match:
            print(f"共有 '{share_name_to_delete}' を削除します。")

            # マッチした部分を空文字列に置換
            new_content = pattern.sub("", content)

            # smb.confを上書き
            with open("/tmp/smb.conf.tmp", "w") as f:
                f.write(new_content)
            
            subprocess.run(f'sudo mv /tmp/smb.conf.tmp {smb_conf_path}', shell=True, check=True)
            print("smb.confから共有設定を削除しました。")

            # Sambaサービスを再起動
            print("Sambaサービスを再起動します...")
            subprocess.run("sudo systemctl restart smbd", shell=True, check=True)
            print("Sambaサービスを再起動しました。")
        else:
            print(f"エラー: 指定された共有 '{share_name_to_delete}' が見つかりませんでした。")

    except FileNotFoundError:
        print(f"エラー: {smb_conf_path} が見つかりません。Sambaがインストールされていない可能性があります。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")



if __name__ == "__main__":
    main()