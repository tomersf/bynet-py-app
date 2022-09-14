from decimal import Decimal
from sqlalchemy import create_engine, Column, String, Integer, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy_serializer import SerializerMixin
from abc import ABC, abstractmethod
from Logger import Logger
import os

from attendance import get_attendance_dict_result
from env import env_config


class DB(ABC):
    def __init__(self) -> None:
        self.base = declarative_base()
        self.session = None
        self.engine = None
        self.connected = False

    @abstractmethod
    def connect(self) -> None:
        pass

    def _init_sessionmaker(self) -> None:
        self.session = sessionmaker(self.engine)

    def _init_db_metadata(self) -> None:
        self.base.metadata.create_all(self.engine)

    @abstractmethod
    def _init_model_tables(self) -> None:
        pass


class AttendanceDB(DB):
    def __init__(self) -> None:
        super().__init__()
        self.attendees = None
        self.attendance = None
        self.model_attendee = None
        self.model_attendance = None
        self.connected = False
        self.attendees_changed = False
        self.attendance_changed = False
        self._init_model_tables()

    def _init_model_tables(self):
        class Attendee(self.base, SerializerMixin):
            __tablename__ = 'attendees'
            id = Column(Integer(), primary_key=True)
            name = Column(String(25), nullable=False)
            attendance_duration = Column(DECIMAL(7, 2), nullable=False)
            attendance_percentage = Column(DECIMAL(5, 2), nullable=False)
        self.model_attendee = Attendee

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
                f"mysql://{username}:{password}@{hostname}:3306/{dbname}", echo=True)
            if not database_exists(engine.url):
                create_database(engine.url)
            self.engine = engine
            self._init_sessionmaker()
            self._init_db_metadata()
            self.connected = True
            return True
        except Exception as ex:
            Logger.ERROR(
                'ERROR! Unable to connect to database! check env variables / sql server is up')
            Logger.ERROR(
                f"Tried to connect to: mysql://{username}:<PASSWORD>@{hostname}/{dbname}")
            print(ex)
            return False

    def insert_or_update_attendees(self, attendees: dict) -> bool:
        self._open_session(self._insert_or_update_attendees, attendees)

    def _insert_or_update_attendees(self, local_session, attendees):
        attendees_to_insert = []
        for attendee in attendees.keys():
            if self._attendee_in_table(attendee):
                self._update_attendee_duration(
                    attendees[attendee], attendee)
            else:
                attendees_to_insert.append(self.model_attendee(
                    name=attendee, attendance_duration=Decimal(attendees[attendee]['attendance_duration']), attendance_percentage=Decimal(attendees[attendee]['attendance_percentage'])))
        local_session.add_all(attendees_to_insert)
        local_session.commit()
        return True

    def close_unexpected_db_session(local_session):
        Logger.ERROR('EXECUTING ROLLBACK & CLOSING SESSION DUE TO EXCEPTION')
        local_session.rollback()
        local_session.close_all()

    def _attendee_in_table(self, attendee_name) -> bool:
        self._open_session(self.__attendee_in_table, attendee_name)

    def __attendee_in_table(self, local_session, attendee_name):
        attendee_entry = local_session.query(self.model_attendee).filter(
            self.model_attendee.name == attendee_name).first()
        if attendee_entry:
            return True
        return False

    def _update_attendee_duration(self, attendee_dict, attendee_name):
        self._open_session(self.__update_attendee_duration,
                           attendee_dict, attendee_name)

    def __update_attendee_duration(self, local_session, attendee_dict, attendee_name):
        attendee_entry = local_session.query(self.model_attendee).filter(
            self.model_attendee.name == attendee_name).first()
        if attendee_entry:
            attendee_entry.attendance_duration += Decimal(
                attendee_dict['attendance_duration'])
            attendee_entry.attendance_percentage = Decimal(
                attendee_dict['attendance_percentage'])

    def insert_or_update_attendance(self, meeting_minutes, loading_from_file_flag) -> bool:
        result = self._open_session(
            self._insert_or_update_attendance, meeting_minutes, loading_from_file_flag)
        if not result:
            Logger.ERROR('Unable to insert into attendance table!')
            return False
        return True

    def _insert_or_update_attendance(self, local_session, meeting_minutes, loading_from_file_flag) -> bool:
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

    def get_total_meetings_duration(self) -> Decimal:
        self._open_session(self._get_total_meetings_duration)

    def _get_total_meetings_duration(self, local_session):
        attendance = local_session.query(self.model_attendance).first()
        return attendance['total_duration']

    def load_db_from_participants_file(self) -> bool:
        self.attendees_changed = True
        self.attendance_changed = True
        attendance_dict = get_attendance_dict_result(os.getcwd())
        total_minutes = attendance_dict['total_meetings_duration']
        attendance_dict.pop('total_meetings_duration')
        if not attendance_dict:
            return False
        else:
            self.insert_or_update_attendees(attendance_dict)
            self.insert_or_update_attendance(Decimal(total_minutes), True)
            return True

    def get_all_attendees(self) -> list[dict]:
        if not self.connected:
            return []
        if not self.attendees_changed:
            return self.attendees
        return self._open_session(self._set_and_get_attendees)

    def _set_and_get_attendees(self, local_session):
        attendees = local_session.query(self.model_attendee).all()
        result = []
        for attendee in attendees:
            result.append(attendee.to_dict())
        self.attendees_changed = False
        self.attendees = result
        return result

    def get_attendance(self) -> dict:
        if not self.connected:
            return self._empty_attendance_result()
        if not self.attendance_changed:
            return self.attendance
        return self._open_session(self._set_and_get_attendance)

    def _set_and_get_attendance(self, local_session):
        attendance = local_session.query(self.model_attendance).all()
        if attendance:
            self.attendance_changed = False
            self.attendance = attendance[0].to_dict()
            return attendance[0].to_dict()
        return self._empty_attendance_result()

    def _empty_attendance_result(self):
        return {
            'total_duration': 0
        }

    def _open_session(self, callbackFn, *args):
        try:
            with self.session() as local_session:
                return callbackFn(local_session, *args)
        except:
            self.close_unexpected_db_session(local_session)
            return False
