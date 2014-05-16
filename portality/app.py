from flask import Flask, request, abort, render_template, redirect, make_response
from flask.views import View
from flask.ext.login import login_user, current_user

import portality.models as models
from portality.core import app, login_manager
from portality import settings

from portality.view.admin import blueprint as admin
from portality.view.account import blueprint as account

@login_manager.user_loader
def load_account_for_login_manager(userid):
    out = models.Account.pull(userid)
    return out

@app.before_request
def standard_authentication():
    """Check remote_user on a per-request basis."""
    remote_user = request.headers.get('REMOTE_USER', '')
    if remote_user:
        user = models.Account.pull(remote_user)
        if user:
            login_user(user, remember=False)
    # add a check for provision of api key
    elif 'api_key' in request.values:
        res = models.Account.query(q='api_key:"' + request.values['api_key'] + '"')['hits']['hits']
        if len(res) == 1:
            user = models.Account.pull(res[0]['_source']['id'])
            if user:
                login_user(user, remember=False)


app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(account, url_prefix='/account')

@app.route("/")
def root():
    return render_template("index.html", api_base_url="")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], port=app.config['PORT'])

