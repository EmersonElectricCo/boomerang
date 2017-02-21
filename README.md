# Boomerang
A tool designed for consistent and safe capture of off network web resources. 


## Introduction
As a network defender doing full life-cycle analysis of an attack, it is often useful to capture an off network web resource to help complete the picture and learn more about the advasary.  However, doing so has inherit risks especially in the coure of an investigation where it is easy for an analyst, no matter the skill level, to make a mistake or forget to capture data.

Boomerang looks to fill this gap by providing a consistent and safe method for analysts of all skill levels to retreieve desired resources in addition to providing metadata about the server providing the files. 

__What are some use cases for boomerang?__

* Pulling the payload at the other side of a phishing link
* Retrieve the next stage of a piece of malware 
* Grab the payload of a strategic web compromise 
* Checkout that suspicious website
 
__How does it work?__

Boomerang operates in a client-minion model like the one shown below. 

![alt text](https://github.com/EmersonElectricCo/boomerang/raw/master/flow.png "Boomerang Flow")



__Client__

The client can be anything that has been configured to talk to the minion's API. In the most simple form this is a CLI script like the [example one provided](https://github.com/compsecmonkey/boomerang/blob/master/examples/cli_use_case.py). However, useage of boomerang can easily be integrated into other tools or automated workflows using the PyMinion bindings provided in this repo.


__Minion__

The minion is where the work of retreiving the resources is done. All data regarding the request is then packaged up and sent back to the client for analysis. Depending on the resources the minion is beeing used to retrieve, it is advisable to deploy minions in an isolated enviornment such as VPS service or an isolated network segment. 


__Anything I should know about using this tool?__

OPSEC (Operational Security) should be the first thing on your mind when using boomerang. While Boomerang was designed with safety in mind, it is important to remember that when using the tool you are potentially reaching out and touching advesary controlled infrastructure. As such each request to a resource leaves a "fingerprint" that could potentially be used to the advasaries advantage. Weigh the risks and benefits before using boomerang to retrieve a resource. 
 
## Installation

### Client
Since interaction with boomerang's minions is done through RESTful API calls, any number of tools or languages can be used. 

Boomerang comes with a [basic CLI client](https://github.com/compsecmonkey/boomerang/blob/master/examples/cli_use_case.py) that can be used to to interact with your minions. To make use of this client you will need to install PyMinion (bindings for the minion API). 

From the repo directory:

```bash
cd pyminion
python setup.py install
```



### Minion
The minion has been successfully installed and tested on Ubuntu Server 14.04 and 16.04, both running Python 2.7.x. It has also been succesfully installed on Centos7. However, minor issues arrose with website mode and Xvfb on a headless Centos Box. The following instructions are for a Ubuntu install but similar steps can be followed for your flavor of choice.

```bash
cd minion
sudo apt-get install -y libz-dev
sudo pip install -r requirements.txt
sudo apt-get install -y python-pyside xvfb
```

All dependencies for the minion should now be install. To test the minion's functionality, run the minion by:

```bash 
python minion.py
```

__Production Install__

For a production enviornment, it is highly recommended that you run the minion inside a WSGI compatiable appliaction web server like [gunicorn](http://gunicorn.org).

## Useage

Boomerang has two basic modes of operation: __basic__ and __website__. 

### Basic Mode

In basic mode, the minion is used to fetch a single discrete resource (ie. a binary, an image, a webpage without it's dependencies).

When executed, a basic fetch will attempt to retrieve the requested resource. Upon a succesful fetch, a zip file is returned to the analyst which contains the following:

* A JSON formated file containing information about the fetch transaction as well as any gathered information about the server. 
* A zip file password protected with the password ```infected``` containing the requested resource

Basic mode can be executed with a __POST__ request to a minion at the root URL. The __POST__ must be JSON formated with the following fields:


| Field | Required | Notes | 
| ----- | -------- | ----- |
| url | yes | must be fully qualified with either http:// or https:// explicitly part of the URL |
| user-agent | no | if none is provided, the default configured in the minion's config file will be used |

__Example__

```bash
curl -H "Content-Type: application/json" -X POST -d '{"url":"http://google.com","user-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"}' http://<minion domain or ip>:<port>/
```

###Website Mode

In website mode, the minion is used to fetch the full contents of a single webpage including it's images, scripts, etc. In addition the minion will use the data collected to render a screenshot of what the page looks like. Upon a succesful fetch, a zip file is returned to the analyst which contains the following:

* A JSON formated file containing information about the fetch transaction as well as any gathered information about the server. 
* A zip file password protected with the password ```infected``` containing: 
 * All gathered resources with naming convention resource<0-n>
 * screenshot.png

Website mode can be executed with a __POST__ request to a minion at the ```/website``` endpoint. The __POST__ must be JSON formated with the following fields:

| Field | Required | Notes | 
| ----- | -------- | ----- |
| url | yes | must be fully qualified with either http:// or https:// explicitly part of the URL |
| user-agent | no | if none is provided, the default configured in the minion's config file will be used |

__Example__

```bash
curl -H "Content-Type: application/json" -X POST -d '{"url":"http://google.com","user-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"}' http://<minion domain or ip>:<port>/website
```


### bommerang_cli.py

The following is the usage for boomerang using the bommerang_cli.py example

```bash
positional arguments:
 uri                   Target URI to be fetched
optional arguments:
 -h, --help            show this help message and exit
 -p PATH, --path PATH  path to where the resulting packaged should be stored
                       [default: current working directory]
 -v, --verbose         Tells emr-boomerang to output the json results to
                       stdout in addition to storing them in the defined path
 -u UA, --useragent UA
                       Set the User-Agent String to be used. [default:
                       randomly selected from a pre-loaded list]
--mode {basic,website}
                       Set the fetch mode to be used. [default: basic]
```

__examples__

Basic fetch:

```
python bommerang_cli.py http://google.com
```

Example with website mode and printing the transaction and server JSON data to the commandline:

```
python bommerang_cli.py -v -mode website http://google.com
```




