from flask import Flask, render_template, redirect, url_for, abort, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask import request
from app.utils import login_required
import enum
import datetime

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

from app.auth.controllers import mod_auth as auth_module

app.register_blueprint(auth_module)

@app.route("/")
@login_required
def home():
    name = session.get('name')
    email = session.get('email')
    me = User.query.filter_by(email=email).first()
    if not me:
        me = init_user(email)

    today = datetime.datetime.today().strftime("%Y-%m-%d")

    return render_template(
            "index.html",
            name=name,
            me=me,
    )

def init_user(email):
    user = User(email=email)
    db.session.add(user)
    db.session.commit()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    img_url = db.Column(db.String(80), nullable=False)


    def __repr__(self):
        return '<Card %r>' % self.email
