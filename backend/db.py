from decimal import Decimal
from sqlalchemy import create_engine, Column, String, Integer, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy_serializer import SerializerMixin
from abc import ABC, abstractmethod
import os

from attendance import get_attendance_dict_result
from env import env_config


class DB(ABC):
    def __init__(self) -> None:
        self.base = declarative_base()
        self.session = None
        self.engine = None
        self.students_changed = False
        self.attendance_changed = False

    @abstractmethod
    def connect(self) -> None:
        pass


class AttendanceDB(DB):
    def __init__(self) -> None:
        super().__init__()
        self.students = None
        self.attendance = None
        self.connected = False

        class Student(self.base, SerializerMixin):
            __tablename__ = 'students'
            id = Column(Integer(), primary_key=True)
            name = Column(String(25), nullable=False)
            attendance_duration = Column(DECIMAL(7, 2), nullable=False)
            attendance_percentage = Column(DECIMAL(5, 2), nullable=False)
        self.model_student = Student

        class Attendance(self.base, SerializerMixin):
            __tablename__ = 'attendance'
            id = Column(Integer(), primary_key=True)
            total_duration = Column(DECIMAL(7, 2), nullable=False)
        self.model_attendance = Attendance

    def connect(self) -> bool:
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
            self.session = sessionmaker(self.engine)
            self.base.metadata.create_all(engine)
            self.connected = True
            return True
        except Exception as ex:
            print(
                'ERROR! Unable to connect to database! check env variables / sql server is up')
            print(
                f"Tried to connect to: mysql://{username}:<PASSWORD>@{hostname}/{dbname}")
            print(ex)
            return False

    def insert_or_update_students(self, students: dict) -> bool:
        try:
            with self.session() as local_session:
                students_to_insert = []
                for student in students.keys():
                    if self._student_in_table(student):
                        self._update_student_durations(
                            students[student], student)
                    else:
                        students_to_insert.append(self.model_student(
                            name=student, attendance_duration=Decimal(students[student]['attendance_duration']), attendance_percentage=Decimal(students[student]['attendance_percentage'])))
                local_session.add_all(students_to_insert)
                local_session.commit()
                return True
        except Exception as ex:
            self.close_unexpected_db_session(local_session)
            print('Unable to insert into students table!')
            print(ex)
            return False

    def close_unexpected_db_session(local_session):
        local_session.rollback()
        local_session.close_all()

    def _student_in_table(self, student_name) -> bool:
        with self.session() as local_session:
            student_entry = local_session.query(self.model_student).filter(
                self.model_student.name == student_name).first()
            if student_entry:
                return True
            return False

    def _update_student_durations(self, student_dict, student_name):
        with self.session() as local_session:
            student_entry = local_session.query(self.model_student).filter(
                self.model_student.name == student_name).first()
            if student_entry:
                student_entry.attendance_duration += Decimal(
                    student_dict['attendance_duration'])
                student_entry.attendance_percentage = Decimal(
                    student_dict['attendance_percentage'])

    def insert_or_update_attendance(self, meeting_minutes, loading_from_file_flag) -> bool:
        try:
            with self.session() as local_session:
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
            self.close_unexpected_db_session(local_session)
            print('Unable to insert into attendance table!')
            print(ex)
            return False

    def get_total_meetings_duration(self) -> Decimal:
        with self.session() as local_session:
            attendance = local_session.query(self.model_attendance).first()
            return attendance['total_duration']

    def load_db_from_participants_file(self) -> bool:
        self.students_changed = True
        self.attendance_changed = True
        attendance_dict = get_attendance_dict_result(os.getcwd())
        total_minutes = attendance_dict['total_meetings_duration']
        attendance_dict.pop('total_meetings_duration')
        if not attendance_dict:
            return False
        else:
            self.insert_or_update_students(attendance_dict)
            self.insert_or_update_attendance(Decimal(total_minutes), True)
            return True

    def get_all_attendees(self) -> list[dict]:
        if not self.connected:
            return []
        if not self.students_changed:
            return self.students
        with self.session() as local_session:
            attendees = local_session.query(self.model_student).all()
            result = []
            for attendee in attendees:
                result.append(attendee.to_dict())
            self.students_changed = False
            self.students = result
            return result

    def get_attendance(self) -> dict:
        if not self.connected:
            return {
                'total_duration': 0
            }
        if not self.attendance_changed:
            return self.attendance
        with self.session() as local_session:
            attendance = local_session.query(self.model_attendance).all()
            self.attendance_changed = False
            self.attendance = attendance[0].to_dict()
            return attendance[0].to_dict()
