import uuid, json
import os

from flask import Blueprint, request, url_for, flash, redirect, make_response
from flask import render_template, abort, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import TextField, TextAreaField, SelectField, HiddenField, IntegerField, FloatField
from flask.ext.wtf import Form, PasswordField, validators, ValidationError, Field
from wtforms.widgets import TextInput
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

from portality.core import app, ssl_required, login_manager
from portality import models
from portality.datasets import domain_uni_lookup
from portality.isbn_lookup import isbn_lookup
from portality import util
from pygeocoder import Geocoder

import requests

blueprint = Blueprint('advert', __name__)

condition_choices = [
    ('as new', 'As New'),
    ('very good', 'Very Good'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor'),
]

location_choices = [
    ('home', 'My term-time Residence'),
    ('uni', 'Uni'),
    ('postcode', 'By Postcode'),
]


class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []


class ValidYear(object):
    def __init__(self):
        pass

    def __call__(self, form, field):
        current_year = datetime.now().year
        year = field.data
        if year > current_year:
            raise ValidationError('The year of publication cannot be in the future.')

class ValidFloat(object):
    def __init__(self):
        pass

    def __call__(self, form, field):
        if field.data:
            try:
                field.data = float(field.data)
            except ValueError:
                raise ValidationError('This is not a valid number.')

class SubmitAd(Form):
    isbn = TagListField('ISBN')
    title = TextField('Title', [validators.Required()])
    edition = TextField('Edition')
    authors = TextField('Author(s)', [validators.Required()])
    year = IntegerField('Year', [validators.Optional(),
                                 ValidYear()]
                        )
    publisher = TextField('Publisher')
    subject = TextField('Subject')
    condition = SelectField('Condition', choices=condition_choices)
    price = TextField('Price', [validators.Required(),
                                ValidFloat()]
                        )
    location = SelectField('Location to advertise', choices=location_choices)
    postcode = TextField('Postcode')
    keywords = TagListField('Keywords')

class GeneralAd(Form):
    category = TextField("Item Category", [validators.Required()])
    title = TextField('Title', [validators.Required()])
    description = TextAreaField("Description", [validators.Optional()])
    price = FloatField('Price', [validators.Required()])
    location = SelectField('Location to advertise', choices=location_choices)
    postcode = TextField('Postcode')
    keywords = TagListField('Keywords')
    condition = SelectField('Condition', choices=condition_choices)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def xwalk_book(form, advert):
    if not advert:
        advert = models.Advert()

    advert.set_category(advert.BOOK)
    advert.set_owner(current_user.id)

    if form.isbn.data:
        advert.set_isbn(form.isbn.data)

    advert.set_title(form.title.data)

    if form.edition.data:
        advert.set_edition(form.edition.data)

    if form.authors.data:
        advert.set_authors(form.authors.data)

    if form.year.data:
        advert.set_year(form.year.data)

    if form.publisher.data:
        advert.set_publisher(form.publisher.data)

    if form.subject.data:
        advert.set_subjects(form.subject.data)

    if form.condition.data:
        advert.set_condition(form.condition.data)

    if form.price.data:
        advert.set_price(form.price.data)

    if form.location.data:
        advert.set_spot(form.location.data)
        if form.location.data == 'home':
            if current_user.location:
                lat, lon = current_user.location
                advert.set_location(lat, lon)
            else:
                flash("We do not have an address for your account. If you wish to use this option, please edit your information under My Account.", 'error')
                return render_template('advert/submit.html', form=form)
        elif form.location.data == 'uni':
            mail = current_user.id.split('@')
            domain = mail[-1]
            uni = domain_uni_lookup[domain]["address"]
            results = Geocoder.geocode(uni + ', United Kingdom')
            lat, lng = results[0].coordinates
            advert.set_location(lat, lng)
        elif form.location.data == 'postcode':
            results = Geocoder.geocode(form.postcode.data + ', United Kingdom')
            lat, lng = results[0].coordinates
            advert.set_location(lat, lng)

    if form.keywords.data:
        advert.set_keywords(form.keywords.data)

    image = request.files['upload']
    if image and allowed_file(image.filename):
        image_id = uuid.uuid4().hex
        name = image.filename.split('.')
        extension = name[-1]
        image_name = str(image_id) + '.' + extension
        image.save(os.path.join(app.config['IMAGES_FOLDER'], image_name))
        advert.set_image_id(image_name)
    elif image and not allowed_file(image.filename):
        flash('This is not an allowed image type', 'error')

    advert.expires_in(app.config.get("ADVERT_TIMEOUT", 604800))
    advert.save()
    advert.refresh()
    return advert

def xwalk_generic(form, advert):
    if not advert:
        advert = models.Advert()

    advert.set_owner(current_user.id)

    if form.category.data:
        advert.set_category(form.category.data)

    advert.set_title(form.title.data)

    if form.description.data:
        advert.set_description(form.description.data)

    if form.condition.data:
        advert.set_condition(form.condition.data)

    if form.price.data:
        advert.set_price(form.price.data)

    if form.location.data:
        advert.set_spot(form.location.data)
        if form.location.data == 'home':
            if current_user.location:
                lat, lon = current_user.location
                advert.set_location(lat, lon)
            else:
                flash("We do not have an address for your account. If you wish to use this option, please edit your information under My Account.", 'error')
                return render_template('advert/submit.html', form=form)
        elif form.location.data == 'uni':
            mail = current_user.id.split('@')
            domain = mail[-1]
            uni = domain_uni_lookup[domain]["address"]
            results = Geocoder.geocode(uni + ', United Kingdom')
            lat, lng = results[0].coordinates
            advert.set_location(lat, lng)
        elif form.location.data == 'postcode':
            results = Geocoder.geocode(form.postcode.data + ', United Kingdom')
            lat, lng = results[0].coordinates
            advert.set_location(lat, lng)

    if form.keywords.data:
        advert.set_keywords(form.keywords.data)

    image = request.files['upload']
    if image and allowed_file(image.filename):
        image_id = uuid.uuid4().hex
        name = image.filename.split('.')
        extension = name[-1]
        image_name = str(image_id) + '.' + extension
        image.save(os.path.join(app.config['IMAGES_FOLDER'], image_name))
        advert.set_image_id(image_name)
    elif image and not allowed_file(image.filename):
        flash('This is not an allowed image type', 'error')

    advert.expires_in(app.config.get("ADVERT_TIMEOUT", 604800))
    advert.save()
    advert.refresh()
    return advert

@blueprint.route('/submit', methods=['GET', 'POST', 'DELETE'])
@blueprint.route('/<ad_id>/edit', methods=['GET', 'POST', 'DELETE'])
@login_required
@ssl_required
def adsubmit(ad_id=None):
    advert = models.Advert.pull(ad_id)
    if advert is not None:
        if advert.is_deleted and not current_user.has_role("edit_deleted"):
            abort(404)

        owner = current_user.id == advert.owner
        if not owner and not current_user.has_role("edit_all_adverts"):
            abort(404)

    # two possible forms, need to populate the right one!
    bookform = None
    genform = None

    # if we are creating a new ad from scratch, both forms are blank
    if request.path.endswith("/submit") and request.method == "GET":
        bookform = SubmitAd()
        genform = GeneralAd()
        return render_template('advert/submit.html', form=bookform, genform=genform)

    # if we are editing an existing advert, we need to populate the correct one
    elif request.path.endswith("/edit") and request.method == "GET":
        if advert.category == "Book":
            bookform = SubmitAd(request.form, advert)
        else:
            genform = GeneralAd(request.form, advert)
        return render_template('advert/submit.html', form=bookform, genform=genform, advert=advert)

    if request.method == "POST":
        category = request.values.get("category")
        if category is not None:
            # something other than a book
            genform = GeneralAd(request.form, advert)
            if not genform.validate():
                flash('Error while submitting', 'error')
                bookform = SubmitAd()
                return render_template('advert/submit.html', form=bookform, advert=advert, genform=genform)
            advert = xwalk_generic(genform, advert)
            flash('Advert saved successfully', 'success')
            return redirect(url_for('.details', ad_id=advert.id))
        else:
            # we have a book
            bookform = SubmitAd(request.form, advert)
            if not bookform.validate():
                flash('Error while submitting', 'error')
                genform = GeneralAd()
                return render_template('advert/submit.html', form=bookform, advert=advert, genform=genform)
            advert = xwalk_book(bookform, advert)
            flash('Advert saved successfully', 'success')
            return redirect(url_for('.details', ad_id=advert.id))

login_manager.login_view = "account.login"

@blueprint.route('/<ad_id>', methods=['GET'])
@login_required
@ssl_required
def details(ad_id):
    advert = models.Advert.pull(ad_id)
    if not advert:
        abort(404)

    if advert.is_deleted and not current_user.has_role("view_deleted"):
        abort(404)

    owner = False
    if current_user.id == advert.owner:
        owner = True

    if advert.is_deactivated and not owner and not current_user.has_role("view_deleted"):
        abort(404)

    return render_template('advert/details.html', advert=advert, images_folder=app.config['IMAGES_FOLDER'],
                           owner=owner, ad_id=ad_id, map_key=app.config.get("GOOGLE_MAP_API_KEY"))

class ContactForm(Form):
    about = TextField('Subject:', [validators.Required()])
    message = TextAreaField('Message:', [validators.Required()])

@blueprint.route('/<ad_id>/contact', methods=['GET', 'POST', 'DELETE'])
@login_required
@ssl_required
def contact(ad_id):
    advert = models.Advert.pull(ad_id)
    owner = advert.owner
    title = advert.title
    ad_id = advert.id

    form = ContactForm(request.form)

    if request.method == 'POST' and form.validate():

        to = [owner, app.config['ADMIN_EMAIL']]
        fro = current_user.id
        subject = form.about.data + ' on ' + app.config.get("SERVICE_NAME", "")
        text = form.message.data
        try:
            util.send_mail(to=to, fro=fro, subject=subject, text=text)
            flash('Email has been sent.')
            if app.config.get('DEBUG', False):
                flash(to[0] + ' ' + fro + ' ' + subject + ' ' + text)
            return redirect(url_for('.details', ad_id=ad_id))
        except Exception as e:
            flash('Hm, sorry - sending the email didn\'t work.', 'error')
            if app.config.get('DEBUG', False):
                flash('Debug mode - email is ' + to[0] + ' ' + fro + ' ' + subject + ' ' + text)

    return render_template('advert/contact.html', form=form, advert=advert, owner=owner, ad_id=ad_id, title=title)

@blueprint.route('/<ad_id>/deactivate', methods=['GET', 'POST', 'DELETE'])
@login_required
@ssl_required
def deactivate(ad_id):
    advert = models.Advert.pull(ad_id)
    username = current_user.id
    if current_user.id == advert.owner:
        advert.mark_deactivated()
        advert.save()
        advert.refresh()
        flash('Advert successfully deactivated!', "success")
    else:
        abort(401)

    referrer = request.values.get("referrer", "user")
    if referrer == "user":
        return redirect(url_for("account.username", username=username))
    elif referrer == "details":
        return redirect(url_for("advert.details", ad_id=ad_id))

@blueprint.route('/<ad_id>/reactivate', methods=['GET', 'POST', 'DELETE'])
@login_required
@ssl_required
def reactivate(ad_id):
    advert = models.Advert.pull(ad_id)
    username = current_user.id
    if current_user.id == advert.owner:
        if advert.is_deleted:
            return render_template("advert/deleted.html")
        advert.mark_deactivated(False)
        advert.set_expires((datetime.now().replace(microsecond=0) + timedelta(days=7)).isoformat() + 'Z')

        advert.save()
        advert.refresh()
        flash('Advert successfully reactivated!', "success")
    else:
        abort(401)

    referrer = request.values.get("referrer", "user")
    if referrer == "user":
        return redirect(url_for("account.username", username=username))
    elif referrer == "details":
        return redirect(url_for("advert.details", ad_id=ad_id))

@blueprint.route('/<ad_id>/delete', methods=['GET', 'POST', 'DELETE'])
@login_required
@ssl_required
def delete(ad_id):
    if not current_user.has_role("delete_advert"):
        abort(401)

    advert = models.Advert.pull(ad_id)
    advert.mark_deleted()
    advert.save()
    advert.refresh()
    flash('Advert successfully deleted!', "success")

    referrer = request.values.get("referrer", "details")
    if referrer == "details":
        return redirect(url_for("advert.details", ad_id=ad_id))
    else:
        return redirect(url_for("admin.index"))

@blueprint.route('/<ad_id>/undelete', methods=['GET', 'POST', 'DELETE'])
@login_required
@ssl_required
def undelete(ad_id):
    if not current_user.has_role("delete_advert"):
        abort(401)

    advert = models.Advert.pull(ad_id)
    advert.mark_deleted(False)
    advert.save()
    advert.refresh()
    flash('Advert successfully undeleted!', "success")

    referrer = request.values.get("referrer", "details")
    if referrer == "details":
        return redirect(url_for("advert.details", ad_id=ad_id))
    else:
        return redirect(url_for("admin.index"))

@blueprint.route('/abuse/<ad_id>', methods=['GET'])
@login_required
@ssl_required
def abuse(ad_id):
    advert = models.Advert.pull(ad_id)
    advert.increment_abuse()
    advert.save()
    flash('Abuse reported', 'message')
    return redirect(url_for("advert.details", ad_id=ad_id))

