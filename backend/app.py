from Db import AttendanceDB
from env import env_config
from flask import Flask, jsonify
from flask_cors import CORS
from colorama import init
init()


app = Flask(__name__)
CORS(app, origins="*")

attendance_db = AttendanceDB()
attendance_db.connect()


@app.route("/attendees")
def attendess():
    attendees = attendance_db.get_all_attendees()
    return jsonify(attendees)


@app.route("/attendance")
def attendance():
    attendance = attendance_db.get_attendance()
    return jsonify(attendance)


@app.route('/load_participant_csv_files_to_db')
def load_participants_csv_files():
    attendance_db.load_participants()


attendance_db.load_participants()
# if __name__ == '__main__':
# app.run(host=env_config['WEB_HOST'], port=env_config['WEB_PORT'])
# attendance_db.load_participants()
