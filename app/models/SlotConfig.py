from app import db


class SlotConfig(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    slot_duration = db.Column(db.DateTime, index=True)
    slot_cancel_time_limit = db.Column(db.DateTime, index=True)
    slot_add_time_limit = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<SlotConfig {} "{}">'.format(self.id, self.slot_duration, self.slot_cancel_time_limit,
                                             self.slot_add_time_limit)

    def serialize(self):
        return {
            "id": self.id,
            "slot_duration": self.slot_duration,
            "slot_cancel_time_limit": self.slot_cancel_time_limit,
            "slot_add_time_limit": self.slot_add_time_limit
        }

    @staticmethod
    def deserialize(request_json):
        return SlotConfig(
            slot_duration=request_json['slot_duration'],
            slot_cancel_time_limit=request_json['slot_cancel_time_limit'],
            slot_add_time_limit=request_json['slot_add_time_limit']
        )
