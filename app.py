from flask import Flask

from db import AttendanceDB
from env import env_config

app = Flask(__name__)

attendance_db = AttendanceDB()


@app.route("/")
def hello_world():
    attendance_db.connect()
    attendance_db.insert_or_update_students(
        [{'name': 'Tomer', 'attendance_duration': 22.3, 'attendnace_percentage': 33.3}])
    return "<p>Hello World!</p>"


if __name__ == '__main__':
    app.run(host=env_config['WEB_HOST'], port=env_config['WEB_PORT'])
