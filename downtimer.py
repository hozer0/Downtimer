#!/usr/bin/env python3
import argparse
import shlex
import time
import sys
import datetime
import platform
import subprocess
title = "Downtimer"
elapsed = 0
total_elapsed = 0
up = True
first_run = True
fqdn = ""
ip = ""
delay = 1
loss_count = 0
bad_dns_messages = ["no address associated with name", "Unknown host", "Name or service not known", "cannot resolve"]


def is_it_plural(number):
    """This simply adds an 's' if number is greater than one so signify plurality"""
    return "s" if int(number) != 1 else ""


def it_pings(target):
    """Does it ping?"""
    global first_run, fqdn, ip, host
    ping_command = shlex.split(command)
    ping_command.append(host)
    result = subprocess.Popen(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = result.communicate()
    returncode = result.returncode
    if stdout.decode('UTF-8') == "":
        if "cannot resolve" in stderr.decode('UTF-8') and ip:
            print(f" Problem found resolving {host}.  Switching to pinging original ip, {ip}. ", end="")
            host = ip
        elif "cannot resolve" in stderr.decode('UTF-8') and not ip:
            print(f"Cannot resolve {host}.")
            sys.exit(1)
    else:
        fqdn = stdout.decode("utf-8").split(' ')[1]
        ip = stdout.decode("utf-8").split(' ')[2].replace('(', "").replace(')', '').replace(':', '')
        returncode = result.returncode
        return returncode == 0


if platform.system().lower() == "netbsd" or platform.system().lower() == "linux" or platform.system().lower() == "openbsd":
    command = f"ping -c 1 -w {delay}"
elif platform.system().lower() == "darwin" or platform.system().lower() == "freebsd":
    command = f"ping -c 1 -t {delay}"
else:
    print("I dunno what OS you are using, I guess.")
    sys.exit(2)

parser = argparse.ArgumentParser(description=f"{title}")
parser.add_argument(action='store', dest='host', help='The host to ping')
parser.add_argument('-l', '--log', action='store', dest='log', help='File to log to')
parser.add_argument('-b', '--bell', action='store_true', default=False, dest='bell', help='Ring a terminal bell on changes')
parser.add_argument('-p', '--acceptable-loss', action='store', default=1, dest='ok_loss', help='How many dropped pings are excusable.')
args = parser.parse_args()
host = args.host
log = args.log
bell = args.bell
ok_loss = int(args.ok_loss)
total_runtime_start = time.time()
start_time = datetime.datetime.now().replace(microsecond=0).isoformat()
try:
    while True:
        error = not it_pings(host)
        if first_run:
            fqdn_differs = f"{fqdn}/" if host != fqdn else ""
            log_string = f", logging to {log}" if log else ""
            if log:
                try:
                    log_file = open(log, 'at', 1)
                except Exception as log_error:
                    sys.exit(f"Problem with that log file: {log_error}")
                log_file.write(
                    f" === Starting pings to {host} every {delay} second{is_it_plural(delay)} at {start_time} ===\n")
            if fqdn_differs == "" and ip == host:
                info_string = ""
            else:
                info_string = f"({fqdn_differs}{ip}) "
            print(
                f" === Pinging {host} {info_string}every {delay} second{is_it_plural(delay)} until you hit CTRL+C{log_string} ===")
            first_run = False
        if not error and up:
            # it pings, still up
            print("!", end='', flush=True)
        elif not error and not up:
            # it pings, recovers
            elapsed = time.time() - downtime_start
            total_elapsed += elapsed
            print(" " + time.strftime("%H:%M:%S",
                                      time.gmtime(elapsed)) + " ", end='')
            print("!", end='', flush=True)
            if bell:
                print("\a", end='')
            if log:
                log_file.write(
                    f" + Ping loss to {host} ended at {datetime.datetime.now().replace(microsecond=0).isoformat()}")
                log_file.write(
                    f" - {int(elapsed)} second{is_it_plural(int(elapsed))} elapsed.\n")
            up = True
        elif error and up:
            # it does not ping, was up
            downtime_start = time.time()
            if bell:
                print("\a", end='')
            if log:
                log_file.write(
                    f" - Ping loss to {host} started at {datetime.datetime.now().replace(microsecond=0).isoformat()}.\n")
            up = False
            print(".", end='', flush=True)
        elif error and not up:
            # it does not ping, was already down
            print(".", end='', flush=True)
        time.sleep(delay)
except KeyboardInterrupt:
    print(' Exiting...')
    if not up:
        elapsed = time.time() - downtime_start
        total_elapsed += elapsed
    stop_time = datetime.datetime.now().replace(microsecond=0).isoformat()
    total_runtime_end = time.time()
    total_runtime_elapsed = f'{time.strftime("%H:%M:%S", time.gmtime(total_runtime_end - total_runtime_start))}'
    total_downtime = time.strftime('%H:%M:%S', time.gmtime(total_elapsed))
    print(
        f" === Total runtime was {total_runtime_elapsed}. Total downtime was {total_downtime}. ===")
    if log:
        log_file.write(f" === Stopping at {stop_time} ===\n")
        log_file.write(
            f" === Total runtime was {total_runtime_elapsed}. Total downtime was {total_downtime}. ===\n")
        log_file.close()
