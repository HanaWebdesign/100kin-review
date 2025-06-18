from flask import Flask
from auth import auth_bp
from review import review_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 適当な文字列に変えてね

app.register_blueprint(auth_bp)
app.register_blueprint(review_bp)

if __name__ == '__main__':
    app.run(debug=True)
    from auth import auth_bp

    