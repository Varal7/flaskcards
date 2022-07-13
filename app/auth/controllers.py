from flask import Flask, render_template, request, redirect, url_for, abort, session, flash, Blueprint
from flask import request
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import current_app

from app.utils import login_required

mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

@mod_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("auth/login.html", client_id=current_app.config['CLIENT_ID'])
    else:
        csrf_token_cookie = request.cookies.get('g_csrf_token')
        if not csrf_token_cookie:
            abort(400, 'No CSRF token in Cookie.')
        csrf_token_body = request.form.get('g_csrf_token')
        if not csrf_token_body:
            abort(400, 'No CSRF token in post body.')
        if csrf_token_cookie != csrf_token_body:
            abort(400, 'Failed to verify double submit cookie.')

        token = request.form.get("credential")

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), current_app.config['CLIENT_ID'])
        except ValueError:
            abort(400, 'Failed to verify user.')

        email = idinfo['email']
        name = idinfo['name']

        session['logged_in'] = True
        session['email'] = email
        session['name'] = name

        return redirect(url_for('home'))

@mod_auth.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('auth.login'))
