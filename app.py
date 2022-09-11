from flask import Flask

from db import AttendanceDB
from env import env_config

app = Flask(__name__)
attendance_db = AttendanceDB()
attendance_db.connect()
attendance_db.load_db_from_participants_file()


@app.route("/")
def hello_world():
    return "<p>Hello World!</p>"


if __name__ == '__main__':
    app.run(host=env_config['WEB_HOST'], port=env_config['WEB_PORT'])
