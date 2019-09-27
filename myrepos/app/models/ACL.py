from app import db


class ACL (db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sam_account_name = db.Column(db.String(50), nullable=False)
    resource = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<ACL {} "{}">'.format(self.id, self.sam_account_name, self.resource)

    def serialize(self):
        return {
            "id": self.id,
            "sam_account_name": self.sam_account_name,
            "resource": self.resource
        }

    @staticmethod
    def deserialize(request_json):
        return ACL(
            sam_account_name=request_json['sam_account_name'],
            resource=request_json['resource']
        )
