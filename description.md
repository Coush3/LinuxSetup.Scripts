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

## 残タスク

- 特になし。