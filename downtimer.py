#!/usr/bin/env python3
#### Version History:
TITLE, VERSION="Downtimer", "1.5"
# 2020-08-22 - v1.5 - Wasting my time solving weird scenarios caused by testing, likely unrealistic
# 2020-08-06 - v1.4 - Fix the messed up times if you end before recovery
# 2020-08-04 - v1.3 - Better error handling
# 2020-08-03 - v1.2 - changing from "os.system" to using subprocess.call
# 2020-08-02 - v1.1 - Correcting a lot of things
# 2020-01-04 - v0.4 - Porting this script to python from bash

import argparse
import shlex
import time
import sys
import datetime
import platform
import subprocess

ELAPSED=0
TOTAL_ELAPSED=0
UP=True
FIRST_RUN=True
FQDN = ""
IP = ""
DELAY=1
BAD_DNS_MESSAGES = ["no address associated with name", "Unknown host", "Name or service not known", "cannot resolve"]

def is_it_plural(number):
    return("s" if int(number) != 1 else "")

def it_pings(target):
    global FIRST_RUN,FQDN,IP,HOST
    ping_command = shlex.split(COMMAND)
    ping_command.append(HOST)
    result = subprocess.Popen(ping_command,stdout = subprocess.PIPE, stderr=subprocess.PIPE)
    stdout,stderr = result.communicate()
    returncode = result.returncode
    if stdout.decode('UTF-8') == "":
        #sys.exit(f"Error encountered: {stderr.decode('UTF-8')[6:-1]}")    
        if "cannot resolve" in stderr.decode('UTF-8'):
            print(f" Problem found resolving {HOST}.  Switching to pinging original IP, {IP}. ", end="")
            HOST = IP
    else:        
        FQDN = stdout.decode("utf-8").split(' ')[1]
        IP = stdout.decode("utf-8").split(' ')[2].replace('(',"").replace(')','').replace(':','')
        if args.debug:
            print(f"FQDN = {FQDN}")
            print(f"IP = {IP}")
        returncode = result.returncode
        return returncode == 0

if platform.system().lower()=='windows':
    print("Is windows still a thing?")
    sys.exit(2)
elif platform.system().lower() == "netbsd" or platform.system().lower() == "linux" or platform.system().lower() == "openbsd":
    COMMAND=f"ping -c 1 -w {DELAY}"
elif platform.system().lower() == "darwin" or platform.system().lower() == "freebsd":
    COMMAND=f"ping -c 1 -t {DELAY}"
else:
    print("I dunno what OS you are using, I guess.")
    sys.exit(3)

parser = argparse.ArgumentParser(description=f"{TITLE} v{VERSION}")
parser.add_argument(action='store', dest='host', help='The host to ping')
parser.add_argument('-l', '--log', action='store', dest='log', help='File to log to')
parser.add_argument('-b', '--bell', action='store_true', default=False, dest='bell', help='Ring a terminal bell on changes')
parser.add_argument('--debug', action='store_true', default=False, help="Create additional noise")
args = parser.parse_args()
HOST = args.host
LOG = args.log
BELL = args.bell
TOTAL_RUNTIME_START = time.time()
START_TIME = datetime.datetime.now().replace(microsecond=0).isoformat()
try:
    while True:
        ERROR = not it_pings(HOST)
        if FIRST_RUN:
            FQDN_DIFFERS = f"{FQDN}/" if HOST != FQDN else ""
            LOG_STRING = f", logging to {LOG}" if LOG else ""
            if LOG:
                try:
                    log_file = open(LOG,'at',1)
                except Exception as log_error:
                    sys.exit(f"Problem with that log file: {log_error}")    
                log_file.write(f" === Starting pings to {HOST} every {DELAY} second{is_it_plural(DELAY)} at {START_TIME} ===\n")
            if FQDN_DIFFERS == "" and IP == HOST:
                INFO_STRING = ""
            else:
                INFO_STRING = f"({FQDN_DIFFERS}{IP}) "       
            print(f" === Pinging {HOST} {INFO_STRING}every {DELAY} second{is_it_plural(DELAY)} until you hit CTRL+C{LOG_STRING} ===")
            FIRST_RUN = False
        if not ERROR and UP:
            # it pings, still up
            print("!", end='', flush=True)
        elif not ERROR and not UP:
            # it pings, recovers
            ELAPSED=time.time() - DOWNTIME_START
            TOTAL_ELAPSED+=ELAPSED
            print(" " + time.strftime("%H:%M:%S", time.gmtime(ELAPSED)) + " ", end='')
            print("!", end='', flush=True)
            if BELL: print("\a", end='')
            # if log yadda
            if LOG:
               log_file.write(f" + Ping loss to {HOST} ended at {datetime.datetime.now().replace(microsecond=0).isoformat()}")
               log_file.write(f" - {int(ELAPSED)} second{is_it_plural(int(ELAPSED))} elapsed.\n")
            UP=True
        elif ERROR and UP:
            # it does not ping, was up
            DOWNTIME_START = time.time()
            if BELL: print("\a", end='')
            # if log yadda
            if LOG:
                log_file.write(f" - Ping loss to {HOST} started at {datetime.datetime.now().replace(microsecond=0).isoformat()}.\n")
            UP=False
            print(".", end='', flush=True)
        elif ERROR and not UP:
            # it does not ping, was already down
            print(".", end='', flush=True)
        time.sleep(DELAY)
except KeyboardInterrupt:
    print(' Exiting...')
    if not UP:
        ELAPSED=time.time() - DOWNTIME_START
        TOTAL_ELAPSED+=ELAPSED
    STOP_TIME  = datetime.datetime.now().replace(microsecond=0).isoformat()
    TOTAL_RUNTIME_END=time.time()
    TOTAL_RUNTIME_ELAPSED=f'{time.strftime("%H:%M:%S", time.gmtime(TOTAL_RUNTIME_END - TOTAL_RUNTIME_START))}'
    TOTAL_DOWNTIME = time.strftime('%H:%M:%S', time.gmtime(TOTAL_ELAPSED))
    #print(f"A total of {int(TOTAL_ELAPSED)} second{is_it_plural(int(ELAPSED))} of unresponsive pings was seen in this run.")
    print(f" === Total runtime was {TOTAL_RUNTIME_ELAPSED}. Total downtime was {TOTAL_DOWNTIME}. ===")
    if LOG:
        log_file.write(f" === Stopping at {STOP_TIME} ===\n")
        log_file.write(f" === Total runtime was {TOTAL_RUNTIME_ELAPSED}. Total downtime was {TOTAL_DOWNTIME}. ===\n")
        log_file.close()

