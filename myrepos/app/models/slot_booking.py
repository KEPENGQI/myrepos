from app import db


class Booking(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'))
    student_sam_account_name = db.Column(db.String(50), nullable=False)
    consultation_with = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(50), nullable=False)
    additional_note = db.Column(db.String(50), nullable=False)
    booking_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    remark = db.Column(db.String(50))
    synced_to_gims = db.Column(db.String(50))

    def __repr__(self):
        return '<Booking {} "{}">'.format(self.id, self.student_sam_account_name, self.consultation_with, self.reason,
                                          self.additional_note, self.booking_datetime, self.status, self.remark,
                                          self.synced_to_gims)

    def serialize(self):
        return {
            "id": self.id,
            "student_sam_account_name": self.student_sam_account_name,
            "consultation_with": self.consultation_with,
            "slot_id": self.slot_id,
            "reason": self.reason,
            "additional_note": self.additional_note,
            "booking_datetime": self.booking_datetime,
            "status": self.status,
            "remark": self.remark,
            "synced_to_gims": self.synced_to_gims
        }

    @staticmethod
    def deserialize(request_json):
        return Booking(
            student_sam_account_name=request_json['student_sam_account_name'],
            consultation_with=request_json['consultation_with'],
            additional_note=request_json['additional_note'],
            reason=request_json['reason'],
        )
