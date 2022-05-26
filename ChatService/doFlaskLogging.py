# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 20:54:35 2021

@author: home
"""

import sys
import logging

def set_up_logger(dest='stdout') -> None:
    _logger = logging.getLogger()
    _logger.setLevel(logging.INFO)
    #_logger.setLevel(logging.DEBUG)
    if dest == 'stdout':
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.FileHandler('logfile.txt','w')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    
    return

def clean_up_logger() -> None:
    _logger = logging.getLogger()
    for h in _logger.handlers:
        print ('removing handler %s'%str(h))
        _logger.removeHandler(h)
       
    return
