from app import log, db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint
import inspect, datetime, babel
from flask import url_for
from sqlalchemy.sql import func
from sqlalchemy.orm import column_property
from babel.dates import get_day_names, get_month_names


def datetime_to_dutch_date_string(date):
    return babel.dates.format_date(date, locale='nl')


# woensdag 24 februari om 14 uur
def datetime_to_dutch_datetime_string(date):
    date_string = f'{get_day_names(locale="nl")[date.weekday()]} {date.day} {get_month_names(locale="nl")[date.month]} om {date.strftime("%H.%M")}'
    return date_string


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    class USER_TYPE:
        LOCAL = 'local'
        OAUTH = 'oauth'

    @staticmethod
    def get_zipped_types():
        return list(zip(['local', 'oauth'], ['LOCAL', 'OAUTH']))

    class LEVEL:
        USER = 1
        SUPERVISOR = 3
        ADMIN = 5

        ls = ["GEBRUIKER", "SECRETARIAAT", "ADMINISTRATOR"]

        @staticmethod
        def i2s(i):
            if i == 1:
                return User.LEVEL.ls[0]
            elif i == 3:
                return User.LEVEL.ls[1]
            if i == 5:
                return User.LEVEL.ls[2]

    @staticmethod
    def get_zipped_levels():
        return list(zip(["1", "3", "5"], User.LEVEL.ls))

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    username = db.Column(db.String(256))
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    password_hash = db.Column(db.String(256))
    level = db.Column(db.Integer)
    user_type = db.Column(db.String(256))
    last_login = db.Column(db.DateTime())
    settings = db.relationship('Settings', cascade='all, delete', backref='user', lazy='dynamic')

    @property
    def is_local(self):
        return self.user_type == User.USER_TYPE.LOCAL

    @property
    def is_oauth(self):
        return self.user_type == User.USER_TYPE.OAUTH

    @property
    def is_at_least_user(self):
        return self.level >= User.LEVEL.USER

    @property
    def is_strict_user(self):
        return self.level == User.LEVEL.USER

    @property
    def is_at_least_supervisor(self):
        return self.level >= User.LEVEL.SUPERVISOR

    @property
    def is_at_least_admin(self):
        return self.level >= User.LEVEL.ADMIN

    @property
    def password(self):
        raise AttributeError('Paswoord kan je niet lezen.')

    @password.setter
    def password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        else:
            return True

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def log(self):
        return '<User: {}/{}>'.format(self.id, self.username)

    def ret_dict(self):
        return {'id': self.id, 'DT_RowId': self.id, 'email': self.email, 'username': self.username,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'level': User.LEVEL.i2s(self.level), 'user_type': self.user_type, 'last_login': self.last_login,
                'chbx': ''}


class Settings(db.Model):
    __tablename__ = 'settings'

    class SETTING_TYPE:
        E_INT = 'INT'
        E_STRING = 'STRING'
        E_FLOAT = 'FLOAT'
        E_BOOL = 'BOOL'
        E_DATETIME = 'DATETIME'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    value = db.Column(db.Text)
    type = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    UniqueConstraint('name', 'user_id')

    def log(self):
        return '<Setting: {}/{}/{}/{}>'.format(self.id, self.name, self.value, self.type)


guests = db.Table('guests',
                  db.Column('end_user_id', db.Integer, db.ForeignKey('end_users.id'), primary_key=True),
                  db.Column('room_id', db.Integer, db.ForeignKey('rooms.id'), primary_key=True),
                  )


