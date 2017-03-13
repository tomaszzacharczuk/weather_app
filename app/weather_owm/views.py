from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from ..models import Location
from .. import db
from . import weather_owm
from .forms import LocationForm, DeleteLocationForm


@weather_owm.route('/locations/add', methods=['GET', 'POST'])
def add():
    """Add or Edit location"""
    form = LocationForm()
    if form.validate_on_submit():
        new_location = Location.query.filter_by(name=form.location.data).first()
        if not new_location:
            new_location = Location(name=form.location.data)
        current_user.locations.append(new_location)
        db.session.add(current_user)
        flash('Location ' + form.location.data + ' has been added.')
        return redirect(url_for('weather_owm.locations'))
    return render_template('weather_owm/location.html', form=form)


@weather_owm.route('/locations/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    form = LocationForm()
    location = Location.query.get(id)

    if form.validate_on_submit():
        if location.users.count() > 1:
            current_user.locations.remove(location)
            new_location = Location(name=form.location.data)
            current_user.locations.append(new_location)
            db.session.add(current_user)
        else:
            location.name = form.location.data
            db.session.add(location)
        flash('Location has been updated.')
        return redirect(url_for('weather_owm.locations'))
    form.location.data = location.name
    return render_template('weather_owm/location.html', form=form, location=location)


@weather_owm.route('/locations/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    delete_form = DeleteLocationForm()
    location = Location.query.get(id)
    if delete_form.validate_on_submit():
        if current_user in location.users.all():
            if location.users.count() > 1:
                current_user.locations.remove(location)
                db.session.add(current_user)
            else:
                db.session.delete(location)
            flash(location.name + ' has been deleted.')
        else:
            flash("You don't owngiven location.")
        return redirect(url_for('weather_owm.locations'))
    return render_template('weather_owm/confirm_delete.html', form=delete_form, location=location)


@weather_owm.route('/locations')
def locations():
    locations = current_user.locations.all()
    return render_template('weather_owm/locations.html', locations=locations)
