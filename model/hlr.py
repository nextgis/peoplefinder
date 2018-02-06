import time
import struct
import datetime
import binascii

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
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

HLRDBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


def bind_session(connection_string, echo=False):
    engine = create_engine(connection_string, echo=echo)
    HLRDBSession.configure(bind=engine)


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
    header = Column(LargeBinary)
    text = Column(Text)


def user_data_decode(user_data, data_coding_scheme, ud_hdr_ind):
    msg_hex = binascii.unhexlify(user_data)
    msg_bytes = struct.unpack('%sB' % len(msg_hex), msg_hex)

    offset = msg_bytes[0]

    msg_bytes = [ b + offset if b + offset <= 255 else b + offset - 256  for b in msg_bytes[1:]]

    if ud_hdr_ind is False:
        msg_id = -1
        msg_part_num = 1
        msg_parts_count = 1
        msg_hex = struct.pack('%sB'%len(msg_bytes), *msg_bytes)
    else:
        udhl =  msg_bytes[0]

        msg_id = msg_bytes[3]
        msg_parts_count = msg_bytes[4]
        msg_part_num = msg_bytes[5]

        msg_offset = udhl + 1
        msg_hex = struct.pack('%sB'%( len(msg_bytes) - msg_offset ), *msg_bytes[msg_offset:])

    try:
        if data_coding_scheme == 8:
            msg = msg_hex.decode('utf-16be')
        elif data_coding_scheme == 4:
            msg = msg_hex.decode('utf-8')
        elif data_coding_scheme == 0:
            msg = msg_hex.decode('windows-1252')
        else:
            msg = msg_hex

        return msg_id, msg_part_num, msg_parts_count, msg

    except Exception as e:
        raise("The message could not be decoded. Error: %s" % e)


def create_sms(src_addr, dest_addr, text, charset=None):
    if charset:
        text_unicode = text.decode(charset)
    else:
        text_unicode = text

    text_utf16 = text_unicode.encode('utf-16be')

    msg_bytes = struct.unpack('%sB' % len(text_utf16), text_utf16)
    msg_bytes = [(255, b-1)[b>0] for b in msg_bytes]
    msg_hex = struct.pack('B%sB'%len(msg_bytes), 1, *msg_bytes)

    return Sms(
        created=datetime.datetime.fromtimestamp(long(time.time())),
        sent=None,
        deliver_attempts=1,
        reply_path_req=0,
        status_rep_req=0,
        protocol_id=0,
        data_coding_scheme=8,
        ud_hdr_ind=0,
        src_addr=src_addr,
        src_ton=0,
        src_npi=0,
        dest_addr=dest_addr,
        dest_ton=0,
        dest_npi=0,
        user_data=msg_hex,
    )
