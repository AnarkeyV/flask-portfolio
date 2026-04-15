# flask_app.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, redirect, render_template, request, url_for
from datetime import datetime
import os
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import text
import tempfile


app = Flask(__name__)
app.config["DEBUG"] = True

# Security headers with Talisman
Talisman(app,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "cdn.jsdelivr.net", "code.jquery.com", "maxcdn.bootstrapcdn.com", "'unsafe-inline'"],
        'style-src': ["'self'", "cdn.jsdelivr.net", "fonts.googleapis.com", "maxcdn.bootstrapcdn.com", "'unsafe-inline'"],
        'font-src': ["'self'", "fonts.googleapis.com", "fonts.gstatic.com", "maxcdn.bootstrapcdn.com"],
        'img-src': ["'self'", "data:", "https:"],
    },
    force_https=False,  # Set to True once you have SSL on AWS
    force_file_save=False,
    frame_options='DENY'
)

# Rate limiting - FIXED VERSION
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
limiter.init_app(app)

# ── Database path ─────────────────────────────────────────────────────────────
if os.path.exists('/home/khairulrizal/mysite'):
    # PythonAnywhere environment
    DB_PATH = "sqlite:////home/khairulrizal/mysite/comments.db"
elif os.environ.get("GITHUB_ACTIONS") == "true":
    # GitHub Actions CI environment - use temporary directory
    temp_dir = tempfile.gettempdir()
    DB_PATH = f"sqlite:///{temp_dir}/comments.db"
elif os.environ.get("DATABASE_URL"):
    # Custom database URL from environment variable
    DB_PATH = os.environ.get("DATABASE_URL")
else:
    # Local development or other environments
    DB_PATH = "sqlite:///comments.db"

app.config["SQLALCHEMY_DATABASE_URI"] = DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ── Secret key — reads from environment, falls back to config.py ──────────────
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        # Use a dummy secret key for CI (not for production!)
        app.secret_key = "github-actions-ci-dummy-key"
    else:
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

# ── Login attempts audit log ──────────────────────────────────────────────────
class LoginAttempt(db.Model):
    __tablename__ = "login_attempts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(256))
    success = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

# Auto-create tables on startup ───────────────────────────────────────────────
with app.app_context():
    db.create_all()

# ── Health check endpoint for monitoring ──────────────────────────────────────
@app.route("/health")
def health_check():
    try:
        # Test database connection - using text() for SQLAlchemy 2.0+
        db.session.execute(text('SELECT 1'))
        db_status = "connected"
        http_status = 200
    except Exception as e:
        db_status = f"error: {str(e)}"
        http_status = 503

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "1.0.0"
    }, http_status

# ── Portfolio / profile page (main landing page) ─────────────────────────────
@app.route("/")
def profile():
    return render_template("profile.html")

# ── Comments scratchpad page ──────────────────────────────────────────────────
@app.route("/scratchpad", methods=["GET", "POST"])
@limiter.limit("10 per minute", error_message="Too many comments. Please wait a moment.")
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments=Comment.query.all())
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    comment = Comment(content=request.form["contents"], commenter=current_user)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('index'))

# ── Login with audit logging ──────────────────────────────────────────────────
@app.route("/login/", methods=["GET", "POST"])
@limiter.limit("5 per minute", error_message="Too many login attempts. Please try again later.")
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    username = request.form["username"]
    password = request.form["password"]
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')

    user = User.query.filter_by(username=username).first()
    login_success = user is not None and user.check_password(password)

    # Log the attempt
    attempt = LoginAttempt(
        username=username,
        ip_address=ip_address,
        user_agent=user_agent,
        success=login_success
    )
    db.session.add(attempt)
    db.session.commit()

    if login_success:
        login_user(user)
        return redirect(url_for('index'))
    else:
        return render_template("login_page.html", error=True)

# ── Logout ────────────────────────────────────────────────────────────────────
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

