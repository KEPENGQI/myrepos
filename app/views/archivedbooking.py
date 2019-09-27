from datetime import datetime, timedelta

from flask import jsonify

from app import bp, db
from app.models import Booking, ArchivedBooking


@bp.route('/archived_booking', methods=['GET', 'POST', 'DELETE'])
# @login_required
def archived_booking(**kwargs):
    filter_after = datetime.today() - timedelta(days=30)
    bookings = Booking.query.filter(Booking.booking_datetime <= filter_after)
    for booking in bookings:
        new_archived_booking = ArchivedBooking()
        new_archived_booking.archived_slot_id = booking.slot_id
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
    db.session.commit()
    return jsonify({"message": "All bookings have move to archived_booking successfully"}), 201
