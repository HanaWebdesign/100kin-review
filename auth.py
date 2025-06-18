from flask import Blueprint, render_template, request, redirect, session
import os, json
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)
USER_FILE = 'users.json'

# ユーザーデータ読み込み（空ファイルも対応）
if os.path.exists(USER_FILE) and os.path.getsize(USER_FILE) > 0:
    with open(USER_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
else:
    users = {}

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        user_id = request.form['user_id']
        email = request.form['email']
        password = request.form['password']

        if user_id in users:
            error = "そのユーザーIDはすでに使われています"
        else:
            users[user_id] = {
                'email': email,
                'password': generate_password_hash(password)
            }
            with open(USER_FILE, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            session['user_id'] = user_id
            return redirect('/')

    return render_template('register.html', error=error)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        if user_id in users and check_password_hash(users[user_id]['password'], password):
            session['user_id'] = user_id
            return redirect('/')
        error = 'ログイン情報が正しくありません。'

    return render_template('login.html', error=error)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
