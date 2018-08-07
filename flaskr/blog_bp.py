from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth_bp import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    all_posts = db.execute('SELECT p.id, title, body, created, author_id, username'
                           ' FROM post p JOIN user u on p.author_id = u.id'
                           ' ORDER BY created DESC').fetchall()
    return render_template('blog/index.html', posts=all_posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Post title is required.'

        if error is None:
            db = get_db()
            db.execute('INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)',
                       (title, body, g.user['id']))
            db.commit()
            return redirect(url_for('index'))

        flash(error)

    return render_template('blog/create.html', )


# The name inside the <> has to match the method argument in order for flask to pass the URL value as the arg. If you
# don't specify int here, the arg will be passed as a string
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Post title is required.'

        if error is None:
            db = get_db()
            db.execute('UPDATE post SET title = ?, body = ? WHERE id = ?',
                       (title, body, id))
            db.commit()
            return redirect(url_for('index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)  # checks that the post exists and the user owns it
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))


def get_post(post_id, require_authorship=True):
    post = get_db().execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
    if post is None:
        abort(404, 'Post id {} does not exist.'.format(post_id))
    if require_authorship and post['author_id'] != g.user['id']:
        abort(403)
    return post
