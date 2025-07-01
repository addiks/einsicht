
import sys, os, logging, traceback
from os.path import dirname, abspath

from systemd.journal import JournalHandler

sys.path.append(dirname(dirname(dirname(dirname(abspath(__file__))))))
sys.path.append(dirname(dirname(abspath(__file__))))

from py.Application import Application
from py.Hub import Log
from py.MessageBroker import FileAlreadyOpenOnOtherProcessException

from lib.BackDoor import BackDoor

if __name__ == "__main__":
    logger = logging.getLogger('einsicht')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(JournalHandler(SYSLOG_IDENTIFIER='einsicht'))
    Log.registerLogger(logger)
    try:
        app = Application.instance()
        BackDoor(app, app.hub)
        app.run(sys.argv)
        sys.exit(app.execQt())
        
    except SystemExit:
        sys.exit(0)
        
    except FileAlreadyOpenOnOtherProcessException:
        sys.exit(0)

    except:
        exception = sys.exc_info()[0]
        Log.error(exception)
        Log.error(traceback.format_exc())
        
    sys.exit(-2)
        
