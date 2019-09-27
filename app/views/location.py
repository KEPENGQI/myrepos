from flask import jsonify, request
from werkzeug.exceptions import abort

from app import bp, db
from app.models import Location
from app.decorators import login_required


@bp.route('/locations')
@login_required
def get_all_locations(**kwargs):
    locations = [location.serialize() for location in Location.query.all()]
    return jsonify(locations)


@bp.route('/location', methods=['POST'])
# @login_required
def create_location(**kwargs):
    # if 'DC=techlab' in kwargs['cas:distinguishedName']:
    #     return abort(401, "Unauthorized to access this resource")
    required_params = ['venue', 'room_code']
    if not request.json:
        abort(400, "Request should be in JSON format")
    if not all(param in request.json for param in required_params):
        abort(400, "One or more required fields not found")

    # validate if any of the request param is empty
    for key in required_params:
        if request.json[key] is None or request.json[key] == "":
            abort(400, "One or more required param is empty")

    # validate if the chosen venue and room_code already exists
    if Location.query.filter_by(venue=request.json['venue'], room_code=request.json['room_code']).first():
        abort(409, "Location already exists")

    new_location = Location.deserialize(request.json)
    db.session.add(new_location)
    db.session.commit()

    return jsonify({"message": "Location has been added successfully"}), 201
