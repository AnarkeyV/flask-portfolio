# flask_app.py
from prometheus_flask_exporter import PrometheusMetrics
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
import smtplib
from email.message import EmailMessage
from flask import request, jsonify


app = Flask(__name__)
app.config["DEBUG"] = True

# ── Prometheus Metrics ────────────────────────────────────────────────────────
metrics = PrometheusMetrics(app)

# Register a custom metric to track app info
metrics.info('app_info', 'Portfolio Application Info', version='1.0.0')

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
elif os.environ.get("WEBSITE_HOSTNAME"):
    # Azure App Service environment - use /home directory (writable)
    DB_PATH = "sqlite:////home/site/wwwroot/instance/comments.db"
    # Ensure the instance directory exists
    import os
    instance_dir = '/home/site/wwwroot/instance'
    os.makedirs(instance_dir, exist_ok=True)
elif os.environ.get("DATABASE_URL"):
    # Custom database URL from environment variable
    DB_PATH = os.environ.get("DATABASE_URL")
else:
    # Local development or other environments
    DB_PATH = "sqlite:///comments.db"

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

# ── Contact form email endpoint ───────────────────────────────────────────────
@app.route("/send_contact", methods=["POST"])
def send_contact():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()

        # Validate inputs
        if not name or not email or not message:
            return jsonify({"success": False, "error": "All fields are required"}), 400

        # Create email message
        msg = EmailMessage()
        msg.set_content(f"""
Name: {name}
Email: {email}

Message:
{message}
        """)
        msg['Subject'] = f"Portfolio Contact from {name}"
        msg['From'] = "khairul@khairulrizal.qzz.io"
        msg['To'] = "khairul@khairulrizal.qzz.io"
        msg['Reply-To'] = email

        # Send using Zoho SMTP - use environment variable for password
        ZOHO_PASSWORD = os.environ.get("ZOHO_APP_PASSWORD", "YOUR_BACKUP_PASSWORD_HERE")


        with smtplib.SMTP_SSL('smtp.zoho.com', 465) as smtp:
            smtp.login("khairul@khairulrizal.qzz.io", ZOHO_PASSWORD)
            smtp.send_message(msg)

        # Optional: Send auto-reply to the person who contacted you
        auto_reply = EmailMessage()
        auto_reply.set_content(f"""
Dear {name},

Thank you for reaching out to me. I have received your message and will get back to you within 24-48 hours.

Best regards,
Khairul Rizal
        """)
        auto_reply['Subject'] = "Thank you for contacting Khairul Rizal"
        auto_reply['From'] = "khairul@khairulrizal.qzz.io"
        auto_reply['To'] = email

        with smtplib.SMTP_SSL('smtp.zoho.com', 465) as smtp:
            smtp.login("khairul@khairulrizal.qzz.io", ZOHO_PASSWORD)
            smtp.send_message(auto_reply)

        return jsonify({"success": True, "message": "Email sent successfully"})

    except Exception as e:
        print(f"Email error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

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

# ── Health check endpoint ─────────────────────────────────────────────────────
@app.route("/health")
def health():
    from flask import jsonify
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500


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

# ── Prometheus metrics endpoint ───────────────────────────────────────────────
@app.route("/metrics")
@limiter.exempt
@metrics.do_not_track()  # Prevents metrics endpoint from tracking itself
def metrics_endpoint():
    return "Metrics available at /metrics", 200

# Auto-create tables on startup ───────────────────────────────────────────────
with app.app_context():
    db.create_all()
