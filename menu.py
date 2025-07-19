import yaml
import os
import subprocess
import sys
import curses
import io # 追加

def main():
    # コマンドライン引数を確認
    if len(sys.argv) > 1:
        # 引数があれば、それを機能IDとして直接実行
        function_id = sys.argv[1]
        # CLIからの実行なので、input_dataはNone
        execute_function(function_id, input_data=None)
    else:
        # 引数がなければ、メニューを表示
        function_id = curses.wrapper(show_menu)
        if function_id:
            # CLIからの実行なので、input_dataはNone
            execute_function(function_id, input_data=None)

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


def execute_function(function_id, input_data=None):
    # 標準出力をキャプチャするための設定
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    try:
        if function_id == "system_update":
            print("システムアップデートを実行します...")
            try:
                # apt update && apt upgrade を実行
                subprocess.run("sudo apt update && sudo apt upgrade -y", shell=True, check=True)
                print("システムアップデートが完了しました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")

        elif function_id == "ufw_allow_8080":
            print("8080ポートを開放します...")
            try:
                subprocess.run("sudo ufw allow 8080/tcp", shell=True, check=True)
                print("8080ポートが開放されました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
        elif function_id == "ufw_deny_8080":
            print("8080ポートを閉じます...")
            try:
                subprocess.run("sudo ufw deny 8080/tcp", shell=True, check=True)
                print("8080ポートが閉じられました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
        elif function_id == "ufw_allow_8000":
            print("8000ポートを開放します...")
            try:
                subprocess.run("sudo ufw allow 8000/tcp", shell=True, check=True)
                print("8000ポートが開放されました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
        elif function_id == "ufw_deny_8000":
            print("8000ポートを閉じます...")
            try:
                subprocess.run("sudo ufw deny 8000/tcp", shell=True, check=True)
                print("8000ポートが閉じられました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
        elif function_id == "ufw_status":
            print("ファイアウォールステータスを表示します...")
            try:
                subprocess.run("sudo ufw status", shell=True, check=True)
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

        elif function_id == "install_gh":
            print("GitHub CLI (gh) のインストールを開始します...")
            try:
                # ghがインストールされているか確認
                subprocess.run("gh --version", shell=True, check=True, capture_output=True)
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
                    subprocess.run(install_command, shell=True, check=True)
                    print("GitHub CLIのインストールが完了しました。")
                except subprocess.CalledProcessError as e:
                    print(f"エラー: GitHub CLIのインストールに失敗しました: {e}")

        elif function_id == "install_vscode_desktop":
            print("Visual Studio Code (Desktop) のインストールを開始します...")
            try:
                # VS CodeのGPGキーをインポート
                subprocess.run("wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg", shell=True, check=True)
                subprocess.run("sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg", shell=True, check=True)
                # VS Codeのリポジトリを追加
                subprocess.run("sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'", shell=True, check=True)
                # パッケージリストを更新してVS Codeをインストール
                subprocess.run("sudo apt update && sudo apt install -y code", shell=True, check=True)
                print("Visual Studio Code (Desktop) のインストールが完了しました。")
            except subprocess.CalledProcessError as e:
                print(f"エラー: Visual Studio Code (Desktop) のインストールに失敗しました: {e}")

        elif function_id == "install_code_server":
            print("Code Serverのインストールを開始します...")
            try:
                # code-serverがインストールされているか確認
                subprocess.run("code-server --version", shell=True, check=True, capture_output=True)
                print("Code Serverは既にインストールされています。")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Code Serverをインストールします...")
                try:
                    # 公式のインストールスクリプトを実行
                    install_command = '''
                    curl -fsSL https://code-server.dev/install.sh | sh
                    '''
                    subprocess.run(install_command, shell=True, check=True)
                    print("Code Serverのインストールが完了しました。")
                except subprocess.CalledProcessError as e:
                    print(f"エラー: Code Serverのインストールに失敗しました: {e}")

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
                    subprocess.run(f"sudo apt update && sudo apt install -y {' '.join(missing_packages)}", shell=True, check=True)
                    print("依存関係のインストールが完了しました。")
                except subprocess.CalledProcessError as e:
                    print(f"エラー: 依存関係のインストールに失敗しました: {e}")
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
                subprocess.run("screen -S my_session", shell=True, check=True)
                print("Screenセッションが開始されました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
        elif function_id == "screen_resume":
            print("Screenセッションを再開します...")
            try:
                # screen -r で既存のセッションを再開
                # 複数のセッションがある場合は、リストが表示され選択を促される
                subprocess.run("screen -r", shell=True, check=True)
                print("Screenセッションを再開しました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
        elif function_id == "start_vscode_web_server":
            print("VS Code Webサーバーを起動します... (Ctrl+Cで終了)")
            try:
                subprocess.run("code serve-web --host 0.0.0.0", shell=True, check=True, capture_output=True, text=True)
                print(result.stdout)
                print(result.stderr)
                # ログからURLを抽出して表示
                import re
                match = re.search(r"Web UI available at (http://[0-9\.]+:[0-9]+/?tkn=[a-f0-9-]+)", result.stdout)
                if match:
                    print(f"アクセスURL: {match.group(1).replace('0.0.0.0', '<あなたのサーバーのIPアドレス>')}")
                else:
                    print("アクセスURLを検出できませんでした。ログを確認してください。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
                print(f"標準出力: {e.stdout}")
                print(f"標準エラー: {e.stderr}")
        elif function_id == "code_server_start_manual":
            print("Code Serverを手動で起動します... (Ctrl+Cで終了)")
            try:
                subprocess.run("code-server --bind-addr 0.0.0.0:8080", shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
        elif function_id == "code_server_enable_and_start_service":
            print("Code Serverをサービスとして登録し起動します...")
            try:
                subprocess.run("sudo systemctl enable --now code-server@$USER", shell=True, check=True)
                print("Code Serverサービスが登録され、起動しました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
        elif function_id == "code_server_disable_and_stop_service":
            print("Code Serverサービスを停止し削除します...")
            try:
                subprocess.run("sudo systemctl disable --now code-server@$USER", shell=True, check=True)
                print("Code Serverサービスが停止され、登録解除されました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")
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
        elif function_id == "code_server_set_password":
            print("Code Serverのパスワードを設定します...")
            try:
                config_path = "/root/.config/code-server/config.yaml"
                if not os.path.exists(config_path):
                    print("config.yamlが見つかりません。Code Serverがインストールされていないか、設定ファイルが作成されていません。")
                    return

                new_password = input_data.get("password") if input_data else None
                if not new_password:
                    new_password = input("新しいパスワードを入力してください: ")

                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                config["password"] = new_password
                with open(config_path, "w") as f:
                    yaml.safe_dump(config, f)
                print("パスワードを設定しました。Code Serverを再起動してください。")
            except Exception as e:
                print(f"エラーが発生しました: {e}")
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
    current_share_name = None
    share_block_start_line = -1

    try:
        with open(smb_conf_path, "r") as f:
            lines = f.readlines()

        # 共有セクションを解析
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.startswith("[") and stripped_line.endswith("]"):
                # 新しいセクションの開始
                if current_share_name:
                    # 前の共有セクションを保存
                    shares.append({
                        "name": current_share_name,
                        "start_line": share_block_start_line,
                        "end_line": i - 1 # 現在のセクションの1つ前の行が終了行
                    })
                current_share_name = stripped_line[1:-1]
                share_block_start_line = i
            elif current_share_name and i == len(lines) - 1:
                # ファイルの終わりに達した場合、最後の共有セクションを保存
                shares.append({
                    "name": current_share_name,
                    "start_line": share_block_start_line,
                    "end_line": i
                })

        # 最後の共有セクションがファイル末尾で終わる場合を考慮
        if current_share_name and not shares or (shares and shares[-1]["name"] != current_share_name):
             shares.append({
                "name": current_share_name,
                "start_line": share_block_start_line,
                "end_line": len(lines) - 1
            })

        # globalセクションを除外
        shares = [s for s in shares if s["name"].lower() != "global"]
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
            lines = f.readlines()

        shares = get_samba_shares()
        selected_share = next((s for s in shares if s["name"] == share_name_to_delete), None)

        if selected_share:
            print(f"共有 '{selected_share['name']}' を削除します。")

            # 選択された共有の行を除外して新しい内容を作成
            new_lines = []
            for i, line in enumerate(lines):
                if not (selected_share["start_line"] <= i <= selected_share["end_line"]):
                    new_lines.append(line)

            # smb.confを上書き
            # sudo権限でファイルを書き込むため、teeコマンドを使用
            temp_smb_conf_content = "".join(new_lines)
            subprocess.run(f'echo "{temp_smb_conf_content}" | sudo tee {smb_conf_path}', shell=True, check=True)
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

def select_share_menu(stdscr, shares):
    curses.curs_set(0)
    stdscr.nodelay(0)
    stdscr.timeout(-1)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    current_row = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        title = "削除するSamba共有を選択してください:"
        stdscr.addstr(0, 0, title)
        stdscr.addstr(1, 0, "=" * len(title))

        for i, share in enumerate(shares):
            display_name = share["name"]
            x = 0
            y = i + 3
            if i == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, f"> {display_name}")
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, f"  {display_name}")
        
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_row = (current_row - 1) % len(shares)
        elif key == curses.KEY_DOWN:
            current_row = (current_row + 1) % len(shares)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return shares[current_row]["name"]
        elif key == 27: # ESCキー
            return None

# select_share_menu は curses 依存のため削除

if __name__ == "__main__":
    main()