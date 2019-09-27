from app import db


class Slot(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    lecturer_sam_account_name = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(50))
    booking_slots = db.relationship('Booking', backref='booking_slot', lazy='dynamic')

    def __repr__(self):
        return '<Slot {}>'.format(self.id, self.lecturer_sam_account_name, self.datetime, self.status)

    def serialize(self):
        return {
            "id": self.id,
            "location_id": self.location_id,
            "lecturer_sam_account_name": self.lecturer_sam_account_name,
            "datetime": self.datetime,
            "status": self.status
        }

    @staticmethod
    def deserialize(request_json):
        return Slot(
            datetime=request_json['datetime']
        )
