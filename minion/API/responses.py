"""
Created on May 19, 2016

@author: Timothy Lemm
@company: Emerson
"""

import json
from flask import Response
from flask import current_app as app


def _finalize_response(data, code):
    """Final formatting for JSON HTTP responses

    :param data: body of the response
    :param code: status code
    :return: resp - Formatted HTTP response
    """
    resp = Response(response=data,
                    status=code,
                    mimetype="application/json")
    return resp


def prepare_200(function_name, data=None):
    """Prepare a 200 HTTP status code

    :param function_name: function that produces the response
    :param data: body of the response
    :return: Prepared 200 HTTP status code
    """
    resp_data = {'code': 200, 'code_name': "OK", 'function_name': function_name, 'data': data}

    app.logger.info(resp_data)

    return _finalize_response(json.dumps(resp_data), 200)


def prepare_201(function_name, resource):
    """Prepare a 201 HTTP status code

    :param function_name: function that produces the response
    :param resource: UID of the resource that was created
    :return: Prepared 201 HTTP status code
    """
    resp_data = {'code': 201, 'code_name': "Created", 'function_name': function_name, 'resource': resource}

    app.logger.info(resp_data)

    return _finalize_response(json.dumps(resp_data), 201)


def prepare_400(function_name, error=None):
    """Prepare a 400 HTTP status code

    :param function_name: function that produces the response
    :param error: specific error of the function that produces the 400 code
    :return: Prepared 400 HTTP status code
    """
    resp_data = {'code': 400, 'code_name': "Bad Request", 'function_name': function_name, 'hint': str(error)}

    app.logger.warning(resp_data)

    return _finalize_response(json.dumps(resp_data), 400)


def prepare_401():
    """Prepare a 401 HTTP status code

    :return: Prepared 401 HTTP status code
    """
    resp_data = {'code': 401, 'code_name': "Unauthorized"}

    app.logger.warning(resp_data)

    return _finalize_response(json.dumps(resp_data), 401)


def prepare_404(resource):
    """Prepare a 404 HTTP status code

    :param resource: resource that could not be found
    :return: Prepared 404 HTTP status code
    """
    resp_data = {'code': 404, 'code_name': "Not Found", 'resource': str(resource)}

    app.logger.warning(resp_data)

    return _finalize_response(json.dumps(resp_data), 404)


def prepare_500(function_name, error):
    """Prepare a 500 HTTP status code

    :param function_name: function that produces the response
    :param error: specific error of the function that produces the 500 code
    :return: Prepared 500 HTTP status code
    """
    resp_data = {'code': 500, 'code_name': "Internal Server Error", 'function_name': function_name,
                 'error_type': str(type(error)), 'error_msg': str(error)}

    app.logger.error(resp_data)

    return _finalize_response(json.dumps(resp_data), 500)


def prepare_501(function_name):
    """Prepare a 501 HTTP status code

    :param function_name: function that produces the response
    :return: Prepared 501 HTTP status code
    """
    resp_data = {'code': 501, 'code_name': "Not Implemented", 'function_name': function_name}

    app.logger.debug(resp_data)

    return _finalize_response(json.dumps(resp_data), 501)
