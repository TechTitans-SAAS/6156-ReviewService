from graphene import ObjectType, String, Schema, List, Field, ID, InputObjectType, DateTime
from Reviews import db
from bson import ObjectId

class Review(ObjectType):
    id = ID()
    item_id = String()
    description = String()
    user_id = String()
    date_created = DateTime()

    def resolve_id(self, info):
        return str(self.id)

class Query(ObjectType):
    reviews_by_item = List(Review, item_id=String(required=True), page=String(required=True))

    def resolve_reviews_by_item(root, info, item_id, page):
        try:
            reviews_data = db.Reviews.find({"item_id": item_id}).sort([("date_created", -1)]).skip((int(page) - 1) * 10).limit(10)
            # Convert data from MongoDB to ReviewModel instances
            reviews = [Review(id=str(review.pop('_id')), **review) for review in reviews_data]
            return reviews
        except Exception as e:
            raise Exception(f"Failed to get review: {str(e)}")
    
    review_by_id = Field(Review, review_id=String(required=True))

    def resolve_review_by_id(root, info, review_id):
        review_id_object = ObjectId(review_id)
        try:
            review = db.Reviews.find_one({"_id": review_id_object})
            if review == None:
                return "Review does not exist", 404
            review["_id"] = str(review["_id"])
            return Review(id=str(review.pop('_id')), **review)
        except Exception as e:
            raise Exception(f"Failed to get review: {str(e)}")


schema = Schema(query=Query)