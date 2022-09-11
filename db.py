from decimal import Decimal
from sqlalchemy import create_engine, Column, String, Integer, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
from abc import ABC, abstractmethod

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

            self.engine = engine
            self.base.metadata.create_all(engine)
        except:
            print('Unable to connect to database! check env variables / sql server is up')
            print(
                f"Tried to connect to: mysql://{username}:<PASSWORD>@{hostname}/{dbname}")
            return

    def insert_or_update_students(self, students) -> bool:
        try:
            students = [
                {'name': 'Tomer', 'attendance_duration': 22.3, 'attendance_percentage': 33.3}]
            local_session = self.session(bind=self.engine)
            students_to_insert = []
            for student in students:
                if self._student_in_table(student):
                    self._update_student_durations(student)
                else:
                    print(student['name'], student['attendance_duration'],
                          student['attendance_percentage'])
                    students_to_insert.append(self.model_student(
                        name=student['name'], attendance_duration=student['attendance_duration'], attendance_percentage=student['attendance_percentage']))
            local_session.add_all(students_to_insert)
            local_session.commit()
            return True
        except Exception as ex:
            print('Unable to insert into students table!')
            return False

    def _student_in_table(self, student) -> bool:
        local_session = self.session(bind=self.engine)
        student_entry = local_session.query(self.model_student).filter(
            self.model_student.name == student['name']).first()
        if student_entry:
            return True
        return False

    def _update_student_durations(self, student):
        local_session = self.session(bind=self.engine)
        student_entry = local_session.query(self.model_student).filter(
            self.model_student.name == student['name']).first()
        student_entry.attendance_duration += student['attendance_duration']
        student_entry.attendance_percentage = student['attendance_percentage']

    def insert_or_update_attendance(self, meeting_minutes) -> bool:
        try:
            local_session = self.session(bind=self.engine)
            attendance = local_session.query(self.model_attendance).first()
            if attendance:
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


thedb = AttendanceDB()
thedb.connect()
thedb.insert_or_update_students([])
