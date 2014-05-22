import uuid, json
import os

from flask import Blueprint, request, url_for, flash, redirect, make_response
from flask import render_template, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import TextField, TextAreaField, SelectField, HiddenField
from flask.ext.wtf import Form, PasswordField, validators, ValidationError

from portality.core import app, ssl_required
from portality import models
from portality import util
from pygeocoder import Geocoder

blueprint = Blueprint('account', __name__)


@blueprint.route('/')
@login_required
@ssl_required
def index():
    if not current_user.has_role("list_users"):
        abort(401)

    # users = models.Account.query() #{"sort":{'id':{'order':'asc'}}},size=1000000
    accs = models.Account.iterall()  # NOTE: this is only suitable if there is a small number of users - we will iterate through all of them here
    users = []
    for acc in accs:
        # explicitly mapped to ensure no leakage of sensitive data. augment as necessary
        user = {'id': acc.id, "email": acc.email, "role": acc.role}
        if 'created_date' in acc.data:
            user['created_date'] = acc.data['created_date']
        users.append(user)
    print
    users
    if util.request_wants_json():
        resp = make_response(json.dumps(users, sort_keys=True, indent=4))
        resp.mimetype = "application/json"
        return resp
    else:
        return render_template('account/users.html', users=users)


@blueprint.route('/<username>', methods=['GET', 'POST', 'DELETE'])
@login_required
@ssl_required
def username(username):
    acc = models.Account.pull(username)

    if acc is None:
        abort(404)
    elif ( request.method == 'DELETE' or
               ( request.method == 'POST' and
                         request.values.get('submit', False) == 'Delete' ) ):
        if current_user.id != acc.id and not current_user.is_super:
            abort(401)
        else:
            conf = request.values.get("confirm")
            if conf is None or conf != "confirm":
                flash('check the box to confirm you really mean it!', "error")
                return render_template('account/view.html', account=acc)
            acc.delete()
            flash('Account ' + acc.id + ' deleted')
            return redirect(url_for('.index'))
    elif request.method == 'POST':
        if current_user.id != acc.id and not current_user.is_super:
            abort(401)
        newdata = request.json if request.json else request.values
        if newdata.get('id', False):
            if newdata['id'] != username:
                acc = models.Account.pull(newdata['id'])
            else:
                newdata['api_key'] = acc.data['api_key']
        for k, v in newdata.items():
            if k not in ['submit', 'password', 'role', 'confirm']:
                acc.data[k] = v
        if 'password' in newdata and not newdata['password'].startswith('sha1'):
            if "confirm" in newdata and newdata["password"] == newdata["confirm"]:
                acc.set_password(newdata['password'])
            else:
                flash("Passwords do not match", "error")
                return render_template('account/view.html', account=acc)
        # only super users can re-write roles
        if "role" in newdata and current_user.is_super:
            new_roles = [r.strip() for r in newdata.get("role").split(",")]
            acc.set_role(new_roles)

        acc.save()
        flash("Account updated", "success")
        return render_template('account/view.html', account=acc)
    else:
        if util.request_wants_json():
            resp = make_response(
                json.dumps(acc.data, sort_keys=True, indent=4))
            resp.mimetype = "application/json"
            return resp
        else:
            # do an mget on the journals, so that we can present them to the user
            return render_template('account/view.html', account=acc)


def get_redirect_target(form=None):
    form_target = ''
    if form and hasattr(form, 'next') and getattr(form, 'next'):
        form_target = form.next.data

    for target in form_target, request.args.get('next', []):
        if not target:
            continue
        if target == util.is_safe_url(target):
            return target
    return url_for('admin.index')


class RedirectForm(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if self.next.data == util.is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class LoginForm(RedirectForm):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])