class EndUser(db.Model):
    __tablename__ = 'end_users'

    class Profile:
        E_FLOOR_COWORKER = 'Scholengemeenschapmedewerker'  # CLB, Scholengemeenschap, Internaat
        E_FAIR_COWORKER = 'Schoolmedewerker'  # VTI, Sint Ursula, SAL, ...'School'
        E_GUEST = 'Bezoeker'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    last_login = db.Column(db.DateTime())
    profile = db.Column(db.String(256))
    sub_profile = db.Column(db.String(256))
    visits = db.relationship('Visit', cascade='all, delete', backref='end_user')

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def add_visit(self, visit):
        self.visits.append(visit)
        db.session.commit()


    def profile_to_dutch(self):
        if self.profile == EndUser.Profile.E_GUEST:
            return 'Bezoeker'
        elif self.profile == EndUser.Profile.E_FAIR_COWORKER:
            return 'Schoolmedewerker'
        elif self.profile == EndUser.Profile.E_FLOOR_COWORKER:
            return 'Scholengemeenschapmedewerker'

    def __repr__(self):
        return f'{self.email}/{self.full_name()}/{self.visits[0].code}/{self.profile}'

    def flat(self):
        return {
            'id': self.id,
            'end-user-email': self.email,
            'end-user-first-name': self.first_name,
            'end-user-last-name': self.last_name,
            'full_name': f'{self.first_name} {self.last_name}',
            'last_login': self.last_login,
            'end-user-profile': self.profile,
            'profile_text': self.profile_to_dutch(),
            'sub_profile': self.sub_profile,
            'initials': ''.join([n[0] for n in self.full_name().split(' ') if n != ''][:2]),
            'is_guest': self.profile == EndUser.Profile.E_GUEST,
            'is_floor_coworker': self.profile == EndUser.Profile.E_FLOOR_COWORKER,
            'is_fair_coworker': self.profile == EndUser.Profile.E_FAIR_COWORKER,
        }

    def ret_dict(self):
        flat = self.flat()
        flat.update({'id': self.id, 'DT_RowId': self.id})
        return flat


class Visit(db.Model):
    __tablename__ = 'visits'

    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    end_user_id = db.Column(db.Integer, db.ForeignKey('end_users.id'))
    timeslot = db.Column(db.DateTime())
    email_sent = db.Column(db.Boolean, default=False)
    email_send_retry = db.Column(db.Integer(), default=0)
    survey_email_sent = db.Column(db.Boolean, default=False)
    survey_email_send_retry = db.Column(db.Integer(), default=0)
    enabled = db.Column(db.Boolean, default=True)
    room_code = db.Column(db.String(256), default=None)
    code = db.Column(db.String(256))

    def timeslot_string(self, layout=None):
        if self.timeslot is None: return ''
        layout = '%Y-%m-%dT%H:%M' if layout == None else layout
        return datetime.datetime.strftime(self.timeslot, layout)

    def flat(self):
        visit = {
            'visit_id': self.id,
            'registration-code': self.code,
            'enabled': self.enabled,
            'email_sent': self.email_sent,
            'survey_email_sent': self.survey_email_sent,
            'timeslot': datetime_to_dutch_datetime_string(self.timeslot),
            'code': self.code,
            'room_code': self.room_code,
            'email-send-retry': self.email_send_retry
        }
        user = self.end_user.flat()
        visit.update(user)
        return visit

    def ret_dict(self):
        flat = self.flat()
        flat.update({'id': self.id, 'DT_RowId': self.id})
        return flat

    def set_timestamp(self):
        self.timestamp = datetime.datetime.now()
        db.session.commit()

    def set_timeslot(self, timeslot):
        self.timeslot = timeslot
        db.session.commit()

    ack_email_sent_cb = []

    def set_email_sent(self, value):
        self.email_sent = value
        db.session.commit()
        for cb in Visit.ack_email_sent_cb:
            cb[0](value, cb[1])
        return True

    survey_email_sent_cb = []

    def set_survey_email_sent(self, value):
        self.survey_email_sent = value
        db.session.commit()
        for cb in Visit.survey_email_sent_cb:
            cb[0](value, cb[1])
        return True

    email_send_retry_cb = []

    def set_email_send_retry(self, value):
        self.email_send_retry= value
        db.session.commit()
        for cb in Visit.email_send_retry_cb:
            cb[0](value, cb[1])
        return True

    enabled_cb = []

    def set_enabled(self, value):
        self.enabled = value
        db.session.commit()
        for cb in Visit.enabled_cb:
            cb[0](value, cb[1])
        return True

    @staticmethod
    def subscribe_ack_email_sent(cb, opaque):
        Visit.ack_email_sent_cb.append((cb, opaque))
        return True

    @staticmethod
    def subscribe_survey_email_sent(cb, opaque):
        Visit.survey_email_sent_cb.append((cb, opaque))
        return True

    @staticmethod
    def subscribe_email_send_retry(cb, opaque):
        Visit.email_send_retry_cb.append((cb, opaque))
        return True

    @staticmethod
    def subscribe_enabled(cb, opaque):
        Visit.enabled_cb.append((cb, opaque))
        return True


