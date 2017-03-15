from flask import g, jsonify, request, url_for
from ..models import Location, Weather
from .errors import unauthorized
from . import api
from .. import db


@api.route('/locations')
def get_locations():
    page = request.args.get('page', 1, type=int)
    pagination = g.current_user.locations.paginate(page=page, per_page=20)
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_locations', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_locations', page=page + 1, _external=True)
    return jsonify({
        'locations': [location.serialize for location in pagination.items],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/locations/<int:location_id>/temp')
def get_temperature(location_id):
    page = request.args.get('page', 1, type=int)
    location = Location.query.get_or_404(location_id)
    if not g.current_user.locations.filter_by(id=location_id).first():
        return unauthorized("Location is not assigned to current user.")
    pagination = location.weather.order_by(Weather.date.desc()).paginate(page=page, per_page=40)
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_temperature', location_id=location_id, page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_temperature', location_id=location_id, page=page + 1, _external=True)
    return jsonify({
        'temperature': [temp.serialize_temperature for temp in pagination.items],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/locations/<int:location_id>/wind')
def get_wind(location_id):
    page = request.args.get('page', 1, type=int)
    location = Location.query.get_or_404(location_id)
    if not g.current_user.locations.filter_by(id=location_id).first():
        return unauthorized("Location is not assigned to current user.")
    pagination = location.weather.order_by(Weather.date.desc()).paginate(page=page, per_page=40)
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_wind', location_id=location_id, page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_wind', location_id=location_id, page=page + 1, _external=True)
    return jsonify({
        'temperature': [wind.serialize_wind for wind in pagination.items],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/locations/', methods=['POST'])
def new_location():
    location = Location.query.filter_by(name=request.json.get('name')).first()
    if not location:
        location = Location.from_json(request.json)
    location.users.append(g.current_user)
    db.session.add(location)
    db.session.commit()
    return jsonify(location.serialize)


@api.route('/locations/<int:location_id>', methods=['PUT'])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    if not g.current_user.locations.filter_by(id=location_id).first():
        return unauthorized("Location is not assigned to current user.")
    if location.users.count() > 1:
        g.current_user.locations.remove(location)
        location = Location.from_json(request.json)
        location.users.append(g.current_user)
        db.session.add(current_user)
        db.session.add(location)
    else:
        location.name = request.json.get('name')
        db.session.add(location)
    db.session.commit()
    return jsonify(location.serialize)
