from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from mysite.auth import login_required
from mysite.db import get_db

bp = Blueprint('blog', __name__)

# now import and register the blueprint from the factory
# unlike the auth blueprint, the blog blueprint does not have a url_prefix
# therefore the index.html will be at '/', create view at '/create' and etc.

#if the blog were not the main feature of mysite, it would have a url_prefix
#CHANGE THIS ONCE I MAKE THE BLOG A SUB PORTION OF MYSITE

'''
However, the endpoint for the index view defined below will be blog.index. 
Some of the authentication views referred to a plain index endpoint. 
app.add_url_rule() associates the endpoint name 'index' with the / url 
so that url_for('index') or url_for('blog.index') will both work, generating
 the same / URL either way.
'''

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p join user u on p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not  None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p join user u on p.author_id = u.id'
        ' WHERE p.id = ?', (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    #404 not found, 403 forbidden, 401 unauthorized
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?', (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

#the <int:id> is an argument within the URL that can be passed to our view function


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))