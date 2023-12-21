from Reviews import app
from flask import jsonify, make_response, request
from graphql import graphql
from bson import ObjectId
import google.auth.crypt
import time
import requests
from google.auth import jwt
from Reviews import db
from datetime import datetime
from Reviews.schema import schema

REVIEWS_PER_PAGE = 10


def verify_token(token):
    audience = "https://thriftustore-api-2ubvdk157ecvh.apigateway.user-microservice-402518.cloud.goog"
    # Public key URL for the service account
    public_key_url = 'https://www.googleapis.com/robot/v1/metadata/x509/jwt-182@user-microservice-402518.iam.gserviceaccount.com'
    
    # Fetch the public keys from the URL
    response = requests.get(public_key_url)
    public_keys = response.json()
    try:
        # Verify the JWT token using the fetched public keys
        decoded_token = jwt.decode(token, certs=public_keys, audience=audience)
        # The token is verified, and 'decoded_token' contains the decoded information
        return decoded_token
    except Exception as e:
        print(f"Error in decoding token: {str(e)}")
        return None

# page should start from 1
@app.route("/<string:item_id>/reviews/<int:page>", methods = ['GET'])
def get_reviews_for_item(item_id, page):
    skip = (page - 1) * REVIEWS_PER_PAGE
    try:
        Reviews = list(db.Reviews.find({"item_id": item_id}).sort("date_created", -1).skip(skip).limit(REVIEWS_PER_PAGE))
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
    if 'Authorization' not in request.headers: return "Unauthorized user", 401
    token = request.headers.get('Authorization').split()[1]
    if (verify_token(token)) is None:
        return "Unauthorized user", 401
    
    response_data = {
        "description": request.form.get('description'),
        "item_id": request.form.get('item_id'),
        "user_id": str(verify_token(token)['id']),
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
    if 'Authorization' not in request.headers: return "Unauthorized user", 401
    token = request.headers.get('Authorization').split()[1]
    if (verify_token(token)) is None:
        return "Unauthorized user", 401
    
    try:
        review = db.Reviews.find_one_and_delete({"_id": ObjectId(review_id), "user_id": str(verify_token(token)['id'])})
        if review is None:
            return "Review does not exist", 404
        review["_id"] = str(review["_id"])


    # Return JSON response
        response = make_response(jsonify(review))
        response.headers["Content-Type"] = "application/json"
        return response, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/reviews/<string:review_id>", methods = ['PUT'])
def update_review_by_id(review_id):
    if 'Authorization' not in request.headers: return "Unauthorized user", 401
    token = request.headers.get('Authorization').split()[1]
    if (verify_token(token)) is None:
        return "Unauthorized user", 401
    
    review_id_object = ObjectId(review_id)
    try:
        # Retrieve updated data from the request form
        updated_data = {}
        for key, value in request.form.items():
            # Ignore fields with empty values
            if value and key != 'user_id' and key != 'item_id':
                updated_data[key] = value


        review = db.Reviews.update_one({"_id": review_id_object}, {'$set': updated_data})
        if review.modified_count > 0:
            # Fetch the updated document from the database
            review = db.Reviews.find_one({'_id': ObjectId(review_id), "user_id": str(verify_token(token)['id'])})
            review["_id"] = str(review["_id"])
            response = make_response(jsonify(review))
            response.headers["Content-Type"] = "application/json"
            return response, 200
        else:
            # Return response indicating no updates were made
            return jsonify({'message': 'No updates made'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/graphql', methods=['POST'])
def graphql():
    try:
        data = request.get_json()
        result = schema.execute(data['query'], context_value={'db': db})
        print(result.data)
        return jsonify(result.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500