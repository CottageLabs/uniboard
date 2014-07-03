import uuid, json
import os

from flask import Blueprint, request, url_for, flash, redirect, make_response
from flask import render_template, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import TextField, TextAreaField, SelectField, HiddenField, IntegerField, FloatField
from flask.ext.wtf import Form, PasswordField, validators, ValidationError, Field
from wtforms.widgets import TextInput
from werkzeug.utils import secure_filename

from portality.core import app, ssl_required
from portality import models
from portality.datasets import domain_uni_lookup
from portality import util
from pygeocoder import Geocoder

blueprint = Blueprint('advert', __name__)

subjects = [
    ('maths', 'Maths'),
    ('biology', 'Biology'),
    ('law', 'Law'),
]

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


class SubmitAd(Form):
    isbn = TagListField('ISBN')
    title = TextField('Title', [validators.Required()])
    edition = TextField('Edition')
    authors = TextField('Author(s)', [validators.Required()])
    year = IntegerField('Year', [validators.Optional()])
    publisher = TextField('Publisher')
    subjects = TextField('Subject')
    condition = SelectField('Condition', choices=condition_choices)
    price = FloatField('Price', [validators.Required()])
    location = SelectField('Location to advertise', choices=location_choices)
    postcode = TextField('Postcode')
    keywords = TagListField('Keywords')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@blueprint.route('/submit', methods=['GET', 'POST', 'DELETE'])
@blueprint.route('/<ad_id>/edit', methods=['GET', 'POST', 'DELETE'])
@login_required
@ssl_required
def adsubmit(ad_id=None):
    advert = models.Advert.pull(ad_id)

    form = SubmitAd(request.form, advert)

    if request.method == 'POST':
        if not form.validate():
            print form.errors
            flash('Error while submitting', 'error')
        else:
            if not advert:
                advert = models.Advert()

            advert.set_owner(current_user.id)

            if form.isbn.data:
                advert.set_isbn(form.isbn.data)

            advert.set_title(form.title.data)

            if form.edition.data:
                advert.set_edition(form.edition.data)

            advert.set_authors(form.authors.data)

            if form.year.data:
                advert.set_year(form.year.data)

            if form.publisher.data:
                advert.set_publisher(form.publisher.data)

            if form.subjects.data:
                advert.set_subjects(form.subjects.data)

            if form.condition.data:
                advert.set_condition(form.condition.data)

            if form.price.data:
                advert.set_price(form.price.data)

            if form.location.data:
                advert.set_spot(form.location.data)
                if form.location.data == 'home':
                    lat, lon = current_user.location
                    advert.set_location(lat, lon)
                elif form.location.data == 'uni':
                    mail = current_user.id.split('@')
                    domain = mail[-1]
                    uni = domain_uni_lookup[domain]
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

            advert.save()
            advert.refresh()
            flash('Advert saved successfully', 'success')
            return redirect(url_for('.details', ad_id=advert.id))

    return render_template('advert/submit.html', form=form)


@blueprint.route('/<ad_id>', methods=['GET'])
@login_required
@ssl_required
def details(ad_id):
    advert = models.Advert.pull(ad_id)
    owner = None

    if current_user.id == advert.owner:
        owner = True
    if not advert:
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

@blueprint.route('/<ad_id>/delete', methods=['GET', 'POST', 'DELETE'])
@login_required
@ssl_required
def delete(ad_id):
    advert = models.Advert.pull(ad_id)
    username = current_user.id
    if current_user.id == advert.owner:
        advert.mark_deleted()
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
        advert.mark_deleted(False)
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