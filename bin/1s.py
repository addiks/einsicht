
import sys, os
from os.path import dirname, abspath

sys.path.append(dirname(dirname(abspath(__file__))))

from py.Application import Application

if __name__ == "__main__":
    sys.exit(Application.main(sys.argv))