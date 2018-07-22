#The __init__.py file tells python that the "mysite" directory should be treated as a package

import os
from flask import Flask

# This is the "application factory"
def create_app(test_config=None):
    # Create and configure the app
    # Pass the __name__ variable to tell flask where this module is located
    # instance_relative_config says configuration files are relative to the instance folder
    # the instance folder is located outside the mysite package and shouldn't be committed to version control
    app = Flask(__name__, instance_relative_config=True)
    
    # secret key should be changed to a random value when deploying
    # database is the path where SQLite database will be saved
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'mysite.sqlite'),
    )

    # overwrites the default config if you provide one
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed as a variable
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    # Flask doesn't automatically make the instance folder so we need to check to ensure it is there
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    # when someone does a GET request to "/hello" return this
    @app.route('/hello')
    def hello():
        return "Hello and welcome to Nick Dima's Site!"

    #registers some functions with our app
    #the import . tells python to search the current package first
    #incase there is a duplicate named package elsewhere in PATH
    from . import db
    db.init_app(app)

    #need to register all blueprints to the app
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app

#flask init-db command line will add a mysite.sqlite file to the instance folder
