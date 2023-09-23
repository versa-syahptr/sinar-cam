import gps
import time
import requests

import led


def get_from_ip():
    r = requests.get("https://ipinfo.io")
    return r.json()['loc'].split(',')


def get_from_gps(timeout=60):
    gps_session = gps.gps("localhost", "2947")
    gps_session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    start_time = time.time()
    print("waiting for gps signal")
    while time.time() - start_time < timeout:
        try:
            report = gps_session.next()
            if report['class'] == 'TPV':
                lat = getattr(report, 'lat', 0.0)
                lon = getattr(report, 'lon', 0.0)
                led.blink(led.green)
                return str(lat), str(lon)
        except KeyError:
            pass
        except KeyboardInterrupt:
            quit()
        except StopIteration:
            gps_session = None
            print("GPSD has terminated")
    print("GPS timeout")
    return False


def get_location():
    loc = get_from_gps()
    if not loc:
        loc = get_from_ip()
        led.blink(led.blue)
    return loc

