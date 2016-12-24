
# Functions for interaction with godaddy api

import requests
import re
import configparser
import os

HERE = os.path.abspath(os.path.dirname(__file__))
config = configparser.ConfigParser()

config.read(os.path.join(HERE,"config/dynamic_ip.ini"))

KEY = config["godaddy"]["KEY"]
SECRET = config["godaddy"]["SECRET"]

IP_PATTERN = r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"

def update_ip(new_ip, domain, test = False):
    """
    updates the ip address for to new_ip for the given domain
    :param new_ip:
    :param domain:
    :return:
    """


    assert re.match(IP_PATTERN,new_ip)



    headers = {'Authorization': 'sso-key {key}:{secret}'.format(key = KEY, secret = SECRET)}
    data = [{"name":"@","data":new_ip,"ttl":5}]

    api_call = "https://api.godaddy.com/v1/domains/{domain}/records/A".format(domain = domain)

    if test == True:
        return {"headers":headers, "data": data, "api_call":api_call}

    return requests.put(api_call,json = data, headers = headers)

