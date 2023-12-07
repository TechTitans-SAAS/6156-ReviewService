from datetime import datetime


class Review:
    def __init__(self, item_id, description, user_id, _id):
        self._id = _id
        self.item_id = item_id
        self.description = description
        self.user_id = user_id
        self.date_created = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "item_id": self.item_id,
            "description": self.description,
            "user_id": self.user_id,
            "date_created": self.date_created
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            item_id=data["item_id"],
            description=data["description"],
            user_id=data["user_id"],
            _id=data["_id"]
        )