@blueprint.route('/login', methods=['GET', 'POST'])
@ssl_required
def login():
    current_info = {'next': request.args.get('next', '')}
    form = LoginForm(request.form, csrf_enabled=False, **current_info)
    if request.method == 'POST' and form.validate():
        password = form.password.data
        username = form.username.data
        user = models.Account.pull(username)
        if user is None:
            user = models.Account.pull_by_email(username)
        if user is not None and user.check_password(password):
            login_user(user, remember=True)
            flash('Welcome back.', 'success')
            # return form.redirect('index')
            # return redirect(url_for('doaj.home'))
            return redirect(get_redirect_target(form=form))
        else:
            flash('Incorrect username/password', 'error')
    if request.method == 'POST' and not form.validate():
        flash('Invalid credentials', 'error')
    return render_template('account/login.html', form=form)


@blueprint.route('/forgot', methods=['GET', 'POST'])
@ssl_required
def forgot():
    if request.method == 'POST':
        # get hold of the user account
        un = request.form.get('un', "")
        account = models.Account.pull(un)
        if account is None:
            account = models.Account.pull_by_email(un)
        if account is None:
            util.flash_with_url('Hm, sorry, your account username / email address is not recognised.', 'error')
            return render_template('account/forgot.html')

        if not account.data.get('email'):
            util.flash_with_url('Hm, sorry, your account does not have an associated email address.', 'error')
            return render_template('account/forgot.html')

        # if we get to here, we have a user account to reset
        reset_token = uuid.uuid4().hex
        account.set_reset_token(reset_token, app.config.get("PASSWORD_RESET_TIMEOUT", 86400))
        account.save()

        sep = "/"
        if request.url_root.endswith("/"):
            sep = ""
        reset_url = request.url_root + sep + "account/reset/" + reset_token

        to = [account.data['email'], app.config['ADMIN_EMAIL']]
        fro = app.config['ADMIN_EMAIL']
        subject = app.config.get("SERVICE_NAME", "") + " - password reset"
        text = "A password reset request for account '" + account.id + "' has been received and processed.\n\n"
        text += "Please visit " + reset_url + " and enter your new password.\n\n"
        text += "If you are the user '" + account.id + "' and you requested this change, please visit that link now and set the password to something of your preference.\n\n"
        text += "If you are the user '" + account.id + "' and you did not request this change, you can ignore this email.\n\n"
        text += "Regards, The OpenDOAR Team"
        try:
            util.send_mail(to=to, fro=fro, subject=subject, text=text)
            flash('Instructions to reset your password have been sent to you. Please check your emails.')
            if app.config.get('DEBUG', False):
                flash('Debug mode - url for reset is ' + reset_url)
        except Exception as e:
            flash('Hm, sorry - sending the password reset email didn\'t work.', 'error')
            if app.config.get('DEBUG', False):
                flash('Debug mode - url for reset is' + reset_url)
                # app.logger.error(magic + "\n" + repr(e))

    return render_template('account/forgot.html')


@blueprint.route("/reset/<reset_token>", methods=["GET", "POST"])
@ssl_required
def reset(reset_token):
    account = models.Account.get_by_reset_token(reset_token)
    if account is None:
        abort(404)

    if request.method == "GET":
        return render_template("account/reset.html", account=account)

    elif request.method == "POST":
        # check that the passwords match, and bounce if not
        pw = request.values.get("password")
        conf = request.values.get("confirm")
        if pw != conf:
            flash("Passwords do not match - please try again", "error")
            return render_template("account/reset.html", account=account)

        # update the user's account
        account.set_password(pw)
        account.remove_reset_token()
        account.save()
        flash("Password has been reset", "success")

        # log the user in
        login_user(account, remember=True)
        return redirect(url_for('root'))


@blueprint.route('/logout')
@ssl_required
def logout():
    logout_user()
    flash('You are now logged out', 'success')
    return redirect('/')


def existscheck(form, field):
    test = models.Account.pull(form.name.data)
    if test:
        raise ValidationError('Taken! Please try another.')

email_file = open(os.path.join(app.config['BASE_FILE_PATH'], 'resources', 'email_list.txt'), 'rb')
email_list = []
for line in email_file.readlines():
    line = line.rstrip('\n')
    email_list.append(line)

