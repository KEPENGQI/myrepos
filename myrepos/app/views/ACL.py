from flask import jsonify, request
from sqlalchemy import JSON
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from datetime import datetime, timedelta

from app import bp, db
from app.models import ACL
from app.decorators import login_required


@bp.route('/acl', methods=['GET'])
@login_required
def view_acl():
    acl = [acl.serialize() for acl in ACL.query.all()]
    return jsonify(acl)


@bp.route('/acl', methods=['POST'])
@login_required
def create_acl(**kwargs):
    required_params = ['sam_account_name', 'resource']
    if not request.json:
        abort(400, "Request should be in JSON format")
    if not all(param in request.json for param in required_params):
        abort(400, "One or more required fields not found")

    for key in required_params:
        if request.json[key] is None or request.json[key] == "":
            abort(400, "One or more required param is empty")

    new_acl = ACL.deserialize(request.json)
    db.session.add(new_acl)
    db.session.commit()

    return jsonify({"message": "New ACL has been added successfully"}), 201


@bp.route('acl', methods=['DELETE'])
@login_required
def delete_acl(**kwargs):
    acl_id = request.args.get('acl_id')
    if not acl_id:
        abort(400, "acl_id param is missing")

    acl_to_delete = ACL.query.filter_by(id=request.json['acl_id']).first()
    db.session.delete(acl_to_delete)
    db.session.commit()

    return jsonify({"message": "ACL has been successfully deleted"}), 200

    # return redirect("/acl")


@bp.route('acl', methods=['PUT'])
@login_required
def update_acl(**kwargs):
    acl_id = request.args.get('acl_id')
    if not acl_id:
        abort(400, "acl_id param is missing")

    required_params = ['sam_account_name', 'resource']
    if not request.json:
        abort(400, "Request should be in JSON format")
    if not all(param in request.json for param in required_params):
        abort(400, "One or more required fields not found")

    acl = ACL.query.filter_by(id=acl_id).first_or_404(description="Invalid acl_id provided")

    acl.sam_account_name = request.json['sam_account_name']
    acl.resource = request.json['resource']

    db.session.commit()

    return jsonify({"message": "ACL has been successfully updated"}), 200
