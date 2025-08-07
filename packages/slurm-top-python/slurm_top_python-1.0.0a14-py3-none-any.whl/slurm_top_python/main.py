import threading
import logging
import npyscreen
import requests
import argparse
import sys
import string
import random
import os
import platform

from slurm_top_python import __version__, _log_file
from slurm_top_python.statistics import Statistics
from slurm_top_python.interfaces import slurm_top_pythonGUI
from slurm_top_python.plugins import SENSORS_LIST
from huepy import *

GENERAL_CONFIG = False


# Backwards compatibility for string input operation
try:
    input = raw_input
except NameError:
    pass

logger = logging.getLogger('slurm_top_python.main')

def main():
    try:
        # app wide global stop flag
        global_stop_event = threading.Event()

        # command line argument parsing
        parser = argparse.ArgumentParser(description='slurm_top_python argument parser')

        # check version
        parser.add_argument('-v',
                            action='version',
                            version='slurm_top_python {}'.format(__version__))

        # config stored in yaml; make sure intervals are always under 1000
        csrt = 1000
        dsrt = 1000
        msrt = 1000
        psrt = 1000
        ssrt = 1000
        nsrt = 1000  # network sensor rate is always 1 second

        srts = [csrt, dsrt, msrt, nsrt, psrt, ssrt]
        sensor_refresh_rates = {SENSORS_LIST[i]: srts[i]
                                for i in range(len(SENSORS_LIST))}

        # TODO ::  Catch the exception of the child thread and kill the application gracefully
        # https://stackoverflow.com/questions/2829329/catch-a-threads-exception-in-the-caller-thread-in-python
        s = Statistics(SENSORS_LIST, global_stop_event, sensor_refresh_rates)
        # internally uses a thread Job
        s.generate()
        logger.info('Statistics generating started')

        app = slurm_top_pythonGUI(s.statistics, global_stop_event,
                       sensor_refresh_rates, "noTheme")
        logger.info('Starting the GUI application')
        app.run()

    # catch the kill signals here and perform the clean up
    except KeyboardInterrupt:
        global_stop_event.set()

        # TODO: Add code for wait for all the threads before join

        # TODO :Wait for threads to exit before calling systemExist
        raise SystemExit

    except Exception as e:
        global_stop_event.set()

        logger.info("Exception :: main.py "+str(e))
        print(sys.exc_info())

        raise SystemExit


if __name__ == '__main__':
    main()
