from datetime import datetime, timedelta

from flask import jsonify, request
from werkzeug.exceptions import abort

from app import bp, db
from app.decorators import login_required
from app.models import Slot, Location, SlotConfig, ArchivedSlot, ArchivedBooking


@bp.route('/slots', methods=['GET'])
@login_required
def get_slots(**kwargs):
    lecturer = request.args.get("lecturer_sam_account_name")
    if not lecturer:
        abort(400, "lecturer_sam_account_name param not provided")

    duration = SlotConfig.query.first().slot_duration
    return jsonify([{
        "id": slot.location.id,
        "slot_id": slot.id,
        "start_time": slot.datetime,
        "end_time": slot.datetime + duration,
        "status": slot.status,
        "venue": slot.location.venue,
        "room_code": slot.location.room_code
    } for slot in Slot.query.filter_by(lecturer_sam_account_name=lecturer).all()])


@bp.route('/slot', methods=['POST'])
@login_required
def create_slot(**kwargs):
    # Validation check to allow only lecturers to open the slots
    # if 'DC=techlab' in kwargs['cas:distinguishedName']:
    #     return abort(401, "Unauthorized to access this resource")

    # The time limit the lecturer has when he creates a slot which is within 24 hours
    # add_time_limit = SlotConfig.query.first().slot_add_time_limit
    # A slot created by a lecturer cannot be within the time frame of another slot
    # duration = SlotConfig.query.first().slot_duration

    if not request.json:
        abort(400, "Request should be in JSON format")

    for slot in request.json:
        required_params = ['datetime', 'location_id']
        if not all(param in slot for param in required_params):
            abort(400, "One or more required fields not found")

        # validate if any of the request param is empty
        # for key in required_params:
        #     if slot[key] is None or slot[key] == "":
        #         abort(400, "One or more required param is empty")

        # Lecturer cannot create a slot in less than 24 hours
        # string_to_datetime_object = datetime.strptime(slot['datetime'], '%y-%m-%d %H:%M:%S')
        # if string_to_datetime_object - datetime.now() < add_time_limit:
        #     abort(400, "You cannot create a slot in less than 24 hours")

        location = Location.query.filter_by(id=slot['location_id']). \
            first_or_404(description='invalid location_id supplied')

        # # Check if the lecturer had previously made a slot at that same particular time
        # # if Slot.query.filter_by(datetime=slot['datetime'], lecturer_sam_account_name=kwargs['cas:sAMAccountName']) \
        # #         .first():
        #     abort(400, "You cannot create multiple slots at the same time")

        # Check if the lecturer is creating a slot when another one has not yet finished
        # slots = Slot.query.filter_by(lecturer_sam_account_name=kwargs['cas:sAMAccountName']).all()
        # for new_slot in slots:
        #     slot_end_time = new_slot.datetime + duration
        #
        #     # Variable used to find if the difference in time is positive
        #     duration2 = timedelta(seconds=1)
        #
        #     time_difference = slot_end_time - string_to_datetime_object
        #     if (time_difference < duration) and (time_difference > duration2) and new_slot.status != 'Cancelled':
        #         abort(400, "You cannot create a slot within the same time period of another slot unless that "
        #                    "slot has finished")

        new_slot = Slot.deserialize(slot)
        new_slot.status = "Available"

        new_slot.lecturer_sam_account_name = kwargs['cas:sAMAccountName']

        location.slots.append(new_slot)
        db.session.add(new_slot)
    db.session.commit()

    return jsonify({"message": "New slot has been added successfully"}), 201


@bp.route('/slot/cancel', methods=['PUT'])
@login_required
def cancel_slot(**kwargs):
    # if 'DC=techlab' in kwargs['cas:distinguishedName']:
    #     abort(401, "unauthorized to access this resource")

    cancel_time_limit = SlotConfig.query.first().slot_cancel_time_limit
    if not request.json:
        abort(400, "Request should be in JSON format")
    for slot in request.json:
        slot_id = slot.get('slot_id')
        if not slot_id:
            abort(400, "slot_id param is missing")
        slot = Slot.query.filter_by(id=slot_id) \
            .first_or_404(description='invalid slot_id or lecture name supplied')
        if slot.status == 'Completed' or slot.status == 'Cancelled':
            abort(400, "slot has either been cancelled or completed")
        # Lecturer cannot cancel a slot in less than 3 hours
        if (slot.datetime - datetime.now()) <= cancel_time_limit:
            abort(409, "slot cancel time already passed")
        slot.status = "Cancelled"
        db.session.commit()

    return jsonify({"message": "Slots have been successfully cancelled"}), 200


@bp.route('/slot/move_to_archives', methods=['POST'])
# @login_required
def move_slot(**kwargs):
    # if 'DC=techlab' in kwargs['cas:distinguishedName']:
    #     abort(401, "unauthorized to access this resource")

    # Fetch Slots that are 1 month old or older
    # For each slots
    #  1. Replicate the record as ArchivedSlot
    #  2. Fetch all of the bookings of each slot
    #     For each bookings
    #     1. Replicate the record as ArchivedBooking
    #     2. Mark the ArchivedBooking to be added to the database
    #     3. Mark the Booking to be deleted from the database
    #  3. Mark the ArchivedSlot to be added to the database
    #  4. Mark the Slot to be deleted from the database
    #  5. Save changes to database
    filter_function = datetime.today() - timedelta(days=30)
    slots_to_archive = Slot.query.filter(Slot.datetime < filter_function).all()
    for slot in slots_to_archive:

        new_archived_slot = ArchivedSlot()

        new_archived_slot.location_id = slot.location_id
        new_archived_slot.lecturer_sam_account_name = slot.lecturer_sam_account_name
        new_archived_slot.datetime = slot.datetime
        new_archived_slot.status = slot.status
        bookings = slot.booking_slots.all()
        for booking in bookings:
            new_archived_booking = ArchivedBooking()
            new_archived_booking.slot = new_archived_slot
            new_archived_booking.student_sam_account_name = booking.student_sam_account_name
            new_archived_booking.consultation_with = booking.consultation_with
            new_archived_booking.reason = booking.reason
            new_archived_booking.additional_note = booking.additional_note
            new_archived_booking.remark = booking.remark
            new_archived_booking.booking_datetime = booking.booking_datetime
            new_archived_booking.status = booking.status
            new_archived_booking.synced_to_gims = booking.synced_to_gims
            db.session.add(new_archived_booking)
            db.session.delete(booking)

        db.session.add(new_archived_slot)
        db.session.delete(slot)

    db.session.commit()
    return jsonify({"message": "Slots and bookings have been successfully moved to archives"}), 200
