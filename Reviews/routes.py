from Reviews import app, mongodb_client
from flask import jsonify, make_response, render_template, request, redirect, flash, url_for

from bson import ObjectId

from Reviews import db
from datetime import datetime
REVIEWS_PER_PAGE = 10

# page should start from 0
@app.route("/reviews/<int:page>", methods = ['GET'])
def get_reviews(page):
    skip = (page - 1) * REVIEWS_PER_PAGE
    try:
        Reviews = list(db.Reviews.find({}).sort("date_created", -1).skip(skip).limit(REVIEWS_PER_PAGE))
        for item in Reviews:
            item["_id"] = str(item["_id"])
        response_data = {"Reviews": Reviews}

    # Return JSON response
        response = make_response(jsonify(response_data))
        response.headers["Content-Type"] = "application/json"
        return response, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route("/reviews/<string:review_id>", methods = ['GET'])
def get_review_by_id(review_id):
    review_id_object = ObjectId(review_id)
    try:
        review = db.Reviews.find_one({"_id": review_id_object})
        if review is None:
            return "Review does not exist", 404
        review["_id"] = str(review["_id"])


    # Return JSON response
        response = make_response(jsonify(review))
        response.headers["Content-Type"] = "application/json"
        return response, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route("/reviews", methods = ['POST'])
def create_review():

    response_data = {
        "description": request.form.get('description'),
        "item_id": request.form.get('item_id'),
        "user_id": request.form.get('user_id'),
        "date_created": datetime.utcnow()
    }


    try:

        result = db.Reviews.insert_one(response_data)
        inserted_id = str(result.inserted_id)
        response_data['_id'] = inserted_id

        response = make_response(jsonify(response_data))
        response.headers["Content-Type"] = "application/json"
        return response, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    
       


@app.route("/reviews/<string:review_id>", methods = ['DELETE'])
def delete_review(review_id):
    try:
        review = db.Reviews.find_one_and_delete({"_id": ObjectId(review_id)})
        if review is None:
            return "Review does not exist", 404
        review["_id"] = str(review["_id"])


    # Return JSON response
        response = make_response(jsonify(review))
        response.headers["Content-Type"] = "application/json"
        return response, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/reviews/<string:review_id>", methods = ['PATCH'])
def update_review_by_id(review_id):
    review_id_object = ObjectId(review_id)
    try:
        # Retrieve updated data from the request form
        updated_data = {}
        for key, value in request.form.Reviews():
            # Ignore fields with empty values
            if value and key != 'user_id' and key != 'item_id':
                updated_data[key] = value


        review = db.Reviews.update_one({"_id": review_id_object}, {'$set': updated_data})
        if review.modified_count > 0:
            # Fetch the updated document from the database
            review = db.Reviews.find_one({'_id': ObjectId(review_id)})
            review["_id"] = str(review["_id"])
            response = make_response(jsonify(review))
            response.headers["Content-Type"] = "application/json"
            return response, 200
        else:
            # Return response indicating no updates were made
            return jsonify({'message': 'No updates made'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500