from flask import Flask, jsonify

from db import AttendanceDB
from env import env_config

app = Flask(__name__)
attendance_db = AttendanceDB()
attendance_db.connect()
attendance_db.load_db_from_participants_file()


@app.route("/api/attendees")
def attendess():
    attendees = attendance_db.get_all_attendees()
    return jsonify(attendees)


@app.route("/api/attendance")
def attendance():
    attendance = attendance_db.get_attendance()
    return jsonify(attendance.todict())


if __name__ == '__main__':
    app.run(host=env_config['WEB_HOST'], port=env_config['WEB_PORT'])
