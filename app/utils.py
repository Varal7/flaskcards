from functools import wraps
from flask import Flask, render_template, redirect, url_for,  session

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('auth.login'))
    return wrap

