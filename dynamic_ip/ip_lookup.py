import subprocess
import re
import traceback
import sqlite3
import sys
import os
import configparser

import logging

import dynamic_ip.go_daddy_update as gd_update


HERE = os.path.abspath(os.path.dirname(__file__))
config = configparser.ConfigParser()

config.read(os.path.join(HERE,"config/dynamic_ip.ini"))

IP_DB = os.path.join(HERE,config["local values"]["IP_DB"])
IP_URL = config["local values"]["IP_URL"]
IP_LINE = config["local values"]["IP_LINE"]

IP_EMAIL_MESSAGE = config["email"]["IP_EMAIL_MESSAGE"]
IP_EMAIL = config["email"]["IP_EMAIL"]
IP_EMAIL_SUBJECT = config["email"]["IP_EMAIL_SUBJECT"]
EMAIL = config.getboolean("email","ENABLED",fallback=False)

IP_PATTERN = r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"
DOMAINS = config["godaddy"]["DOMAINS"].replace(" ","").split(",")

LOGFILE = os.path.join(HERE,config["local values"]["LOGFILE"])


def read_current_ip():
    """
    reads the current recorded ip address
    :return:
    """
    conn = sqlite3.connect(IP_DB)

    cur = conn.cursor()


    #query ip
    query  = "SELECT ip FROM ip_record WHERE service = 'current_ip'"
    cur.execute(query)
    ip = cur.fetchone()
    if ip:
        ip = ip[0]


    return ip


def check_ip(url):
    """
    checks public ip address using the service specified by url.
    Assumes a format like ipecho.net where the ip address is given
    by a line saying "Your IP is ..."
    :param url:
    :return:
    """
    try:
        p1 = subprocess.Popen(["wget",url,"-O","-"],stdout = subprocess.PIPE)
        p2 = subprocess.Popen(["grep", IP_LINE],stdin = p1.stdout,stdout = subprocess.PIPE,
                              universal_newlines=True)

        output = p2.communicate()

        ip = re.search(IP_PATTERN,output[0])

        if ip:
            ret = ip.group(0)
        else:
            logging.warning("ip failed to be looked up.  {reason}".format(reason=output[0][:1000]))



    except Exception as e:
        traceback.print_exc()
        logging.warning("ip failed to be looked up.  {reason}".format(reason = traceback.format_exc()))
        raise e
        return 1

    return ret

def update_ip( pub_ip,cur_ip, test = False):
    """
    checks ip address. if new, writes to table and sends email
    :modifies: writes to ip_record when ip address changes
    :return: if intervening processes do not execute successfully, return 1, else return 0
    """


    try:
        conn = sqlite3.connect(IP_DB)

        ret = []


        # Update only if the new ip address is valid and is not equal to the curren ip
        # on record
        if re.search(IP_PATTERN,str(pub_ip)) \
                and str(pub_ip).strip() != str(cur_ip).strip():




            if EMAIL == True:
                p1 = subprocess.Popen(["echo",IP_EMAIL_MESSAGE.format(ip = pub_ip)],stdout = subprocess.PIPE)
                p2 = subprocess.Popen(["mutt", "-s",IP_EMAIL_SUBJECT,"--",IP_EMAIL],stdin = p1.stdout)
                p2.communicate()

            # update godaddy ip
            for domain in DOMAINS:
                ret.append(gd_update.update_ip(pub_ip,domain, test))
                if ret[-1].status_code == 200:
                    logging.info("ip updated successfully")

                    # TODO add table structure so that each domain's ip address
                    # TODO is tracked and updated
                    cur = conn.cursor()
                    cur.execute("UPDATE ip_record SET ip = ?", [str(pub_ip).strip()])
                    conn.commit()
                    logging.info("updated ip to {pub_ip}".format(pub_ip))

                else:
                    logging.warning("ip failed.  response from godaddy: \n {text}".\
                                    format(text = ret[-1].text))

            conn.close()

            return ret


    except Exception:
        traceback.print_exc()
        return 1
    finally:
        conn.close()





def initialize_db():
    """
    creates db and populates row
    :return:
    """
    print("Executing from {file}".format(file=__file__))
    print("ip database is: {ip_db}".format(ip_db = IP_DB))
    conn = sqlite3.connect(IP_DB)
    cur = conn.cursor()

    # Create Table if one doesn't exist
    print("creating table")
    c_table = "CREATE TABLE IF NOT EXISTS ip_record (service text UNIQUE, ip text)"
    cur.execute(c_table)
    conn.commit()

    # check if table has row with service = 'current_ip'
    print('checking table')
    check = "SELECT ip FROM ip_record where service = 'current_ip'"
    cur.execute(check)
    ips = [item for item in cur]

    # if there are no rows with service = 'current_ip' populate row with current_ip
    if ips == []:
        try:
            print("ip table empty.  Populating")
            current_ip = check_ip(IP_URL)

            # if ip lookup fails, raise exception
            if current_ip == 1:
                raise Exception("ip lookup failed")

            insert_statement = "INSERT INTO ip_record (service, ip) VALUES ('current_ip',?)"
            cur.execute(insert_statement,[current_ip])
            conn.commit()


            print("ip writen.  Current value: {ip}".format(ip = current_ip))

        except Exception as e:
            # TODO: add log statement
            traceback.print_exc()
            conn.close()
            return 1
    else:
        print("ip already in table")


    conn.close()

    return 0



def main():
    if "-t" in sys.argv:
        test = True
    else:
        test = False

    logging.basicConfig(filename = LOGFILE, level = logging.INFO,
                        format = "%(levelname)s %(asctime)s: %(message)s")
    pub_ip = check_ip(IP_URL)
    cur_ip = read_current_ip()

    update_ip(pub_ip, cur_ip,test = test)


