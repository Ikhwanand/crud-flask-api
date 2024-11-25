from flask import Flask, Response, request
import json
import pymongo
import os
from bson.objectid import ObjectId



app = Flask(__name__)

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# MongoDB Connection
MONGODB_URI = "mongodb://localhost:27017/"
try:
    client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Verify the connection
    client.server_info()
    db = client['thirty-days-of-python']
    print("Successfully connected to MongoDB!")
except pymongo.errors.ServerSelectionTimeoutError as err:
    print(f"Failed to connect to MongoDB: {err}")
    raise
except Exception as err:
    print(f"An error occurred while connecting to MongoDB: {err}")
    raise


@app.route('/api/v1.0/students', methods=['GET'])
def students():
    students_list = list(db.students.find())
    return Response(
        JSONEncoder().encode(students_list),
        mimetype='application/json'
    )


@app.route('/api/v1.0/students/<id>', methods=['GET'])
def single_student(id):
    student = db.students.find_one({'_id': ObjectId(id)})
    if student:
        return Response(
            JSONEncoder().encode(student),
            mimetype='application/json'
        )
    return Response(
        json.dumps({"error": "Student not found"}),
        mimetype='application/json',
        status=404
    )


@app.route('/api/v1.0/students/add', methods=['POST'])
def add_student():
    student_data = request.get_json()
    if len(student_data) == 1:
        db.students.insert_one(student_data[0])
        return Response(
            json.dumps({'success': 'Student added successfully'}),
            mimetype='application/json',
            status=201
        )
    elif len(student_data) > 1:
        db.students.insert_many(student_data)
        return Response(
            json.dumps({'success': 'Students added successfully'}),
            mimetype='application/json',
            status=201
        )
    else:
        return Response(
            json.dumps({'error': 'Data is invalid'}),
            mimetype='application/json',
            status=400
        )
    
@app.route('/api/v1.0/students/update/<id>', methods=['PUT'])
def update_student(id):
    student_data = request.get_json()
    if db.students.find_one({'_id': ObjectId(id)}) is None:
        return Response(
            json.dumps({'error': 'Student not found'}),
            mimetype='application/json',
            status=404
        )
    db.students.update_one({'_id': ObjectId(id)}, {'$set': student_data})
    return Response(
        json.dumps({'success': 'Student updated successfully'}),
        mimetype='application/json',
        status=200
    )

@app.route('/api/v1.0/students/delete/<id>', methods=['DELETE'])
def delete_student(id):
    if not db.students.find_one({'_id': ObjectId(id)}):
        return Response(
            json.dumps({'error': 'Student not found'}),
            mimetype='application/json',
            status=404
        )
    db.students.delete_one({'_id': ObjectId(id)})
    return Response(
        json.dumps({'success': 'Student deleted successfully'}),
        mimetype='application/json',
        status=200
    )

@app.route('/api/v1.0/students/update-all', methods=['PUT'])
def update_all_students():
    students_data = request.get_json()
    try:
        db.students.update_many({}, {'$set': students_data})
        return Response(
            json.dumps({'success': 'All students updated successfully'}),
            mimetype='application/json',
            status=200
        )
    except Exception as err:
        return Response(
            json.dumps({'error': str(err)}),
            mimetype='application/json',
            status=500
        )


if __name__ == '__main__':
    app.run(debug=True)