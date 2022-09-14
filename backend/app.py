from unittest import skip
from Db import AttendanceDB
from env import env_config
from Logger import Logger
from flask import Flask, jsonify
from flask_cors import CORS
from colorama import init
init()


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


if __name__ == '__main__':
    app.run(host=env_config['WEB_HOST'], port=env_config['WEB_PORT'])
