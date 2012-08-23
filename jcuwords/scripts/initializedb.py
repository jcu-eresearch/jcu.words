import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    Base,
    Keyword
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
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        
        import ipdb; ipdb.set_trace()
        txt = open(os.path.join(os.getcwd(), 'jcu.words.txt'), 'rb')
        for line in txt:
            for term in line.split(' '):
                try:
                    term.decode('ascii')
                except:
                    continue
                model = Keyword(keyword=term, user_id='system')
                DBSession.add(model)
