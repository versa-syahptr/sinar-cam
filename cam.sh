#!/bin/bash
OUTPUT="rtmp://0.0.0.0/live/tes"

if [ $# -eq 0 ]; then
    echo "output empty, using $OUTPUT"
#    exit 
else
    OUTPUT=$1
fi

raspivid -n -hf -vf -awb greyworld -o - -t 0 -fps 25 -w 480 -h 320 -b 1000000 | ffmpeg -re -f h264 \
    -framerate 25 -i - \
    -c:v copy \
    -preset ultrafast \
    -s 480x320 \
    -maxrate 200k \
    -bufsize 400k \
    -tune zerolatency \
    -x264opts keyint=15 \
    -f flv $OUTPUT
