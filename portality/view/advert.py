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
    ('home', 'Home'),
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
    isbn = TextField('ISBN')
    title = TextField('Title', [validators.Required()])
    edition = TextField('Edition')
    authors = TextField('Author(s)', [validators.Required()])
    year = IntegerField('Year')
    publisher = TextField('Publisher')
    subjects = SelectField('Subject', choices=subjects)
    condition = SelectField('Condition', choices=condition_choices)
    price = FloatField('Price', [validators.Optional()])
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
            advert.set_isbn(form.isbn.data)
            advert.set_title(form.title.data)
            advert.set_edition(form.edition.data)
            advert.set_authors(form.authors.data)
            advert.set_year(form.year.data)
            advert.set_publisher(form.publisher.data)
            advert.set_subjects(form.subjects.data)
            advert.set_condition(form.condition.data)

            if form.price.data:
                advert.set_price(form.price.data)

            if form.location.data == 'home':
                lat, lon = current_user.location
                advert.set_location(lat, lon)
            elif form.location.data == 'uni':
                results = Geocoder.geocode('Brunel University, United Kingdom')
                lat, lng = results[0].coordinates
                advert.set_location(lat, lng)
            elif form.location.data == 'postcode':
                results = Geocoder.geocode(form.postcode.data + ', United Kingdom')
                lat, lng = results[0].coordinates
                advert.set_location(lat, lng)

            advert.set_keywords(form.keywords.data)

            image = request.files['upload']
            if image and allowed_file(image.filename):
                image_id = secure_filename(image.filename)
                advert.set_image_id(image_id)
                image.save(os.path.join(app.config['IMAGES_FOLDER'], image_id))
            elif image and not allowed_file(image.filename):
                flash('This is not an allowed image type', 'error')

            advert.save()
            advert.refresh()
            flash('Advert saved successfully', 'success')
            return redirect(url_for('.adsubmit', ad_id=advert.id))

    return render_template('advert/submit.html', form=form)


@blueprint.route('/<ad_id>', methods=['GET'])
@login_required
@ssl_required
def details(ad_id):
    advert = models.Advert.pull(ad_id)

    if not advert:
        abort(404)

    return render_template('advert/details.html', advert=advert, images_folder=app.config['IMAGES_FOLDER'])

