from flask import jsonify, request
from werkzeug.exceptions import abort

from app import bp, db
from app.models import SlotConfig
from app.decorators import login_required


@bp.route('/slotconfig')
def get_all_slotconfigs():
    slotconfigs = [slotconfig.serialize() for slotconfig in SlotConfig.query.all()]
    return jsonify(slotconfigs)


@bp.route('/slotconfig', methods=['POST'])
def create_slot_config():
    required_params = ['slot_duration', 'slot_cancel_time_limit', 'slot_add_time_limit']
    if not request.json:
        abort(400, "Request should be in JSON format")
    if not all(param in request.json for param in required_params):
        abort(400, "One or more required fields not found")

    # validate if any of the request param is empty
    for key in required_params:
        if request.json[key] is None or request.json[key] == "":
            abort(400, "One or more required param is empty")
    new_slotconfig = SlotConfig.deserialize(request.json)
    db.session.add(new_slotconfig)
    db.session.commit()
    return jsonify({"message": "slotconfig has been added successfully"}), 201


@bp.route('/slotconfig', methods=['PUT'])
def update_slot_config():
    slotconfig_id = ['slotconfig_id']
    if not request.json:
        abort(400, "Request should be in JSON format")
    if not slotconfig_id:
        abort(400, "acl_id param is missing")
    slotconfig = SlotConfig.query.filter_by(id=request.json['slotconfig_id']). \
        first_or_404(description='invalid booking_id supplied')
    slotconfig.slot_duration = request.json['slot_duration']
    slotconfig.slot_cancel_time_limit = request.json['slot_cancel_time_limit']
    slotconfig.slot_add_time_limit = request.json['slot_add_time_limit']
    db.session.commit()

    return jsonify({"message": "SlotConfig update successfully"}), 200


@bp.route('slotconfig', methods=['DELETE'])
def delete_slot_config():
    slotconfig_id = ['slotconfig_id']
    if not request.json:
        abort(400, "Request should be in JSON format")
    if not slotconfig_id:
        abort(400, "slotconfig_id param is missing")
    slotconfig = SlotConfig.query.filter_by(id=request.json['slotconfig_id']). \
        first_or_404(description='invalid booking_id supplied')
    db.session.delete(slotconfig)
    db.session.commit()

    return jsonify({"message": "slotconfig has been successfully deleted"}), 200