class EndUserSurvey(db.Model):
    __tablename__ = 'end_user_surveys'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(256))
    result = db.Column(db.Text)

    def ret_dict(self):
        return {
            'DT_RowId': self.id,
            'id': self.id,
            'code': self.code,
            'result': self.result,
        }


class Room(db.Model):
    __tablename__ = 'rooms'

    class State:
        E_NEW = 'nieuw'
        E_OPEN = 'open'
        E_CLOSING = 'afsluiten'
        E_CLOSED = 'gesloten'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), default='')
    info = db.Column(db.String(256), default='')
    state = db.Column(db.String(256), default=State.E_NEW)
    code = db.Column(db.String(256))
    floor = db.Column(db.String(256))
    nbr_guests = db.Column(db.Integer, default=0)
    history = db.relationship('ChatLine', cascade='all, delete', backref='room')

    def __repr__(self):
        return f'{self.code}/{self.name}'

    def flat(self):
        return {'id': self.id,
                'name': self.name,
                'info': self.info,
                'state': self.state,
                'code': self.code,
                'floor': self.floor.level,
                }


class Floor(db.Model):
    __tablename__ = 'floors'

    class Level:
        E_CLB = 'CLB'
        E_SCHOLENGEMEENSCHAP = 'Scholengemeenschap'
        E_INTERNAAT = 'Internaat'

        @staticmethod
        def get_enum_list():
            attributes = inspect.getmembers(Floor.Level, lambda a: not (inspect.isroutine(a)))
            enums = [a[1] for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]
            return enums

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), default='')
    info = db.Column(db.String(256), default='')
    level = db.Column(db.String(256))
    has_chat = db.Column(db.Boolean, default=False)
    items = db.relationship('InfoItem', cascade='all, delete', backref='floor')

    def __repr__(self):
        return f'{self.level}'

    def flat(self):
        return {
            'DT_RowId': self.id,
            'id': self.id,
            'name': self.name,
            'info': self.info,
            'level': self.level,
            'has_chat': self.has_chat,
        }


class Fair(db.Model):
    __tablename__ = 'fairs'

    class School:
        E_VTI = 'VTI'
        E_SINT_URSULA = 'Sint Ursula'
        E_SAL = 'SAL'

        @staticmethod
        def get_enum_list():
            attributes = inspect.getmembers(Fair.School, lambda a: not (inspect.isroutine(a)))
            enums = [a[1] for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]
            return enums

    id = db.Column(db.Integer, primary_key=True)
    school = db.Column(db.String(256), default='')
    timeslot = db.Column(db.DateTime())
    wonder_url = db.Column(db.String(256), default='')

    def __repr__(self):
        return f'{self.school} {self.timeslot}'

    def flat(self):
        return {
            'DT_RowId': self.id,
            'id': self.id,
            'school': self.school,
            'wonder_url': self.wonder_url,
        }

    def ret_dict(self):
        return self.flat()


class ChatLine(db.Model):
    __tablename__ = 'chat_lines'

    id = db.Column(db.Integer, primary_key=True)
    owner_code = db.Column(db.String(256))
    initials = db.Column(db.String(256))
    full_name = db.Column(db.String(256))
    text = db.Column(db.String(256), default='')
    timestamp = db.Column(db.DateTime())
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))

    def flat(self):
        return {
            'id': self.id,
            'owner_code': self.owner_code,
            'text': self.text,
            'timestamp': self.timestamp,
        }


class InfoItem(db.Model):
    __tablename__ = 'info_items'

    class Type:
        E_TEXT = 'text'
        E_PDF = 'pdf'
        E_MP4 = 'mp4'
        E_YOUTUBE = 'youtube'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(256), default=Type.E_TEXT)
    item = db.Column(db.String(256))
    thumbnail = db.Column(db.String(256))
    text = db.Column(db.String(256), default='')
    active = db.Column(db.Boolean, default=True)
    floor_id = db.Column(db.Integer, db.ForeignKey('floors.id'))

    def flat(self):
        return {
            'id': self.id,
            'text': self.text,
            'type': self.type,
            'item': self.item
        }


