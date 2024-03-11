from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_basicauth import BasicAuth
from urllib.parse import quote_plus
from bson import ObjectId


app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'tunyawut'
app.config['BASIC_AUTH_PASSWORD'] = '1234'
basic_auth = BasicAuth(app)

# Escape username and password
username = quote_plus("tunyawutm")
password = quote_plus("@98765431Za")

# Connect to MongoDB
client = MongoClient(f"mongodb+srv://{username}:{password}@cluster0.ahdiapf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["students"]
collection = db["std_info"]

# Welcome page
@app.route("/")
def welcome():
    return "<p>Welcome to Student Management API</p>"

# Get all students
@app.route("/students", methods=["GET"])
@basic_auth.required
def get_all_students():
    try:
        all_students = list(collection.find({}, {"_id": 1, "fullname": 1, "major": 1, "gpa": 1}))
        return jsonify(all_students)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get a specific student by ID
@app.route("/students/<string:std_id>", methods=["GET"])
@basic_auth.required
def get_id_student(std_id):
    try:
        db = client["students"]
        collection = db["std_info"]
        all_student = list(collection.find())
        std = next((s for s in all_student if s["_id"] == std_id), None)
        if(std):
            return jsonify(std)
        else:
            return jsonify({"error":"Student not found"}), 404
    except Exception as e:
        print(e)

# Add a new student
@app.route("/students", methods=["POST"])
@basic_auth.required
def add_student():
    try:
        data = request.get_json()
        new_student = {
            "_id": data["_id"],
            "fullname": data["fullname"],
            "major": data["major"],
            "gpa": data["gpa"]
        }

        existing_student = collection.find_one({"_id": data["_id"]})
        if existing_student:
            return jsonify({"error": "Cannot create new student"}), 500

        collection.insert_one(new_student)
        return jsonify(new_student), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update a student
@app.route("/students/<string:std_id>", methods=["PUT"])
@basic_auth.required
def update_student(std_id):
    try:
        data = request.get_json()
        updated_student = {
            "$set": {
                "fullname": data["fullname"],
                "major": data["major"],
                "gpa": data["gpa"]
            }
        }
        result = collection.update_one({"_id": std_id}, updated_student)
        
        if result.modified_count > 0:
            # Retrieve the updated student from the database
            updated_data = collection.find_one({"_id": std_id})
            
            # Include the unchanged student ID in the response
            updated_data["_id"] = str(updated_data["_id"])
            
            return jsonify(updated_data), 200
        else:
            return jsonify({"error": "Student not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a student
@app.route("/students/<string:std_id>", methods=["DELETE"])
@basic_auth.required
def delete_student(std_id):
    try:
        db = client["students"]
        collection = db["std_info"]
        all_student = list(collection.find())
        if(next((s for s in all_student if s["_id"] == std_id), None)):
            collection.delete_one({"_id":std_id})
            return jsonify({"message":"Student deleted successfully"}),200
        else:
            return jsonify({"error":"Student not found"}),404
        
    except Exception as e:
        print(e)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)

print("disconnected")
client.close()