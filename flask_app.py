# flask_app.py
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/khairulrizal/mysite/comments.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))

# ── Portfolio / profile page (main landing page) ─────────────────────────────
@app.route("/")
def profile():
    return render_template("profile.html")

# ── Comments scratchpad page ──────────────────────────────────────────────────
@app.route("/scratchpad", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments=Comment.query.all())
    comment = Comment(content=request.form["contents"])
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('index'))