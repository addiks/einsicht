
import sys, os, logging
from os.path import dirname, abspath

from systemd.journal import JournalHandler

sys.path.append(dirname(dirname(abspath(__file__))))

from py.Application import Application
from py.Hub import Log

if __name__ == "__main__":
    
    logger = logging.getLogger('einsicht')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(JournalHandler(SYSLOG_IDENTIFIER='einsicht'))
    Log.registerLogger(logger)
        
    sys.exit(Application.main(sys.argv))
        
