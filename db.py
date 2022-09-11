from decimal import Decimal
from sqlalchemy import create_engine, Column, String, Integer, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import database_exists, create_database
from abc import ABC, abstractmethod
import os

from attendance import get_attendance_dict_result
from env import env_config


class DB(ABC):
    def __init__(self) -> None:
        self.base = declarative_base()
        self.session = sessionmaker()
        self.engine = None

    @abstractmethod
    def connect(self) -> None:
        pass


class AttendanceDB(DB):
    def __init__(self) -> None:
        super().__init__()

        class Student(self.base):
            __tablename__ = 'students'
            id = Column(Integer(), primary_key=True)
            name = Column(String(25), nullable=False)
            attendance_duration = Column(DECIMAL(7, 2), nullable=False)
            attendance_percentage = Column(DECIMAL(5, 2), nullable=False)
        self.model_student = Student

        class Attendance(self.base):
            __tablename__ = 'attendance'
            id = Column(Integer(), primary_key=True)
            total_duration = Column(DECIMAL(7, 2), nullable=False)
        self.model_attendance = Attendance

    def connect(self) -> None:
        try:
            hostname = env_config['SQL_HOST']
            password = env_config['SQL_PASSWORD']
            username = env_config['SQL_USER']
            dbname = env_config['SQL_DBNAME']
            engine = create_engine(
                f"mysql://{username}:{password}@{hostname}/{dbname}", echo=True)
            if not database_exists(engine.url):
                create_database(engine.url)
            self.engine = engine
            self.base.metadata.create_all(engine)
        except:
            print('Unable to connect to database! check env variables / sql server is up')
            print(
                f"Tried to connect to: mysql://{username}:<PASSWORD>@{hostname}/{dbname}")
            return

    def insert_or_update_students(self, students: dict) -> bool:
        try:
            local_session = self.session(bind=self.engine)
            students_to_insert = []
            for student in students.keys():
                if self._student_in_table(student):
                    self._update_student_durations(students[student], student)
                else:
                    students_to_insert.append(self.model_student(
                        name=student, attendance_duration=Decimal(students[student]['attendance_duration']), attendance_percentage=Decimal(students[student]['attendance_percentage'])))
            local_session.add_all(students_to_insert)
            local_session.commit()
            return True
        except Exception as ex:
            print('Unable to insert into students table!')
            return False

    def _student_in_table(self, student_name) -> bool:
        local_session = self.session(bind=self.engine)
        student_entry = local_session.query(self.model_student).filter(
            self.model_student.name == student_name).first()
        if student_entry:
            return True
        return False

    def _update_student_durations(self, student_dict, student_name):
        local_session = self.session(bind=self.engine)
        student_entry = local_session.query(self.model_student).filter(
            self.model_student.name == student_name).first()
        student_entry.attendance_duration += Decimal(
            student_dict['attendance_duration'])
        student_entry.attendance_percentage = Decimal(
            student_dict['attendance_percentage'])

    def insert_or_update_attendance(self, meeting_minutes, loading_from_file_flag) -> bool:
        try:
            local_session = self.session(bind=self.engine)
            attendance = local_session.query(self.model_attendance).first()
            if attendance and loading_from_file_flag:
                attendance.total_duration = meeting_minutes
                local_session.commit()
                return True
            elif attendance:
                attendance.total_duration += meeting_minutes
                local_session.commit()
                return True
            else:
                new_entry = self.model_attendance(
                    total_duration=meeting_minutes)
                local_session.add(new_entry)
                local_session.commit()
                return True
        except Exception as ex:
            print('Unable to insert into attendance table!')
            return False

    def get_total_meetings_duration(self) -> Decimal:
        local_session = self.session(bind=self.engine)
        attendance = local_session.query(self.model_attendance).first()
        return attendance['total_duration']

    def load_db_from_participants_file(self) -> bool:
        attendance_dict = get_attendance_dict_result(os.getcwd())
        total_minutes = attendance_dict['total_meetings_duration']
        attendance_dict.pop('total_meetings_duration')
        if not attendance_dict:
            return False
        else:
            self.insert_or_update_students(attendance_dict)
            self.insert_or_update_attendance(Decimal(total_minutes), True)
            return True
