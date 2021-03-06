import os, requests, json, esprit
from flask import Flask
from functools import wraps
from urllib import unquote

from flask import request, redirect, url_for, flash
from portality import settings
from flask.ext.login import LoginManager, current_user
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    configure_app(app)
    if app.config.get('INITIALISE_INDEX',False): initialise_index(app)
    setup_jinja(app)
    setup_error_logging(app)
    login_manager.setup_app(app)
    return app

def configure_app(app):
    app.config.from_object(settings)
    # parent directory
    here = os.path.dirname(os.path.abspath( __file__ ))
    config_path = os.path.join(os.path.dirname(here), 'app.cfg')
    if os.path.exists(config_path):
        app.config.from_pyfile(config_path)

def initialise_index(app):
    mappings = app.config["MAPPINGS"]
    conn = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])
    if not esprit.raw.index_exists(conn):
        print "Creating Index; host:" + str(conn.host) + " port:" + str(conn.port) + " db:" + str(conn.index)
        esprit.raw.create_index(conn)
    for key, mapping in mappings.iteritems():
        if not esprit.raw.has_mapping(conn, key):
            r = esprit.raw.put_mapping(conn, key, mapping)
            print key, r.status_code

def setup_error_logging(app):
    if not app.debug:
        # Custom logging WILL BE IGNORED by Flask if app.debug == True -
        # even if you remove the condition above this comment.
        import logging, sys
        ADMINS = app.config.get('ADMINS', [])
        if not ADMINS:
            e = app.config.get('ADMIN_EMAIL')
            if e:
                if isinstance(e, basestring):
                    ADMINS = [e]
                elif isinstance(e, list):
                    ADMINS = e
        if ADMINS and not app.config.get('SUPPRESS_ERROR_EMAILS'):
            from logging.handlers import SMTPHandler
            import platform
            hostname = platform.uname()[1]
            mail_handler = SMTPHandler('mailtrap.io',
                                       'server-error@' + hostname,
                                       ADMINS,
                                       'Uniboard Flask Error',
                                       credentials=('17847d564f257fd8f', 'dc4018be4e84eb')
                           )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # send errors to stderr, supervisord will capture them in the app's
        # error log
        send_errors_to_supervisor = logging.StreamHandler(sys.stderr)
        send_errors_to_supervisor.setLevel(logging.ERROR)
        app.logger.addHandler(send_errors_to_supervisor)


def setup_jinja(app):
    '''Add jinja extensions and other init-time config as needed.'''

    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.jinja_env.globals['getattr'] = getattr
    app.jinja_env.globals['unquote'] = unquote

    # a jinja filter that prints to the Flask log
    def jinja_debug(text):
        print text
        return ''
    app.jinja_env.filters['debug']=jinja_debug

app = create_app()

# a decorator to be used elsewhere (or in this file) in the app,
# anywhere where a view f() should be served only over SSL
def ssl_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if app.config.get("SSL"):
            if request.is_secure:
                return fn(*args, **kwargs)
            else:
                return redirect(request.url.replace("http://", "https://"))
        
        return fn(*args, **kwargs)
            
    return decorated_view

def restrict_to_role(role):
    if current_user.is_anonymous():
        flash('You are trying to access a protected area. Please log in first.', 'error')
        return redirect(url_for('account.login', next=request.url))

    if not current_user.has_role(role):
        flash('You do not have permission to access this area of the site.', 'error')
        return redirect(url_for('root'))
