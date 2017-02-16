"""
Created on May 19, 2016
@author: Timothy Lemm
@Company: Emerson
"""

from flask import current_app as app


def log_debug(location, msg):
    """Creates a DEBUG entry in the boomerang logs

    :param location: module where the DEBUG message is created
    :param msg: DEBUG message
    """
    log_msg = {"location": location,
               "message": str(msg)}
    app.logger.debug(log_msg)
