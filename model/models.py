from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    Float,
    create_engine,
    Numeric,
    LargeBinary,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


def get_session(connection_string, echo=False):
    engine = create_engine(connection_string, echo=echo)
    return scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind=engine))


class Measure(Base):
    __tablename__ = 'measure'

    id = Column(Integer, primary_key=True)
    imsi = Column(Text)
    timestamp = Column(DateTime)
    timing_advance = Column(Integer)
    distance = Column(Float)
    phone_number = Column(Text)
    gps_lat = Column(Float)
    gps_lon = Column(Float)


class Subscriber(Base):
    __tablename__ = 'Subscriber'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    updated = Column(DateTime)
    imsi = Column(Numeric)
    name = Column(Text)
    extension = Column(Text)
    authorized = Column(Integer)
    tmsi = Column(Text)
    lac = Column(Integer)
    expire_lu = Column(DateTime)


class Sms(Base):
    __tablename__ = 'Sms'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    sent = Column(DateTime)
    deliver_attempts = Column(Integer)
    valid_until = Column(DateTime)
    reply_path_req = Column(Integer)
    status_rep_req = Column(Integer)
    protocol_id = Column(Integer)
    data_coding_scheme = Column(Integer)
    ud_hdr_ind = Column(Integer)
    src_addr = Column(Text)
    src_ton = Column(Integer)
    src_npi = Column(Integer)
    dest_addr = Column(Text)
    dest_ton = Column(Integer)
    dest_npi = Column(Integer)
    user_data = Column(LargeBinary)
    user_data = Column(LargeBinary)
    text = Column(Text)
