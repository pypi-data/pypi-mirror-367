# -*- coding: utf-8 -*-
'''
    slurm_top_python(http://github.com/kinetekenergy)

    Author : Aashray Reddy
    Licence : MIT © 2025
'''
import sys,os
import logging

__dir__ = os.path.dirname(os.path.abspath(__file__))
__version__ = "1.0.0a12"

# setting the config
_log_file = os.path.join(os.path.expanduser('~'),'.slurm_top_python.log')
 # create file if not exists
if not os.path.exists(_log_file):
    open(_log_file,'w').close()

logging.basicConfig(filename=_log_file,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger('slurm_top_python_logger')

sys.path.append( os.path.join(
    (os.path.dirname(__file__)),
    'slurm_top_python'
))