from app import db


class ArchivedSlot(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    lecturer_sam_account_name = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(50))
    booking_slots = db.relationship('ArchivedBooking', backref='slot', lazy='dynamic')

    def __repr__(self):
        return '<ArchivedSlot {}>'.format(self.id, self.location_id, self.lecturer_sam_account_name, self.datetime, self.status)



