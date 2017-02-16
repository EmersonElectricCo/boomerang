"""
Created on June 12, 2016
@author: Timothy Lemm
@Company: Emerson
"""
import os
import zipfile
import datetime
from urlparse import urlparse

import requests


class PyMinion:

    # base_url should be the url that routes to the minion
    base_url = ""

    def __init__(self, hostname, port=None, protocol="https", mode="basic"):
        """
        Establishes the PyMinion object.

        During setup init will check the connection to the provided server. If the connection is not successfully
        established, an Exception will be thrown.

        :param hostname: Mandatory field of the hostname for the minion
        :param port: Optional field, if no port is provided the default port for the defined method will be used
                     (i.e. 80 for http; 443 for https)
        :param protocol: Optional field to define the protocol to be used. Must be either 'http' or 'https'
        """

        if protocol != "https" and protocol != "http":
            raise ValueError("Connection method must be 'http' or 'https'")

        if port is None:
            self.base_url = protocol + "://" + str(hostname) + "/"
        else:
            self.base_url = protocol + "://" + str(hostname) + ":" + str(port) + "/"

        try:
            connection_test = requests.get(self.base_url)
            if connection_test.status_code != 200:
                raise Exception("Server does not appear to be responding properly. " + str(
                    connection_test.status_code) + " status code returned during connection testing")
        except Exception as e:
            raise Exception(str(e))

        # if website mode is specified, the base url is constructed to hit the appropriate endpoint on the minion
        if mode == "website":
            if port is None:
                self.base_url = protocol + "://" + str(hostname) + "/website"
            else:
                self.base_url = protocol + "://" + str(hostname) + ":" + str(port) + "/website"

    def request_url(self, return_path, url, user_agent=None):
        """Makes the URL request to the minion

        :param return_path: path to return the boomerang results to
        :param url: url of the website that will be fetched
        :param user_agent: user-agent string
        :return: if HTTP code is 200, the path to the boomerang results. otherwise, None

        The first thing that is done is the creation of the request payload dictionary, which will contain all necessary
        information for the HTTP request. This is sent to the minion. After that, the url is cleaned up and a unique
        location for the results to be stored in is created. Then the payload is POSTed to the minion, which does its
        magic and returns the data from the fetch. If the status code is 200, then the data is written to the location
        created for it and does some final cleanup and then returns the path to the results data.
        """

        request_payload = {'url': url}
        stamp = datetime.datetime.now()

        # parse the url and check to see if we can save results
        parsed_url = urlparse(url)

        # nabs the beginning 7 characters from the url path
        url_path = parsed_url.path[:8]

        # replaces any naughty characters
        for char in url_path:
            if char in ["<", ">", ":", "\"", "/", "\\", "|", "!", "?", "*", "%", "=", "&", ";", ",", "[", "]"]:
                url_path = url_path.replace(char, "")

        # formats file path
        results_path = os.path.join(return_path,
                                    "boomerang_results_{}_{}_{}_{}_{}_{}".format(stamp.year, stamp.month, stamp.day,
                                                                                 stamp.hour, stamp.minute,
                                                                                 stamp.second) + parsed_url.netloc + url_path)

        if os.path.exists(results_path):
            raise UserWarning("It appears you have already tried to grab this URL. "
                              "Are you sure you want to fetch it again?")

        os.mkdir(results_path)
        zip_path = os.path.join(results_path, "res.zip")

        if user_agent is not None:
            request_payload['user-agent'] = str(user_agent)

        try:
            req = requests.post(self.base_url, json=request_payload)

            if req.status_code == 200:
                with open(zip_path, 'wb') as res:
                    for chunk in req.iter_content(100000):
                        res.write(chunk)

                zip_file = zipfile.ZipFile(zip_path, 'r')
                zip_file.extractall(results_path)
                zip_file.close()

                try:
                    os.remove(zip_path)
                except:
                    pass

                return results_path

            else:
                return None

        except Exception as e:
            raise Exception(str(e))


if __name__ == "__main__":
    print "This module is meant to be run in support of another program and should not be ran directly."
