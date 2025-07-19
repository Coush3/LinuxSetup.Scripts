## 作業経緯

- `menu.py` が壊れていたため、以下の修正を実施。
    - 重複していた `execute_function` を統合。
    - `show_menu` のサブメニュー遷移のロジックを修正。
    - `get_samba_shares` のロジックを正規表現に修正。
    - `samba_delete_share` から `curses` への依存を削除。
    - 不要な `select_share_menu` 関数を削除。
- VS Code Webサーバーのプロセスチェックが正しく機能していなかった問題を修正 (`is_process_running`)。
- VS Code Webサーバー起動直後にURL取得ができない問題を、待機処理を追加して修正。
- 「VS Code Webサーバーのログを表示」メニューを追加。
- 非活性メニュー項目の表示が明るすぎたため、背景を黒、文字をグレーに変更。
- `webmenu.py` にも非活性化の処理を追加。
- `setup.sh` に、ホームディレクトリへ `menu`、`webmenu`、`pull` の実行可能ファイルを作成する機能を追加。作成前にはプロンプトで確認。
- `readme.md` に、インストールコマンドを1行にまとめた例と、`chmod +x setup.sh` の手順を追加。
- ホームディレクトリに作成したスクリプトが、`menu.py` などの実体パスを正しく解決できない問題を修正 (`readlink -f` を使用)。
- `menu.py` が `menu.yaml` を見つけられない問題を修正（相対パスから絶対パスへ）。
- `webmenu.py` が `menu.yaml` を見つけられない問題を修正（相対パスから絶対パスへ）。
- `webmenu` から「Code Serverパスワード設定」を行う際に、パスワード入力欄が表示されない問題を修正。
- `webmenu` から「Code Serverをサービスとして登録し起動」を実行した際に `通信エラー: Unexpected token '<', "<!DOCTYPE "... is not valid JSON` と表示される問題に対応するため、`menu.py` の `code_server_enable_and_start_service` 関数を修正し、Code Serverのサービスをシステムサービスとして適切に登録・起動するように変更。

## 残タスク

- `code_server_disable_and_stop_service` 関数も、`code_server_enable_and_start_service` と同様に、システムサービスとして適切に停止・削除するように修正する必要がある。