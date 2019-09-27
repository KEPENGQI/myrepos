from flask import jsonify, request
from werkzeug.exceptions import abort
from datetime import datetime

from app import bp, db
from app.models import Booking, Slot
from app.decorators import login_required


@bp.route('/bookings')
@login_required
def get_all_bookings(**kwargs):
    booked_slots = []
    if 'DC=techlab' in kwargs['cas:distinguishedName']:
        bookings = Booking.query.filter_by(student_sam_account_name=kwargs['cas:sAMAccountName']).all()
        if bookings:
            for booking in bookings:
                slot = Slot.query.filter_by(id=booking.slot_id).first()
                if str(slot.datetime) > str(datetime.now()):
                    booking = [booking.serialize() for booking in Booking.query.filter_by(id=booking.id).all()]
                    booked_slots.append(booking)
            return jsonify(booked_slots)

    slots = Slot.query.filter_by(lecturer_sam_account_name=kwargs['cas:sAMAccountName'], status='Booked').all()

    for slot in slots:
        if str(slot.datetime) > str(datetime.now()):
            bookings = [booking.serialize() for booking in Booking.query.filter_by(slot_id=slot.id).all()]
            booked_slots.append(bookings)
    return jsonify(booked_slots)


@bp.route('/booking', methods=['POST'])
@login_required
def create_booking(**kwargs):
    required_params = ['slot_id', 'consultation_with', 'additional_note', 'reason']
    if 'DC=techlab' not in kwargs['cas:distinguishedName']:
        abort(401, "Unauthorized to access this resource")
    if not request.json:
        abort(400, "Request should be in JSON format")
    if not all(param in request.json for param in required_params):
        abort(400, "One or more required fields not found")

    # validate if any of the request param is empty
    for key in required_params:
        if request.json[key] is None or request.json[key] == "":
            abort(400, "One or more required param is empty")

    # validate if the provided slot id is not booked
    if Booking.query.filter_by(slot_id=request.json['slot_id']).first():
        abort(409, "Slot is already booked")

    slot = Slot.query.filter_by(id=request.json['slot_id'], status='Available'). \
        first_or_404(description='invalid slot_id supplied')

    bookings = Booking.query.filter_by(student_sam_account_name=kwargs['cas:sAMAccountName']).all()

    # for booking in bookings:
    #     if slot.datetime == Slot.query.filter_by(id=booking.slot_id).first().datetime:
    #         abort(409, "Student can not book two slots at same time")
    #
    # if (slot.datetime - datetime.now()).seconds <= 1:
    #     abort(409, "slot booking time already passed")

    new_booking = Booking.deserialize(request.json)
    new_booking.student_sam_account_name = kwargs['cas:sAMAccountName']
    new_booking.status = "Booked"
    new_booking.booking_datetime = datetime.now()

    slot.status = "Booked"
    slot.booking_slots.append(new_booking)
    db.session.add(new_booking)
    db.session.commit()

    return jsonify({"message": "Booking has been added successfully"}), 201


@bp.route('/booking/cancel', methods=['PUT'])
@login_required
def cancel_booking(**kwargs):
    required_params = ['booking_id', 'reason']
    if not request.json:
        abort(400, "Request should be in JSON format")
    if not all(param in request.json for param in required_params):
        abort(400, "One or more required fields not found")
    for key in required_params:
        if request.json[key] is None or request.json[key] == "":
            abort(400, "One or more required param is empty")

    booking = Booking.query.filter_by(id=request.json['booking_id']). \
        first_or_404(description='invalid booking_id supplied')
    if booking.status == 'Cancelled by lecturer' or booking.status == 'Cancelled by student':
        abort(400, "slot has already been cancelled by another user")

    if 'DC=techlab' in kwargs['cas:distinguishedName']:
        if booking.student_sam_account_name != kwargs['cas:sAMAccountName']:
            abort(401, "unauthorized to cancel the slot")
        booking.status = "Cancelled by student"
    else:
        if booking.booking_slot.lecturer_sam_account_name != kwargs['cas:sAMAccountName']:
            abort(401, "unauthorized to cancel the slot")
        booking.status = "Cancelled by lecturer"
        booking.reason = request.json['reason']

    db.session.commit()

    return jsonify({"message": "Slot has been successfully cancelled"}), 200


@bp.route('/remark', methods=['PUT'])
@login_required
def add_remark(**kwargs):
    if 'DC=techlab' in kwargs['cas:distinguishedName']:
        abort(401, "Unauthorized to access this resource")
    required_params = ['booking_id', 'remark', 'synced_to_gims']
    if not request.json:
        abort(400, "Request should be in JSON format")
    if not all(param in request.json for param in required_params):
        abort(400, "One or more required fields not found")
    for key in required_params:
        if request.json[key] is None or request.json[key] == "":
            abort(400, "One or more required param is empty")

    booking = Booking.query.filter_by(id=request.json['booking_id']). \
        first_or_404(description='invalid booking_id supplied')
    # validate that a remark can be only added to a booked slot
    if booking.booking_slot.status != 'Booked':
        abort(401, "You cannot add a remark to unbooked slot")
    # validate that the lecturer trying to add a remark is the slot owner
    if booking.booking_slot.lecturer_sam_account_name != kwargs['cas:sAMAccountName']:
        abort(401, "unauthorized to add remark the slot")

    booking.remark = request.json['remark']
    booking.synced_to_gims = request.json['synced_to_gims']
    db.session.commit()
    return jsonify({"message": "remark has been added"}), 200
