"""
Created on May 19, 2016
@author: Timothy Lemm
@Company: Emerson
"""
import os
import logging
from logging.handlers import RotatingFileHandler

# General Flask Imports
from flask import Flask, jsonify, send_file, request
from werkzeug.exceptions import HTTPException, BadRequest
from werkzeug.exceptions import default_exceptions

# API Helper Imports
from API.responses import prepare_200, prepare_404, prepare_500, prepare_400
from Helpers.jobs import run_job, get_job_results

__all__ = ['make_json_app']


def make_json_app(import_name, **kwargs):
    """
    Creates a JSON-oriented Flask app.
    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):
    { "message": "405: Method Not Allowed" }
    """

    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
        return response

    app = Flask(import_name, **kwargs)

    for code in default_exceptions.iterkeys():
        app.register_error_handler(code, make_json_error)

    return app


'''
Minion Config and Loading
'''
minion = make_json_app(__name__)

# Loading Config
minion.config.from_pyfile('config.py')
user = "None"

# Logging Setup
logging_handler = RotatingFileHandler(minion.config['LOGGING_FILE'])
logging_handler.setLevel(minion.config['LOGGING_LEVEL'])
logging_format = logging.Formatter("{\"time\":\"%(asctime)s\", \"user\":\"" + user +
                                   "\", \"level\":\"%(levelname)s\", \"msg\":%(message)s}\"")
logging_handler.setFormatter(logging_format)
minion.logger.addHandler(logging_handler)
minion.logger.info("\"Minion Starting Up\"")

# Ensure the the environment is setup
if not os.path.isdir(minion.config['BOOMERANG_FETCH_DIR']):
    minion.logger.info("\"Boomerang Directory Does not Exist... Creating...\"")
    os.makedirs(minion.config['BOOMERANG_FETCH_DIR'])


'''
Minion Routes
'''

@minion.route('/')
def index():
    """Establishes minion root "GET" Endpoint

    Serves no actual puprose for the operation of the minion
	useful for smoke testing the minion after installation.
    """
    data = {"hello": "This Is Dog"}
    return prepare_200("Hello This Is Dog", data)


@minion.route('/', methods=["POST"])
def api_request_basic():
    """Establishes the endpoint that is used for the basic fetch mode

	POST body should be json formated.
	Required field(s):
	  - url : actual url that is requested to be fetched by the minion

	Optional field(s):
	  - user-agent : user agent to be used during the request of the url
	                 if this argument is not provided, then the default
					 user agent in the config file will be used.

    """
    try:
        data = request.get_json()
        if data is None:
            raise BadRequest

        file_path = run_job(data, "basic")
        return send_file(file_path)

    except BadRequest as e:
        return prepare_400("api_request_basic", str(e))
    except ValueError as e:
        return prepare_400("api_request_basic", str(e))
    except Exception as e:
        print type(e)
        return prepare_500("api_request_basic", str(e))


@minion.route("/website", methods=["POST"])
def api_request_website():
    """Establishes the endpoint that is used for the website fetch mode

	POST body should be json formated.
	Required field(s):
	  - url : actual url that is requested to be fetched by the minion

	Optional field(s):
	  - user-agent : user agent to be used during the request of the url
	                 if this argument is not provided, then the default
					 user agent in the config file will be used.


    """
    try:
        data = request.get_json()
        if data is None:
            raise BadRequest

        file_path = run_job(data, "website")
        return send_file(file_path)

    except BadRequest as e:
        return prepare_400("api_request_website", str(e))
    except ValueError as e:
        return prepare_400("api_request_website", str(e))
    except Exception as e:
        print type(e)
        return prepare_500("api_request_website", str(e))


@minion.route('/<job_id>', methods=["GET"])
def api_basic_results(job_id):
    """Establishes endpoint for retrieval of historical boomerang results

    :param job_id: id of the specific job that you wish to look up

    """
    if minion.config['BOOMERANG_STORE_RESULTS']:
        try:
            file_path = get_job_results(job_id)
            return send_file(file_path)
        except BadRequest as e:
            return prepare_400("api_basic_results", str(e))
        except ValueError:
            return prepare_404('api_basic_results')
        except Exception as e:
            return prepare_500("api_basic_results", str(e))
    else:
        return prepare_400("api_basic_results", error="Config set to not store results")


if __name__ == "__main__":
	# Values not relevant when ran in gunicorn or similar system.
    minion.run(debug=True, host="0.0.0.0", port=5000)
