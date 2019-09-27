from app import db


class Location (db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    venue = db.Column(db.String(50), nullable=False,)
    room_code = db.Column(db.String(50), nullable=False)
    slots = db.relationship('Slot', backref='location', lazy='dynamic')

    def __repr__(self):
        return '<Location {} "{}">'.format(self.id, self.venue, self.room_code)

    def serialize(self):
        return {
            "id": self.id,
            "venue": self.venue,
            "room_code": self.room_code
        }

    @staticmethod
    def deserialize(request_json):
        return Location(
            venue=request_json['venue'],
            room_code=request_json['room_code']
        )