#TODO write tests for this
def valid_email(self, field):
        l = self.email.data.split('@')
        if l[-1] not in email_list:
            raise ValidationError('This email is not on our list of permitted emails')

class RegisterForm(Form):
    name = TextField('Full name', [validators.Required()])
    email = TextField('Email Address',
    [
        validators.Length(min=3, max=35),
        validators.Email(message='Must be a valid email address'),
        valid_email
    ])
    degree = TextField('Degree')
    postcode = TextField('Postcode')
    phone = TextField('Phone number')
    graduation = TextField('Graduation Year')


class SetPasswordForm(Form):
    password = PasswordField('Password', [
        validators.Required(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Repeat Password')


@blueprint.route('/register', methods=['GET', 'POST'])
#@login_required
@ssl_required
def register():
    #if not app.config.get('PUBLIC_REGISTER',False) and not current_user.has_role("create_user"):
    #abort(401)
    form = RegisterForm(request.form, csrf_enabled=False)
    if request.method == 'POST' and form.validate():
        # api_key = str(uuid.uuid4())
        account = models.Account()
        account.set_email(form.email.data)
        account.set_name(form.name.data)
        account.set_degree(form.degree.data)
        account.set_postcode(form.postcode.data)

        results = Geocoder.geocode(form.postcode.data + ', United Kingdom')
        lat, lng = results[0].coordinates
        account.set_location(lat, lng)

        account.set_phone(form.phone.data)
        account.set_graduation(form.graduation.data)

        activation_token = uuid.uuid4().hex
        account.set_activation_token(activation_token, app.config.get("PASSWORD_ACTIVATE_TIMEOUT", 86400))
        account.save()
        account.refresh()  # refresh the index
        flash('Account created for ' + account.email + '.  You may wish to edit the roles next.', 'success')

        #sending the email with the activation link

        sep = "/"
        if request.url_root.endswith("/"):
            sep = ""
        activation_url = request.url_root + sep + "account/activate/" + activation_token

        # to = [account.data['email'], app.config['ADMIN_EMAIL']]
        # fro = app.config['ADMIN_EMAIL']
        # subject = app.config.get("SERVICE_NAME", "") + " - new password"
        # text = "A new password request for account '" + account.email + "' has been received and processed.\n\n"
        # text += "Please visit " + activation_url + " and enter your new password.\n\n"
        # text += "Regards, The UniBoard Team"
        try:
            util.send_mail(to=to, fro=fro, subject=subject, text=text)
            flash('Instructions to set up your password have been sent to you. Please check your emails.')
            if app.config.get('DEBUG', False):
                flash('Debug mode - url for activation is ' + activation_url)
        except Exception as e:
            magic = str(uuid.uuid1())
            #util.flash_with_url(
                #'Hm, sorry - sending the password reset email didn\'t work.' + CONTACT_INSTR + ' It would help us if you also quote this magic number: ' + magic + ' . Thank you!',
                #'error')
            if app.config.get('DEBUG', False):
                flash('Debug mode - url for reset is ' + activation_url)
            app.logger.error(magic + "\n" + repr(e))

        return redirect('/account/register')  #TODO should be redirecting somewhere else
    if request.method == 'POST' and not form.validate():
        flash('Please correct the errors', 'error')
    return render_template('account/register.html', form=form)


@blueprint.route("/activate/<activation_token>", methods=["GET", "POST"])
@ssl_required
def activate(activation_token):
    account = models.Account.get_by_activation_token(activation_token)
    if account is None:
        abort(404)
    form = SetPasswordForm()
    if request.method == "GET":
        return render_template("account/activate.html", account=account, form=form)

    elif request.method == "POST":
        # check that the passwords match, and bounce if not
        pw = request.values.get("password")
        conf = request.values.get("confirm_password")
        if pw != conf:
            flash("Passwords do not match - please try again", "error")
            return render_template("account/activate.html", account=account, form=form)

        # update the user's account
        account.set_password(pw)
        account.remove_activation_token()
        account.save()
        flash("Password has been set", "success")

        # log the user in
        login_user(account, remember=True)
        return redirect('/')