# SUM in a box
class AvailablePeriod(db.Model):
    __tablename__ = 'available_periods'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime())
    length = db.Column(db.Integer, default=5)  # length, in days, of a period
    max_nbr_boxes = db.Column(db.Integer, default=4)
    active = db.Column(db.Boolean, default=True)
    reservations = db.relationship('SchoolReservation', cascade='all, delete', backref='period')

    nbr_boxes_taken = column_property(func.nbr_boxes_taken(id))

    def period_string(self):
        start_date = self.date.strftime('%d/%m/%Y')
        end_date = (self.date + datetime.timedelta(days=self.length - 1)).strftime('%d/%m/%Y')
        return f'{start_date} tem {end_date}'


# SUM in a box
class SchoolReservation(db.Model):
    __tablename__ = 'school_reservations'

    id = db.Column(db.Integer, primary_key=True)

    name_school = db.Column(db.String(256), default='')
    name_teacher_1 = db.Column(db.String(256), default='')
    name_teacher_2 = db.Column(db.String(256), default='')
    name_teacher_3 = db.Column(db.String(256), default='')
    email = db.Column(db.String(256))
    phone = db.Column(db.String(256))
    address = db.Column(db.String(256))
    postal_code = db.Column(db.Integer)
    city = db.Column(db.String(256))
    nbr_students = db.Column(db.Integer)

    reservation_period_id = db.Column(db.Integer, db.ForeignKey('available_periods.id'))
    reservation_nbr_boxes = db.Column(db.Integer)
    reservation_code = db.Column(db.String(256))

    ack_email_sent = db.Column(db.Boolean, default=False)

    active = db.Column(db.Boolean, default=True)
    enabled = db.Column(db.Boolean, default=True)

    meetings = db.relationship('TeamsMeeting', cascade='all, delete', backref='reservation')

    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def ack_email_is_sent(self):
        self.ack_email_sent = True
        db.session.commit()

    def send_ack_email(self):
        self.ack_email_sent = False
        db.session.commit()

    def flat(self, date_format=None):
        period_id_key = f'select-boxes-{self.reservation_period_id}'
        return {
            'name-school': self.name_school,
            'name-teacher-1': self.name_teacher_1,
            'name-teacher-2': self.name_teacher_2,
            'name-teacher-3': self.name_teacher_3,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'postal-code': self.postal_code,
            'city': self.city,
            'number-students': self.nbr_students,
            period_id_key: self.reservation_nbr_boxes,
            'teams-meetings': [m.flat(date_format) for m in self.meetings],
            'reservation-code': self.reservation_code,
        }

    def ret_dict(self):
        flat = self.flat()
        flat.update({'id': self.id, 'DT_RowId': self.id, 'number-boxes': self.reservation_nbr_boxes,
                     'period': self.period.period_string()})
        return flat


# SUM in a box
class TeamsMeeting(db.Model):
    __tablename__ = 'teams_meetings'

    id = db.Column(db.Integer, primary_key=True)

    classgroup = db.Column(db.String(256), default='')
    email = db.Column(db.String(256))
    date = db.Column(db.DateTime())
    teams_meeting_code = db.Column(db.String(1024), default=None)

    reservation_id = db.Column(db.Integer, db.ForeignKey('school_reservations.id'))

    enabled = db.Column(db.Boolean, default=False)
    ack_email_sent = db.Column(db.Boolean, default=False)

    def set_ack_email_sent(self, value):
        self.ack_email_sent = value
        db.session.commit()
        for cb in TeamsMeeting.ack_email_sent_cb:
            cb[0](value, cb[1])
        return True

    def date_string(self, layout=None):
        if self.date is None: return ''
        layout = '%Y-%m-%dT%H:%M' if layout == None else layout
        return datetime.datetime.strftime(self.date, layout)

    def flat(self, date_format=None):
        return {
            'classgroup': self.classgroup,
            'meeting-email': self.email,
            'meeting-date': self.date_string(date_format),
        }

    def ret_dict(self):
        flat = self.flat('%d/%m/%Y %H:%M')
        flat.update({'id': self.id, 'DT_RowId': self.id, 'code': self.teams_meeting_code,
                     'reservation': self.reservation.ret_dict(), 'email_sent': self.ack_email_sent,
                     'enabled': self.enabled,
                     'html_url': f'<a href="{self.teams_meeting_code}" target="_blank" >Hier klikken voor Teams meeting</a>'
                     })
        return flat

    ack_email_sent_cb = []

    @staticmethod
    def subscribe_ack_email_sent(cb, opaque):
        TeamsMeeting.ack_email_sent_cb.append((cb, opaque))
        return True