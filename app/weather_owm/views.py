from flask import render_template, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from ..models import Location, Weather
from .. import db
from . import weather_owm
from .forms import LocationForm, DeleteLocationForm


@weather_owm.route('/locations/add', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
def locations():
    locations = current_user.locations.order_by(Location.name.asc()).all()
    return render_template('weather_owm/locations.html', locations=locations)


@weather_owm.route('/_graph/get_temperature/<int:location_id>')
@login_required
def _get_temperature(location_id):
    location = current_user.locations.filter_by(id=location_id).first()
    if not location:
        return jsonify({})
    data = [w.serialize_temperature for w in location.weather.order_by(Weather.date.desc()).limit(40)]

    return jsonify({
        'element': 'location-temp-' + str(location_id),
        'data': data,
        'xkey': 'date',
        'ykeys': ['temperature_min', 'temperature', 'temperature_max'],
        'labels': ['Min Temp', 'Med Temp', 'Max Temp'],
    })


@weather_owm.route('/_graph/get_wind/<int:location_id>')
@login_required
def _get_wind(location_id):
    location = current_user.locations.filter_by(id=location_id).first()
    if not location:
        return jsonify({})
    data = [w.serialize_wind for w in location.weather.order_by(Weather.date.desc()).limit(40)]
    return jsonify({
        'element': 'location-wind-' + str(location_id),
        'data': data,
        'xkey': 'date',
        'ykeys': ['wind'],
        'labels': ['Wind'],
    })
