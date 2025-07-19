from flask import Flask, render_template, jsonify, request
import yaml
import sys
import os
import socket # 追加

# menu.py から execute_function をインポート
# sys.path に現在のディレクトリを追加して、menu.py をモジュールとして認識させる
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from menu import execute_function, get_samba_shares

app = Flask(__name__)

# menu.yaml を読み込む関数
def load_menu_data():
    with open("menu.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@app.route('/')
def index():
    hostname = socket.gethostname() # ホスト名を取得
    return render_template('index.html', hostname=hostname) # テンプレートにホスト名を渡す

@app.route('/api/menu')
def get_menu():
    menu_data = load_menu_data()
    return jsonify(menu_data)

@app.route('/api/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    function_id = data.get('function_id')
    input_data = data.get('input_data', {})

    if not function_id:
        return jsonify({'error': 'function_id is required'}), 400

    # execute_function を呼び出し、出力をキャプチャ
    output = execute_function(function_id, input_data)
    return jsonify({'output': output})

@app.route('/api/samba_shares')
def get_samba_shares_api():
    shares = get_samba_shares()
    return jsonify(shares)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)