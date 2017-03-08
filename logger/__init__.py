# -*- coding: utf-8 -*-
"""
Created on 2016-12-29

@author: xb
"""
import logging
from fluent import handler


def kafka_logger(log_name):
    line_format = {
      'file_name': '%(module)s',
      'log_level': '%(levelname)s',
      'line': '%(lineno)d'
    }
    files_handle = handler.FluentHandler(log_name, host='10.19.47.136', port=54224)
    formatter = handler.FluentRecordFormatter(line_format)
    files_handle.setFormatter(formatter)
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(files_handle)
    return logger

logger = kafka_logger('kafka')