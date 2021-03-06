import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.set_db_ops_for_app(app)

    from . import auth_bp
    app.register_blueprint(auth_bp.bp)

    from . import blog_bp
    app.register_blueprint(blog_bp.bp)
    # works exactly the same as the @route decorator; Needed so that url_for('index') will direct to the '/' URL -
    # otherwise would have to always use url_for('blog.index')
    app.add_url_rule('/', endpoint='index')

    return app