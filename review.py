import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from datetime import datetime

review_bp = Blueprint('review', __name__)

REVIEW_FILE = 'reviews.json'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_reviews():
    if not os.path.exists(REVIEW_FILE):
        return []
    with open(REVIEW_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_reviews(reviews):
    with open(REVIEW_FILE, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

def get_today_string():
    return datetime.now().strftime("%Y-%m-%d")

@review_bp.route('/', methods=['GET', 'POST'])
def index():
    reviews = load_reviews()
    user = session.get('user_id')

    # 検索処理
    query = request.args.get("q", "").strip()
    if query:
        reviews = [
    r for r in reviews
    if query.lower() in (r.get("item") or "").lower()
    or query.lower() in (r.get("comment") or "").lower()
]
    # 投稿処理
    if request.method == 'POST':
        file = request.files.get('image')
        image_path = None
        if file and allowed_file(file.filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = f"uploads/{filename}".replace("\\", "/")

        new_review = {
            "user": session.get("user_name", "名無し"),  # 仮に名前も保存してるなら
            "user_id": session.get("user_id", "unknown"),
            "item": request.form.get("item"),
            "maker": request.form.get("maker"),
            "rating": request.form.get("rating"),
            "comment": request.form.get("comment"),
            "date": get_today_string(),
            "image_path": image_path,
            "likes": 0,
            "reported": False  # ←初期状態では通報されてない
        }

        reviews.append(new_review)
        save_reviews(reviews)
        return redirect(url_for('review.index'))
# 投稿後リダイレクト

    return render_template('index.html', reviews=reviews, user=user, request=request)  # GETのときだけテンプレート表示

@review_bp.route('/like', methods=['POST'])
def like_review():
    index = int(request.form.get("index"))
    reviews = load_reviews()

    # セッションに「いいね済みリスト」がなければ作る
    if "liked_reviews" not in session:
        session["liked_reviews"] = []

    # すでに押していたらスキップ
    if index in session["liked_reviews"]:
        return redirect(url_for('review.index'))

    # まだ押してなければ処理続行
    if 0 <= index < len(reviews):
        reviews[index]["likes"] = reviews[index].get("likes", 0) + 1
        save_reviews(reviews)

        # セッションに追加
        session["liked_reviews"].append(index)
        session.modified = True  # セッション更新を明示

    return redirect(url_for('review.index'))

@review_bp.route('/report', methods=['POST'])
def report_review():
    index = int(request.form.get("index"))
    reviews = load_reviews()
    if 0 <= index < len(reviews):
        reviews[index]["reported"] = True
        save_reviews(reviews)
    return redirect(url_for('review.index'))