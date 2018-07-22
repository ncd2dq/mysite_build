#a Blueprint for the authentication page code

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request,
    session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from mysite.db import get_db

#the url_prefix will be prepended to all URLs assocaited with the blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

#when someone visits /auth/register the register view will return HTML

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'

        #check to make sure there is not already a user in the database
        #before we create a new user with this username
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        #if there isn't a user of this same name, add the username and password
        #hash to our database
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            #always call commit after data is modified
            db.commit()

            #url_for generates the URL for the login view based on the name
            return redirect(url_for('auth.login'))

        #flash stores messages that can be retrieved when rendering the template
        flash(error)

    #if the method is not a POST request (i.e. it is a GET request) render the register template
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        #session is a dictionary that stores data across requests
        #when validation succeeds, the users ID is stored in the session
        #the data is stored in a cookie that is sent to the browser, and the
        #browser then sends it back with subsequent requets. Flask securely signs
        #the data so that it can't be tampered with (i.e. fake a cookie)
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# this registers a function that runs before the view function no matter
# what URL is requested
# this checks if a user id is stored in the session (and subsequently the cookie)
# and gets that users data from the database storing it in g.user, which lasts
# the length of the request
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# Clears the session so that the load_logged_in_user function sets g.user = None
# and doesn't load a user
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


#this will be used to make a decorator to check if a user is logged in
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# the url_for() function generates the URL to a view based on a name and arguments
# the name associated with a view is also called the ENDPOINT and by default
# it's the same as the name of the view function

#when using a blueprint, the name of the blueprint is prepended to the name
#of all the functions so the endpoint for the login function is 'auth.login'
#because it was added to the 'auth' blueprint