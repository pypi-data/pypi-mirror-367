import sys
from time import sleep

from src.logcatter import Log

Log.init()
Log.set_level(Log.VERBOSE)
with Log.redirect(stderr=Log.ERROR):
    print("This is just print")
    print("Wait for 2 secs")
    sleep(2)
    sys.stderr.write("This is stderr with CR")
    sleep(2)
    sys.stderr.write("\r >> That is stderr with CR")
    sys.stderr.flush()
    sys.stderr.write("This is stderr message\n")
Log.dispose()
