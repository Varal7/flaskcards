from flask import Flask, render_template, redirect, url_for, abort, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask import request
from app.utils import login_required
import enum
import datetime
import random
from flask import current_app
import hashlib


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

    return render_template(
            "index.html",
            name=name,
            me=me,
    )

def hash_fn(v):
    m = hashlib.sha256()
    m.update(v.encode())
    return m.hexdigest()


@app.route("/game")
@login_required
def game():
    cards = Card.query.all()
    card = random.choice(cards)
    now = str(datetime.datetime.now().timestamp())
    hash = hash_fn(now + str(card.id) + current_app.config['SECRET_KEY'])

    return render_template("game.html", card=card, now=now, hash=hash)

@app.route("/guess", methods=['POST'])
@login_required
def guess():
    email = session.get('email')
    me = User.query.filter_by(email=email).first()

    guess = request.form['guess']

    card_id = int(request.form['card_id'])
    now = request.form['now']
    hash = hash_fn(now + str(card_id) + current_app.config['SECRET_KEY'])
    if hash != request.form['hash']:
        abort(400, "Hash not matching")

    then = datetime.datetime.fromtimestamp(float(now))
    now = datetime.datetime.now()
    time_spent_in_ms = int((now - then).total_seconds() * 1000)

    card = Card.query.get(card_id)
    if not card:
        abort(400, "Could not find card")

    correct = card.first_name.lower() == guess.lower()

    trial = Trial(user_id=me.id,
                    card_id=card_id,
                    correct=correct,
                    time_spent_in_ms=time_spent_in_ms,
                    guess=guess[:79],
                    trial_type=TrialTypeEnum.first_name
    )

    db.session.add(trial)
    db.session.commit()

    return redirect(url_for('result', trial_id=trial.id))

@app.route("/result/<trial_id>")
@login_required
def result(trial_id):
    email = session.get('email')
    me = User.query.filter_by(email=email).first()
    trial = Trial.query.get(trial_id)

    if trial.user_id != me.id:
        abort(403, "Forbidden: Not your trial")

    card = Card.query.get(trial.card_id)

    return render_template(
            "result.html",
            trial=trial,
            card=card
    )


@app.route("/show_card/<card_id>")
@login_required
def show_card(card_id):
    card = Card.query.get(card_id)
    filename = "faces/" + card.filename

    return render_template(
            "card.html",
            filename=filename,
            name=card.name,
    )

def init_user(email):
    user = User(email=email)
    db.session.add(user)
    db.session.commit()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    trials = db.relationship('Trial', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.email

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=True)
    filename = db.Column(db.String(80), nullable=False)
    trials = db.relationship('Trial', backref='carrd', lazy=True)

    def __repr__(self):
        return '<Card %r>' % self.email

    @property
    def url_filename(self):
        return "faces/" + self.filename

    @property
    def first_name(self):
        return self.name.split()[0]


class TrialTypeEnum(enum.Enum):
    first_name = 1
    full_name = 2
    autocomplete = 3

class Trial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    guess = db.Column(db.String(80), nullable=False)
    ts = db.Column(db.DateTime, default=func.now())
    time_spent_in_ms = db.Column(db.Integer, nullable=False)
    trial_type = db.Column(db.Enum(TrialTypeEnum))

    def __repr__(self):
        return '<Trial %r>' % self.email
