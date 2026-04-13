# flask_app.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, redirect, render_template, request, url_for
from datetime import datetime
import os

app = Flask(__name__)
app.config["DEBUG"] = True

# ── Database path ─────────────────────────────────────────────────────────────
if os.path.exists('/home/khairulrizal/mysite'):
    DB_PATH = "sqlite:////home/khairulrizal/mysite/comments.db"
else:
    DB_PATH = os.environ.get("DATABASE_URL", "sqlite:////app/instance/comments.db")

app.config["SQLALCHEMY_DATABASE_URI"] = DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ── Secret key — reads from environment, falls back to config.py ──────────────
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    try:
        from config import SECRET_KEY
        app.secret_key = SECRET_KEY
    except ImportError:
        app.secret_key = "fallback-dev-key-not-for-production"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

# ── User model ────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Comment model ─────────────────────────────────────────────────────────────
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    posted = db.Column(db.DateTime, default=datetime.now)
    commenter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    commenter = db.relationship('User', foreign_keys=commenter_id)

# Auto-create tables on startup ───────────────────────────────────────────────
with app.app_context():
    db.create_all()

# ── Portfolio / profile page (main landing page) ─────────────────────────────
@app.route("/")
def profile():
    return render_template("profile.html")

# ── Comments scratchpad page ──────────────────────────────────────────────────
@app.route("/scratchpad", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments=Comment.query.all())
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    comment = Comment(content=request.form["contents"], commenter=current_user)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('index'))

# ── Login ─────────────────────────────────────────────────────────────────────
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)
    user = User.query.filter_by(username=request.form["username"]).first()
    if user is None or not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)
    login_user(user)
    return redirect(url_for('index'))

# ── Logout ────────────────────────────────────────────────────────────────────
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

