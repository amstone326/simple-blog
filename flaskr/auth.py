import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# creates a Blueprint named 'auth', and the given url_prefix will be prepended to all URLs associated with the blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')


# Note: The url_for() function generates the URL to a view based on a name and arguments. The name associated with a
# view is, by default, the name of the view function. E.g. the hello() view can be linked to with  url_for('hello').
# If it took an argument, it would be linked to using url_for('hello', who='World'). When using a blueprint, the name
# of the blueprint is prepended to the name of the function, so the endpoint for the  login() view is 'auth.login'.


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


# this URL is really '/auth/register', see above
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone() is not None:
            error = 'User {} is already registered'.format(username)

        if error is None:
            db.execute('INSERT INTO user (username, password) VALUES (?, ?)',
                       (username, generate_password_hash(password))
            )
            db.commit()
            # redirect to login if registration succeeded
            return redirect(url_for('auth.login'))

        # stores the error message such that it can be retrieved when rendering the template
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute('SELECT * FROM user WHERE username=?', (username,)).fetchone()
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
