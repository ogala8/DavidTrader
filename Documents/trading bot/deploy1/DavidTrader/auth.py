#import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

#from david.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        error = None

        if user != 'David':
            error = 'Incorrect username or password.'
        elif password != 'Traider2023!':
            error = 'Incorrect username or password.'

        if error is None:
            session.clear()
            session['user_id'] = user
            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))