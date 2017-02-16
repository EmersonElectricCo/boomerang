"""
Created on May 22, 2016
@author: Timothy Lemm
@author: Grant Steiner
@Company: Emerson
"""
import json
import os
import uuid
import pyminizip
from flask import current_app as app
from fetch import fetch_basic, fetch_website


def run_job(arguments, mode):
    """Organizes a fetch job

    :param arguments: dictionary of data that is needed to make fetch (url and user-agent)
    :param mode: string that specifies which fetch method to use (website or basic)
    :return: path to the zip file that holds the results

    This method is used to organize a single boomerang job. When the minion receives a http request to make a fetch job,
    this method is called (see minion.py, lines 100 and 123). A JSON string containing data necessary to run the fetch
    (the arguments variable) is passed in, and the url to fetch from and the user-agent string to use are obtained from
    this string. From there, the job is assigned an id, and a directory on the minion that will hold the results is
    created. After that, depending on the mode of the fetch that will be run (basic or website), the necessary method in
    fetch.py is called, which returns a dictionary of metadata of the fetch. This metadata is written into a file called
    results.json. From there, all of the other data gathered by the fetch is packaged up into the file.zip file, and
    then all of the data is packaged into the results.zip file and then returned via the minion as the http response.
    """
    if 'url' not in arguments:
        raise ValueError("Missing URL Argument")

    if 'user-agent' not in arguments:
        user_agent = app.config['BOOMERANG_DEFAULT_USER_AGENT']
    else:
        user_agent = arguments['user-agent']

    # assign id to job
    job_id = uuid.uuid4()

    # create directory to hold results on minion
    job_path = os.path.join(app.config['BOOMERANG_FETCH_DIR'], str(job_id))
    sample_path = os.path.join(job_path, str(job_id))
    os.mkdir(job_path)

    try:
        if mode == 'basic':
            response_info = fetch_basic(arguments['url'], user_agent, sample_path, job_id)
        elif mode == 'website':
            response_info = fetch_website(arguments['url'], user_agent, job_path)

    except ValueError as e:
        # remove created dir
        os.rmdir(job_path)
        raise e
    except Exception as e:
        os.rmdir(job_path)
        raise e

    # write metadata to json file
    json_path = os.path.join(job_path, "results.json")
    with open(json_path, "wb") as json_results_file:
        json.dump(response_info, json_results_file)

    # Package up the file for the basic fetch
    if mode == "basic":
        results_zip_path = os.path.join(job_path, "results.zip")
        file_zip_path = os.path.join(job_path, "file.zip")
        if os.path.exists(sample_path):
            pyminizip.compress(sample_path, file_zip_path, "infected", 1)
            pyminizip.compress_multiple([json_path, file_zip_path], results_zip_path, None, 9)
        else:
            pyminizip.compress_multiple([json_path], results_zip_path, None, 9)

        return results_zip_path

    # package up the files returned by the website fetch
    elif mode == "website":
        results_zip_path = os.path.join(job_path, "results.zip")
        file_zip_path = os.path.join(job_path, "file.zip")

        # gathers resources and the screen-shot into the compression list, then appends remaining files to that list
        compression_list = [os.path.join(job_path, x) for x in os.listdir(job_path) if "resource" in x or ".png" in x]
        compression_list.append(json_path)
        compression_list.append(file_zip_path)

        if os.path.exists(job_path):
            pyminizip.compress(os.path.join(job_path, response_info["remote_job_id"]), file_zip_path, "infected", 1)
            pyminizip.compress_multiple(compression_list, results_zip_path, None, 9)
        else:
            pyminizip.compress_multiple([json_path], results_zip_path, None, 9)
        return results_zip_path


def get_job_results(job_id):
    """Get data from previous jobs

    :param job_id: ID number to get results of job
    :return: results_path - path to the job data

    This checks to see if the job that you are looking for exists, and returns the path to that job's data
    """
    if not os.path.exists(os.path.join(app.config['BOOMERANG_FETCH_DIR'], str(job_id))):
        raise ValueError("Job Does not Exist")

    results_path = os.path.join(app.config['BOOMERANG_FETCH_DIR'], str(job_id), "results.zip")

    if not os.path.isfile(results_path):
        raise ValueError("Results not there...")

    return results_path
