from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    Float,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


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
