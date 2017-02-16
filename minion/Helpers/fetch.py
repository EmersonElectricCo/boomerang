"""
Created on May 19, 2016
@author: Timothy Lemm 
@author: Grant Steiner
@Company: Emerson
"""

from ghost import Ghost
from urlparse import urlparse
import requests
import ghost
from logging import log_debug


def fetch_basic(url, user_agent, results_location, job_id=None):
    """function to use for basic fetch

    :param url: url to fetch information from
    :param user_agent: user agent string that is used by the minion in making the fetch
    :param results_location: the location to where the results are stored
    :param job_id: id of the job that is used to differentiate if from any other jobs that may be run
    :return: results_data - a dictionary of metadata on the fetch

    Before anything else, the url that is specified is cleaned so as to not throw any errors. After that, a Requests
    session is started. It is from this session that we will be making the HTTP request to the minion that makes the
    fetch. We perform a GET on the url. If there is no connection error, we raise the http status code from the get. If
    it is 200, we write the page data to a file. After that, we write some metadata about the fetch to the results_data
    dictionary, such as cookies and any info about redirects. Then, we return the results_data dictionary.
    """
    log_debug("fetch_basic", "Entering fetch_basic")
    headers = {'user-agent': user_agent}

	# Clean up an loose hanging non-printable characters. 
	# In the future consider moving this out to it's own method
	# with additional checks. 
    url_clean = url.lstrip()

    results_data = {'requested_url': url,
                    'actual_url': url_clean,
                    'remote_job_id': str(job_id)}

    log_debug("fetch_basic", "Starting Fetch of: " + url_clean)

    session = requests.Session()

    try:
		# Do the actual fetch. We are ok with non-valid SSL Certs
        fetch_result = session.get(url_clean, headers=headers, verify=False)

    except requests.ConnectionError:
        results_data['connection_success'] = False
        log_debug("fetch_basic", "Connection Failed for Fetch: " + url_clean)
        return results_data

    except Exception as e:
        log_debug("fetch_basic", "Unexpected Exception while fetching site. " + str(type(e)) + " : " + str(e)
        return results_data

    try:
        fetch_result.raise_for_status()

        results_data['fetch_success'] = True

        log_debug("fetch_basic", "Succesfully Fetched: " + url_clean)

        try:
            log_debug("fetch_basic", "Opening: " + str(results_location) + " for: " + url_clean)

            fetch_file = open(results_location, 'wb')

            for chunk in fetch_result.iter_content(100000):
                fetch_file.write(chunk)

                log_debug("fetch_basic",
                          "Writing " + str(len(chunk)) + " bytes to: " + str(results_location) + " for: " + str(
                              url_clean))

            fetch_file.close()

            log_debug("fetch_basic", "Closing: " + str(results_location) + " for: " + str(url_clean))

            results_data['fetch_object_success'] = True
            log_debug("fetch_basic", "got here")
        except:
            results_data['fetch_object_success'] = False

    except Exception as e:
        log_debug("fetch_basic", "Unexpected Exception while handlin fetch data. " + str(type(e)) + " : " + str(e)
        results_data['fetch_success'] = False

    finally:
        results_data['connection_success'] = True
        results_data['server_info'] = dict(fetch_result.headers)
        results_data['response_code'] = fetch_result.status_code

        if len(fetch_result.cookies) > 0:
            results_data['cookies'] = fetch_result.cookies.get_dict()

        if len(fetch_result.history) > 0:
            # There was some sort of redirect... Might as well capture everything
            results_data['redirects'] = []
            for item in fetch_result.history:
                history_item = {'headers': dict(item.headers),
                                'response_code': item.status_code}
                results_data['redirects'].append(history_item)

        return results_data


def fetch_website(url, user_agent, results_location_dir):
    """function to use for website fetch

    :param url: url to fetch information from
    :param user_agent: user agent string that is used by the minion in making the fetch
    :param results_location_dir: the location to where the results are stored
    :return: results_data - a dictionary of metadata on the fetch

    This method uses a different library than the basic fetch method, Ghost.py (documentation at
    http://ghost-py.readthedocs.io/en/latest/#). After cleaning the url, a session is opened with the user agent string
    passed in. Then the specific web page is opened and all the resources of the web page are collected. After that, a
    screen-shot of the web page is collected. Then, the page data is written to a file that is named from
    the session id. Then each resource gathered during the fetch is written to a file, and these are placed in the same
    directory as the page data. Beyond that, miscellaneous metadata is written to the results_data dictionary.
    """
    log_debug("fetch_website", "Entering fetch_website")

    # clean the url
    url_clean = url.lstrip()

    log_debug("fetch_website", "Starting Fetch of: " + url_clean)

    # start a Ghost.py session
    session = Ghost().start(user_agent=user_agent)

    results_data = {'requested_url': url,
                    'actual_url': url_clean,
                    'remote_job_id': str(session.id)}
    try:
        # open the web page and gather all the page's resources
        page, resources = session.open(address=url_clean, user_agent=user_agent)

    # catch a TimeoutError
    except (ghost.TimeoutError, ghost.Error):
        results_data['connection_success'] = False
        log_debug("fetch_website", "Connection Failed for Fetch: " + url_clean)
        return results_data

    except Exception as e:
        print type(e)
        print str(e)
        return results_data

    # if page is None and there are no resources, that means that a connection to the page failed
    if page is None and len(resources) == 0:
        log_debug("fetch_website", "")
        results_data['connection_success'] = False

    else:
        netloc = urlparse(url_clean).netloc
        log_debug("fetch_website", "Attempting to capture screenshot of {}".format(netloc))

        try:
            # capture a screen-shot of the web page
            session.capture_to("{}/{}.png".format(results_location_dir, netloc))

            log_debug("fetch_website", "Successful capture of screenshot of {}".format(netloc))

        except Exception as e:
            log_debug("fetch_website", "Failed to capture screenshot of {}".format(netloc))

            print type(e)
            print str(e)

        try:
            log_debug("fetch_website", "Opening: {}/{} for: {}".format(results_location_dir, session.id, url_clean))
            fetch_file = open("{}/{}".format(results_location_dir, session.id), 'w')

            log_debug("fetch_website", "writing page content to file")

            # write page content to file
            fetch_file.write(page.content)

            log_debug("fetch_website", "closing {}".format(session.id))
            fetch_file.close()

            # write the data of each resource to different files
            for resource in resources:
                log_debug("fetch_website", "opening {}/resource{} for: {}".format(results_location_dir,
                                                                                  resources.index(resource),
                                                                                  url_clean))
                data_file = open("{}/resource{}".format(results_location_dir, resources.index(resource)), "w")

                log_debug("fetch_website", "writing content to {}".format(resources.index(resource)))
                data_file.write(resource.content)

                log_debug("fetch_website", "closing {}".format(resources.index(resource)))
                data_file.close()

            results_data['fetch_object_success'] = True

        except:
            results_data['fetch_object_success'] = False

        finally:
            # collect more metadata
            results_data['connection_success'] = True
            results_data['server_info'] = dict(page.headers)
            results_data['response_code'] = page.http_status

            if page.http_status in [400, 404, 403, 401]:
                results_data["fetch_success"] = False

            if len(session.cookies) > 0:
                results_data['cookies'] = [x.value().data() for x in session.cookies]

            return results_data
