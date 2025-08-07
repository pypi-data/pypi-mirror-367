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


def _update():
    '''
        Try to update slurm_top_python at application start after asking the user
    '''
    try:
        if GENERAL_CONFIG:
            CURRENT_VERSION = str(__version__)
            os_name = "{0} {1}".format(platform.system(),
                                       platform.release()
                                       )
            resp = requests.get("https://slurm_top_python-telemetry.kinetekenergy.in",
                                params={'os_name': os_name, 'version': __version__}, timeout=1)

            NEW_VERSION = str(resp.text)
            if NEW_VERSION != CURRENT_VERSION and resp.status_code == 200:
                sys.stdout.write(
                    blue("A new version is available, would you like to update (Y/N)? ")) # type: ignore
                sys.stdout.flush()

                user_consent = input()

                if user_consent.lower() == 'y':
                    logger.info(
                        "main.py :: Updating slurm_top_python to version {0}".format(NEW_VERSION))

                    # run update instructions
                    update_success_status = 0
                    source_folder = ''.join(random.choice(
                        string.ascii_uppercase + string.digits) for _ in range(10))

                    sys.stdout.write(
                        green("\nCreating a temporary directory /tmp/{0} ...\n".format(source_folder))) # type: ignore
                    sys.stdout.flush()

                    update_success_status |= os.system(
                        'mkdir /tmp/{0}'.format(source_folder))
                    sys.stdout.flush()

                    update_success_status |= os.system(
                        'git clone https://github.com/kinetekenergy/slurm_top_python.git /tmp/{0}'.format(source_folder))

                    sys.stdout.write(green("\nInstalling slurm_top_python ...\n")) # type: ignore
                    sys.stdout.flush()

                    update_success_status |= os.system(
                        'cd /tmp/{0}/ && sudo python setup.py install'.format(source_folder))

                    # if we are not successful in updating status
                    if update_success_status != 0:
                        sys.stdout.write(
                            red("\nError occured while updating slurm_top_python.\n")) # type: ignore

                        sys.stdout.write(red(  # type: ignore
                            "Please report the issue at https://github.com/kinetekenergy/slurm_top_python/issues with the terminal output.\n"))

                        sys.stdout.flush()

                        sys.exit(1)
        else:
            blue("Checking for updates has been disabled - Skipping update check") # type: ignore
    except Exception as e:
        logger.info(
            "Exception :: main.py :: Exception occured while updating slurm_top_python "+str(e))

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

        # try to update slurm_top_python
        _update()

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

        # Add code for wait for all the threads before join

        # if GENERAL_CONFIG["logging"]["clear-log-on-exit"]:
        #     with open(_log_file, 'w'):
        #         pass

        # TODO :Wait for threads to exit before calling systemExist
        raise SystemExit

    except Exception as e:
        global_stop_event.set()

        logger.info("Exception :: main.py "+str(e))
        print(sys.exc_info())

        raise SystemExit


if __name__ == '__main__':
    main()
