import uuid, json
import os

from flask import Blueprint, request, url_for, flash, redirect, make_response
from flask import render_template, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import TextField, TextAreaField, SelectField, HiddenField
from flask.ext.wtf import Form, PasswordField, validators, ValidationError

from portality.core import app, ssl_required
from portality import models
from portality.datasets import domain_uni_lookup
from portality import util
from pygeocoder import Geocoder

blueprint = Blueprint('account', __name__)

class ValidEmailDomain(object):
    def __init__(self):
        pass

    def __call__(self, form, field):
        domain = field.data.split("@")
        if len(domain) != 2:
            raise ValidationError('This email address is not supported')
        allowed = domain_uni_lookup.keys()
        if domain[1] in allowed:
            return True
        allowed_suffix = ["." + a for a in allowed]
        for suffix in allowed_suffix:
            if domain[1].endswith(suffix):
                return True
        raise ValidationError('This email is not on our list of permitted emails.  Please be sure to use your institutional email address.')

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
    email = TextField('Email', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

class RegisterForm(Form):
    name = TextField('Full name', [validators.Required()])
    email = TextField('Email Address',
                    [
                        validators.Required(),
                        validators.Length(min=3, max=35),
                        validators.Email(message='Must be a valid email address'),
                        ValidEmailDomain()
                    ],
                    description="You must use your institutional email here")
    degree = TextField('Course')
    postcode = TextField('Postcode of term-time residence',
                         description='We will use this postcode to obtain the approximate location of your term-time residence, to give you information about items for sale that are close to you.',)
    phone = TextField('Phone number')
    graduation = TextField('Graduation Year')

class SetPasswordForm(Form):
    old_password = PasswordField("Current Password", [validators.Required()])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Repeat Password', [validators.Required()])


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

    if request.method == "GET":
        adverts = models.Advert.get_by_owner(username)
        form = _get_user_form(acc)
        pw = SetPasswordForm(csrf_enabled=False)
        return render_template('account/view.html', account=acc, adverts=adverts, form=form, pwform=pw)

    is_delete = request.method == "DELETE" or (request.method == "POST" and request.values.get("submit", False) == "Delete")
    if is_delete:
        if current_user.id != acc.id and not current_user.is_super:
            abort(401)

        acc.set_deleted(True, cascade=True, save=True) # this automatically deletes all the ads and saves
        logout_user()
        flash('Account ' + acc.id + ' deleted', "success")
        return redirect(url_for('root'))

    if request.method == "POST":
        if current_user.id != acc.id and not current_user.is_super:
            abort(401)

        newdata = request.json if request.json else request.values

        # is this a password update request?
        if "password" in newdata:
            pw = SetPasswordForm(request.form, csrf_enabled=False)
            form = _get_user_form(acc)
            adverts = models.Advert.get_by_owner(username)

            # first check that the form validates
            if not pw.validate():
                flash("There was a problem with your password change request", "error")
                return render_template('account/view.html', account=acc, adverts=adverts, form=form, pwform=pw)

            # now check that the current password is correct
            if not acc.check_password(pw.old_password.data):
                flash("The current password you supplied was wrong", "error")
                pw.old_password.errors.append("Your password was incorrect")
                return render_template('account/view.html', account=acc, adverts=adverts, form=form, pwform=pw)

            # if we get to here, we can set the password
            acc.set_password(pw.password.data)
            acc.save()
            flash("Password updated", "success")
            return render_template('account/view.html', account=acc, adverts=adverts, form=form, pwform=pw)

        # is this a user details update request (which is all that is left here)
        form = _get_user_form(acc, use_form_data=True)
        if not form.validate():
            flash("There was a problem with your change of details request", "error")
            pw = SetPasswordForm(csrf_enabled=False)
            adverts = models.Advert.get_by_owner(username)
            return render_template('account/view.html', account=acc, adverts=adverts, form=form, pwform=pw)

        # if we get to here then we need to update the account record
        _update_account(acc, form)
        acc.save()
        flash("Account updated", "success")
        adverts = models.Advert.get_by_owner(username)
        pw = SetPasswordForm(csrf_enabled=False)
        return render_template('account/view.html', account=acc, adverts=adverts, form=form, pwform=pw)

@blueprint.route('/login', methods=['GET', 'POST'])
@ssl_required
def login():
    current_info = {'next': request.args.get('next', '')}
    form = LoginForm(request.form, csrf_enabled=False, **current_info)
    if request.method == 'POST' and form.validate():
        password = form.password.data
        email = form.email.data
        user = models.Account.pull(email)
        if user is None:
            user = models.Account.pull_by_email(email)

        if user is not None:
            if user.is_deleted():
                flash('Invalid credentials', 'error')
                return render_template('account/login.html', form=form)

            if user.is_banned():
                flash('This account is banned from the service', 'error')
                return render_template('account/login.html', form=form)

            if user.check_password(password):
                login_user(user, remember=True)
                flash('Welcome back.', 'success')
                return redirect(get_redirect_target(form=form))
            else:
                flash('Incorrect username/password', 'error')
                return render_template('account/login.html', form=form)
        else:
            flash('Incorrect username/password', 'error')
            return render_template('account/login.html', form=form)
    elif request.method == 'POST' and not form.validate():
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
            util.flash_with_url('Your account email address is not recognised.', 'error')
            return render_template('account/forgot.html')

        if account.is_deleted():
            util.flash_with_url('Your account email address is not recognised.', 'error')
            return render_template('account/forgot.html')

        if account.is_banned():
            flash('This account is banned from the service', 'error')
            return render_template('account/forgot.html')

        if not account.data.get('email'):
            util.flash_with_url('Your account does not have an associated email address.', 'error')
            return render_template('account/forgot.html')

        # if we get to here, we have a user account to reset
        reset_token = uuid.uuid4().hex
        account.set_reset_token(reset_token, app.config.get("PASSWORD_RESET_TIMEOUT", 86400))
        account.save()

        sep = "/"
        if request.url_root.endswith("/"):
            sep = ""
        reset_url = request.url_root + sep + "account/reset/" + reset_token

        to = [account.data['email'], app.config['FEEDBACK_EMAIL']]
        fro = app.config['FEEDBACK_EMAIL']
        subject = app.config.get("SERVICE_NAME", "") + " - password reset"
        text = "A password reset request for account '" + account.id + "' has been received and processed.\n\n"
        text += "Please visit " + reset_url + " and enter your new password.\n\n"
        text += "If you are the user " + account.id + " and you requested this change, please visit that link now and set the password to something of your preference.\n\n"
        text += "If you are the user " + account.id + " and you did not request this change, you can ignore this email.\n\n"
        text += "Regards, The UniBoard Team"
        try:
            util.send_mail(to=to, fro=fro, subject=subject, text=text)
            flash('Instructions to reset your password have been sent to you. Please check your emails.', "success")
            if app.config.get('DEBUG', False):
                flash('Debug mode - url for reset is ' + reset_url, "error")
        except Exception as e:
            flash('Hm, sorry - sending the password reset email didn\'t work.', 'error')
            if app.config.get('DEBUG', False):
                flash('Debug mode - url for reset is' + reset_url, "error")
                # app.logger.error(magic + "\n" + repr(e))

    return render_template('account/forgot.html')


@blueprint.route("/reset/<reset_token>", methods=["GET", "POST"])
@ssl_required
def reset(reset_token):
    account = models.Account.get_by_reset_token(reset_token)
    if account is None:
        abort(404)

    if account.is_deleted():
        abort(404)

    if account.is_banned():
        abort(403)

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


@blueprint.route('/register', methods=['GET', 'POST'])
@ssl_required
def register():
    form = RegisterForm(request.form, csrf_enabled=False)

    if request.method == 'POST' and form.validate():
        existing_account = models.Account.pull(form.email.data)
        account = None
        if existing_account is not None:
            if existing_account.is_banned():
                flash('You have been banned from using this service.', "error")
                return render_template('account/register.html', form=form)
            elif existing_account.is_deleted():
                flash('Your old account has been restored. Welcome back!', "success")
                existing_account.set_deleted(False, save=False)
                account = existing_account
                account.clear_password()
            else:
                flash('This account already exists.')
                return redirect(url_for('.forgot'))

        if account is None:
            account = models.Account()

        account.id = form.email.data
        account.set_email(form.email.data)
        account.set_name(form.name.data)

        if form.degree.data:
            account.set_degree(form.degree.data)

        if form.postcode.data:
            account.set_postcode(form.postcode.data)

            results = Geocoder.geocode(form.postcode.data + ', United Kingdom')
            lat, lng = results[0].coordinates
            account.set_location(lat, lng)

        if form.phone.data:
            account.set_phone(form.phone.data)

        if form.graduation.data:
            account.set_graduation(form.graduation.data)

        # automatically set the user role to be "user"
        account.add_role("user")

        activation_token = uuid.uuid4().hex
        account.set_activation_token(activation_token, app.config.get("PASSWORD_ACTIVATE_TIMEOUT", 86400))
        account.save()
        account.refresh()  # refresh the index

        #sending the email with the activation link

        sep = "/"
        if request.url_root.endswith("/"):
            sep = ""
        activation_url = request.url_root + sep + "account/activate/" + activation_token

        to = [account.data['email'], app.config['FEEDBACK_EMAIL']]
        fro = app.config['FEEDBACK_EMAIL']
        subject = app.config.get("SERVICE_NAME", "") + " - new password"
        text = "Welcome to UniBoard, '" + account.email + "'!\n\n"
        text += "Please visit " + activation_url + " to set a password for your account.\n\n"
        text += "Regards, The UniBoard Team"
        try:
            util.send_mail(to=to, fro=fro, subject=subject, text=text)
            flash('Instructions to set up your password have been sent to you. Please check your emails.', "success")
            if app.config.get('DEBUG', False):
                flash('Debug mode - url for activation is ' + activation_url, "error")
        except Exception as e:
            magic = str(uuid.uuid1())
            #util.flash_with_url(
                #'Hm, sorry - sending the password reset email didn\'t work.' + CONTACT_INSTR + ' It would help us if you also quote this magic number: ' + magic + ' . Thank you!',
                #'error')
            if app.config.get('DEBUG', False):
                flash('Debug mode - url for reset is ' + activation_url, "error")
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

def get_redirect_target(form=None):
    form_target = ''
    if form and hasattr(form, 'next') and getattr(form, 'next'):
        form_target = form.next.data

    for target in form_target, request.args.get('next', []):
        if not target:
            continue
        if target == util.is_safe_url(target):
            return target
    return url_for('root')

def _get_user_form(acc, use_form_data=False):
    form = None
    if use_form_data:
        form = RegisterForm(request.form, csrf_enabled=False)
        form.email.data = acc.email
    else:
        form = RegisterForm(csrf_enabled=False)
        form.name.data = acc.name
        form.email.data = acc.email
        form.degree.data = acc.degree
        form.postcode.data = acc.postcode
        form.phone.data = acc.phone
        form.graduation.data = acc.graduation
    return form

def _update_account(account, form):
    account.set_name(form.name.data)

    if form.degree.data:
        account.set_degree(form.degree.data)
    elif form.degree.data == "":
        del account.degree

    if form.postcode.data:
        account.set_postcode(form.postcode.data)

        results = Geocoder.geocode(form.postcode.data + ', United Kingdom')
        lat, lng = results[0].coordinates
        account.set_location(lat, lng)
    elif form.postcode.data == "":
        del account.postcode
        account.unset_location()

    if form.phone.data:
        account.set_phone(form.phone.data)
    elif form.phone.data == "":
        del account.phone

    if form.graduation.data:
        account.set_graduation(form.graduation.data)
    elif form.graduation.data == "":
        del account.graduation