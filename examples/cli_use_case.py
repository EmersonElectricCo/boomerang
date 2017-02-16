#!/usr/bin/python
# encoding: utf-8
"""
boomerang -- CLI tool for interfacing with the boomerang service to retrieve an off network resource while hiding the
             fact that you are coming from your machine.

@author:     Timothy Lemm
"""

import getpass
import json
import logging
import os
import random
import sys
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from logging.handlers import RotatingFileHandler

from pyminion.pyminion import PyMinion
from verbalexpressions import VerEx

__all__ = []
__version__ = 1.0
__date__ = '2016-06-16'
__updated__ = '2016-06-23'
program_name = os.path.basename(sys.argv[0])
program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
description = '''
emr-boomerang -- EMR CLI tool for interfacing with the boomerang service to retrieve an off network resource while
hiding the fact that you are coming from your machine.
'''

REMOTE_SERVER = "127.0.0.1"
REMOTE_PORT = 5000
REMOTE_METHOD = "http"
USER_AGENT_OPTIONS = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    # Win10 Chrome 50
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    # Win7 Chrome 50
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',  # Win 7 Firefox 46
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',  # Win 10 Firefox 46
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',  # Win 7 IE 11
    'Mozilla/5.0 (Windows NT 5.1; rv:46.0) Gecko/20100101 Firefox/46.0'  # WinXP Firefox 46
]
LOGGING_PATH = '/var/log/boomerang.log'
LOG_LEVEL = logging.INFO

if __name__ == "__main__":
    try:
        # Pull in arguments and set environment
        argv = sys.argv
        # Setup argument parser
        parser = ArgumentParser(description=description, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-p", "--path", dest="path", action="store", default=os.getcwd(),
                            help="path to where the resulting packaged should be stored [default: current working directory]")
        parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                            help="Tells emr-boomerang to output the json results to stdout in addition to storing them in the defined path")
        parser.add_argument("-u", "--useragent", dest="ua", action="store", default=random.choice(USER_AGENT_OPTIONS),
                            help="Set the User-Agent String to be used. [default: randomly selected from a pre-loaded list]")
        parser.add_argument("--mode", choices=['basic', 'website'], default='basic', help="Set the fetch mode to be used.")
        parser.add_argument(dest="uri", help="Target URI to be fetched")

        # Process arguments
        args = parser.parse_args()

        path = args.path
        if not os.path.isdir(path):
            raise Exception("Invalid Path: " + str(path))

        ua = str(args.ua)

        verbal_expression = VerEx()
        tester = (verbal_expression.
                  start_of_line().
                  find('http').
                  maybe('s').
                  find('://').
                  maybe('www.').
                  anything_but(' ').
                  end_of_line()
                  )

        uri = args.uri
        if not tester.match(uri):
            raise Exception("Invalid URI: " + str(uri) + " \n Hint - matching on: " + str(tester.source()))
        verbose = args.verbose

        user = getpass.getuser()

        # Logging
        logger = logging.getLogger('BoomLog')
        logger.setLevel(LOG_LEVEL)
        log_handler = RotatingFileHandler(LOGGING_PATH, maxBytes=100000)
        logging_format = logging.Formatter(
            "{\"time\":\"%(asctime)s\", \"user\":\"" + user + "\", \"uri\":\"" + str(
                uri) + "\", \"user-agent\":\"" + str(ua) + "\", \"result\":\"%(message)s\"}"
        )
        log_handler.setFormatter(logging_format)
        logger.addHandler(log_handler)

        # Make Request For File:
        try:
            pm = PyMinion(REMOTE_SERVER, REMOTE_PORT, REMOTE_METHOD, mode=args.mode)
            # result = pm.request_url(path, uri, ua)
            result = pm.request_url(return_path=path, url=uri, user_agent=ua)
            if result is not None:
                logger.info("Success")

                if verbose:
                    with open(os.path.join(result, "results.json")) as res_file:
                        parsed = json.load(res_file)
                        print json.dumps(parsed, indent=4, sort_keys=True)

            else:
                logger.error("Minion Error")
                print "Error with remote minion when attempting to complete job. Check Minion Health"
        except UserWarning as e:
            logger.info("User Already Fetched Resource")
            print str(e)
        except Exception as e:
            logger.error("Error Communicating with Minion: " + str(e))
            print "Error with remote minion when attempting to complete job. Check Minion Health"

    except Exception as e:
        print "Error Running EMR-Boomerang. please see --help for usage"
        print str(type(e))
        print str(e)
        print "-------------"
