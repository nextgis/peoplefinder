import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from model.models import (
    DBSession,
    Settings,
    Base,
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
