#!/usr/bin/env python3
import subprocess
import os
import sys
import time
from multiprocessing import Process, Event

from flask import Flask, request, render_template

import led

APNAME = "sinar-cam"

app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

server = Process(target=app.run, kwargs={'host':'0.0.0.0', 'port':80})
stop_event = Event()


# check run with root
def check_root():
    if os.geteuid() != 0:
        print("You need to have root privileges to run this script.")
        sys.exit(1)


def check_wifi():
    try:
        output = subprocess.check_output(["iwgetid", "-r"])
        return output.decode("utf-8").strip()
    except:
        return False

def ap_exist():
    res = subprocess.check_output("nmcli connection show".split()).decode()
    return APNAME in res
    
# enable wifi access point
def enable_ap():
    led.red()
    # check_root()
    if ap_exist():
        res = subprocess.check_output(f"nmcli connection up {APNAME}".split()).decode()
        print(res)
    else:
        # create wifi access point
        cmd = ['nmcli',
               'con',
               'add',
               'con-name',
               APNAME,
               'ifname',
               'wlan0',
               'type',
               'wifi',
               'ssid',
               APNAME,
               'mode',
               'ap',
               'wifi.band',
               'bg',
               'wifi.channel',
               '6',
               'ipv4.method',
               'shared']
        print(subprocess.check_output(cmd).decode())
    

# disable wifi access point
def disable_ap():
    # check_root()
    if not ap_exist():
        print("Access point not exist")
        return
    print(subprocess.check_output(f"nmcli connection down {APNAME}".split()).decode())\
    

def connect_wifi(ssid, paswd):
    # check_root()
    time.sleep(0.5)
    print("scanning wifi")
    subprocess.call("nmcli device wifi rescan".split())
    print("connecting to wifi")
    cmd = ['nmcli',
           'dev',
           'wifi',
           'connect',
           ssid,
           'password',
           paswd]
    print(subprocess.check_output(cmd).decode())
    time.sleep(0.5)
    stop_event.set()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ssid = request.form['ssid']
        password = request.form['password']
        print(f"connect to ssid: {ssid} with password: {password}")
        disable_ap()
        try:
            connect_wifi(ssid, password)
        except subprocess.CalledProcessError:
            led.blink()
            enable_ap()
    
    return render_template('index.html')


def setup():
    led.red()
    # check_root()
    if check_wifi():
        print("wifi connected")
        led.blue()
        return
        # sys.exit(0)

    print("no wifi connected, enabling ap")
    enable_ap()
    server.start()
    stop_event.wait()
    server.terminate()

if __name__ == "__main__":
    setup()


