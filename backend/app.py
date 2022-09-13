from flask import Flask, jsonify
from flask_cors import CORS

from db import AttendanceDB
from env import env_config

app = Flask(__name__)
CORS(app, origins="*")

attendance_db = AttendanceDB()
if attendance_db.connect():
    attendance_db.load_db_from_participants_file()


@app.route("/attendees")
def attendess():
    attendees = attendance_db.get_all_attendees()
    return jsonify(attendees)


@app.route("/attendance")
def attendance():
    attendance = attendance_db.get_attendance()
    return jsonify(attendance)


@app.route('/test')
def test():
    return jsonify({'Test': 'test'})


if __name__ == '__main__':
    app.run(host=env_config['WEB_HOST'], port=env_config['WEB_PORT'])
