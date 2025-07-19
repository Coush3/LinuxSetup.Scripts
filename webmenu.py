from flask import Flask, render_template, jsonify, request, redirect, url_for, session, g
import yaml
import sys
import os
import socket
import hashlib
import secrets
import functools

# パスワード保存ファイル
WEB_PASSWORD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.webmenu_password')

# パスワードをハッシュ化
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# パスワードを検証
def check_password(password):
    if not os.path.exists(WEB_PASSWORD_FILE):
        return False
    with open(WEB_PASSWORD_FILE, 'r') as f:
        stored_hash = f.read().strip()
    return stored_hash == hash_password(password)

# ログインが必要なデコレータ
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# menu.py から execute_function をインポート
# sys.path に現在のディレクトリを追加して、menu.py をモジュールとして認識させる
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from menu import execute_function, get_samba_shares

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) # セッション管理のためのシークレットキー

# menu.yaml を読み込む関数
def load_menu_data():
    with open("menu.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = user_id # ユーザーがログインしていることを示す

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if check_password(password):
            session['user_id'] = 'authenticated' # ログイン成功
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid password')
    
    # 初回起動時にパスワードが設定されていない場合
    if not os.path.exists(WEB_PASSWORD_FILE):
        return render_template('login.html', setup_mode=True)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not os.path.exists(WEB_PASSWORD_FILE):
        return redirect(url_for('login'))
    if g.user is None:
        return redirect(url_for('login'))
    hostname = socket.gethostname()
    return render_template('index.html', hostname=hostname)

@app.route('/api/menu')
@login_required
def get_menu():
    menu_data = load_menu_data()
    return jsonify(menu_data)

@app.route('/api/execute', methods=['POST'])
@login_required
def execute_command():
    data = request.get_json()
    function_id = data.get('function_id')
    input_data = data.get('input_data', {})

    if not function_id:
        return jsonify({'error': 'function_id is required'}), 400

    output = execute_function(function_id, input_data)
    return jsonify({'output': output})

@app.route('/api/samba_shares')
@login_required
def get_samba_shares_api():
    shares = get_samba_shares()
    return jsonify(shares)

@app.route('/set_initial_password', methods=['POST'])
def set_initial_password():
    password = request.form['password']
    if not password:
        return render_template('login.html', setup_mode=True, error='Password cannot be empty')
    
    with open(WEB_PASSWORD_FILE, 'w') as f:
        f.write(hash_password(password))
    session['user_id'] = 'authenticated'
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)