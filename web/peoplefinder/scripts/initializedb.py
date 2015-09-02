import os
import sys
import time
import datetime
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from model.hlr import (
    HLRDBSession,
    Subscriber
    )

from model.models import (
    DBSession,
    Settings,
    Base,
    )

from com_interface.comms_interface_server import (
    pf_subscriber_imsi,
    pf_subscriber_extension,
    pf_subscriber_name
    )

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.pf.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    hlr_engine = engine_from_config(settings, 'sqlalchemy.hlr.')
    HLRDBSession.configure(bind=hlr_engine)

    # initial settings
    with transaction.manager:
        DBSession.add_all([
            Settings(name='imsiUpdate', value=3000),
            Settings(name='smsUpdate', value=3000),
            Settings(name='silentSms', value=3000),
            Settings(
                name='welcomeMessage',
                value='You are connected to a mobile search and rescue team. ' + \
                      'Please SMS to {ph_phone_number} to communicate. ' + \
                      'Your temporary phone number is {ms_phone_number}'
            ),
            Settings(
                name='replyMessage',
                value='Your SMSs are being sent to a mobile search and rescue team. ' + \
                      'Reply to this message to communicate.'
            ),
        ])

        HLRDBSession.add_all([
            Subscriber(
                created=datetime.datetime.fromtimestamp(time.time()),
                updated=datetime.datetime.fromtimestamp(time.time()),
                imsi=pf_subscriber_imsi,
                name=pf_subscriber_name,
                extension=pf_subscriber_extension,
                authorized=1,
                lac=0
            )
        ])
