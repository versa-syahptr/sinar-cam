from argparse import ArgumentParser
import subprocess

import requests
import sys


import network
import led
from location import get_location

SINAR_URL = "sinar.versa.my.id"


def ping(): 
    try:
        r = requests.get(f"https://{SINAR_URL}/")
        print(f"{r.status_code}")
        if r.status_code == 200:
            led.green()
    except requests.exceptions.ConnectionError:
        print("connection error")
        led.blue()


def get_cam_id(lat, lon):
    r = requests.post(f"https://{SINAR_URL}/insert-cctv", json={"lat": lat, "lng": lon})
    return r.json()['data']['_id']


def write_args(cam_id=None, lat=None, lon=None, fname="arg"):
    with open(fname, 'w') as f:
        if cam_id:
            f.write(f'-id {cam_id}\n')
        if lat:
            f.write(f'-lat {lat}\n')
        if lon:
            f.write(f'-lon {lon}\n')


def verify_args(args):
    if not any((args.lat, args.lon, args.id)):
        if args.lat is None and args.lon is None:
            args.lat, args.lon = get_location()
            print(f"got lat: {args.lat}; lon: {args.lon}")
        if args.id is None:
            args.id = get_cam_id(args.lat, args.lon)
            print(f"got id: {args.id}")
        fname = next(filter(lambda x: x.startswith('@'), sys.argv))[1:] # get argv started with @
        write_args(args.id, args.lat, args.lat, fname)
        print(f"args written to {fname}")
    return args


def notify_tracker(cam_id, action="start"):
    if action not in ("start", "stop"):
        raise Exception(f"invalid action: {action}")
    r = requests.get(f"https://{SINAR_URL}/{action}-tracker/{cam_id}")
    print(f"{r.status_code} : {r.text}")

def stream_dvs(args):
    args = verify_args(args)
    device = args.device
    output = f"rtmp://{SINAR_URL}/input/{args.id}"

    cmd = ['ffmpeg',
            '-f',
            'v4l2',
            '-standard',
            'pal',
            '-video_size',
            '720x576',
            '-i',
            device,
            '-c:v',
            'libx264',
            '-preset',
            'ultrafast',
            '-tune',
            'zerolatency',
            '-f',
            'flv',
            output
    ]
    notify_tracker(args.id, "start")
    try:
        subprocess.run(cmd)
    except (KeyboardInterrupt, SystemExit):
        notify_tracker(args.id, "stop")
        print('Exiting...')

def stream_cam(args):
    output = f"rtmp://{SINAR_URL}/input/{args.id}"
    subprocess.run(["cam.sh", output])
    

def stream_push(input):
    raise NotImplementedError


if __name__ == '__main__':
    # do network setup before everything else
    network.setup()

    parser = ArgumentParser(
        prog='sinar-cam', 
        description='Sinar Camera Streaming',
        fromfile_prefix_chars='@'
    )
    parser.convert_arg_line_to_args = lambda line: line.split()

    mode = parser.add_subparsers(title="mode" ,dest='mode', help='sub-command help')

    cam_cmd = mode.add_parser('cam', help='sinar-cam mode')
    dvs_cmd = mode.add_parser('dvs', help='sinar-dvs mode')
    push_cmd = mode.add_parser('push', help='sinar-push mode')


    for cmd in [cam_cmd, dvs_cmd, push_cmd]:
        cmd.add_argument('-id', help='id of the camera')
        cmd.add_argument('-lat', help='latitude of the camera')
        cmd.add_argument('-lon', help='longitude of the camera')
        # cmd.set_defaults(func=stream_cam)
    
    dvs_cmd.add_argument('device', help='video device for dvs')
    push_cmd.add_argument('input', help='input stream for push')

    ping()

    cam_cmd.set_defaults(func=stream_cam)
    dvs_cmd.set_defaults(func=stream_dvs)
    push_cmd.set_defaults(func=stream_push)


    args = parser.parse_args()
    args.func(args)
    
