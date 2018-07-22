# This file establishes functions for the database
# web applications usually create a connection tied to a request, make changes, then close the connection before the response
# is sent

#SQLite is slow with concurrent requests as it is sequential

import sqlite3

import click #for command line Flask stuff
from flask import current_app, g
from flask.cli import with_appcontext

# current_app is a special object that points to the Flask app handling the request
# this is because you make and return your application in the "application factory"
# so there is no global reference to your application and you must access it using
# current_app

def get_db():
    # g is a special object unqiue to each request
    # it stores data that might be used by multiple functions
    # during the request. The connection is stored and reused instead
    # of making a new connection if get_db is called again during
    # the same request

    if 'db' not in g:
        #uses the location of the database that we chose in the __init__.py file
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES

        )
        g.db.row_factory = sqlite3.Row #return rows that behave like dictionaries

    # returns the database already in 'g', or puts one in there first
    # this way you only make a connection once
    return g.db

def close_db(e=None):
    db = g.pop('db', None) #remove the database from g when finished

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    # open_resource() opens a file relative to the mysite package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

#click command defines the command line called 'init-db' that calls the
#init_db function
@click.command('init-db')
@with_appcontext
def init_db_command():
    '''Clear the exisitng data and create new tables.'''
    init_db()
    click.echo('Initialized the database.')


#we need to register the close_db and init_db_command function
#with our application instance or they wont be used by it

def init_app(app):
    #tells your app what to do when cleaning up after returning the response
    app.teardown_appcontext(close_db) 

    #adds a new command that can be called with the 'flask' command
    app.cli.add_command(init_db_command)


#now we need to import this function and call it within the app factory
# put this code at the end of the factory before returning the app
