from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class LocationForm(FlaskForm):
    location = StringField('Location name', validators=[DataRequired()])
    submit = SubmitField('Add Location')


class DeleteLocationForm(FlaskForm):
    submit = SubmitField('Delete')
