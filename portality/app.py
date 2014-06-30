from flask import Flask, request, abort, render_template, redirect, make_response, jsonify, send_file, send_from_directory
from flask.views import View
from flask.ext.login import login_user, current_user

import portality.models as models
from portality.core import app, login_manager
from portality import settings

from portality.view.admin import blueprint as admin
from portality.view.account import blueprint as account
from portality.view.query import blueprint as query
from portality.view.advert import blueprint as advert

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
app.register_blueprint(query, url_prefix='/user_query')
app.register_blueprint(advert, url_prefix='/advert')

@app.route("/")
def root():
    if current_user.is_authenticated() and current_user.has_role("user"):
        return render_template("search.html", search_base_url="")
    else:
        return render_template("welcome.html")

@app.route('/autocomplete/<doc_type>/<field_name>', methods=["GET", "POST"])
def autocomplete(doc_type, field_name):
    prefix = request.args.get('q','').lower()

    if not prefix:
        return jsonify({'suggestions':[{"id":"", "text": "No results found"}]})  # select2 does not understand 400, which is the correct code here...

    #Because AdBock blocks anything with the word advert in it, the doc_type the autocomplete submits had to be renamed.
    if doc_type == 'adsubmit':
        doc_type = 'advert'
    m = models.lookup_model(doc_type)
    if not m:
        return jsonify({'suggestions':[{"id":"", "text": "No results found"}]})  # select2 does not understand 404, which is the correct code here...

    size = request.args.get('size', 5)
    return jsonify({'suggestions': m.autocomplete(field_name, prefix, size=size)})
    # you shouldn't return lists top-level in a JSON response:
    # http://flask.pocoo.org/docs/security/#json-security

@app.route("/user_uploads/<image_name>")
def serve_user_uploads(image_name):
    # if current_user.is_authenticated() and current_user.has_role("user"):
    #
    return send_from_directory(app.config['IMAGES_FOLDER'], image_name)
    # else:
    #     abort(401)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], port=app.config['PORT'])


