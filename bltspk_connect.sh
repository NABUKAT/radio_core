#!/bin/bash

function bltspk_connect(){
  echo 'connect '$1 \
    && sleep 5 \
    && echo 'quit'
}

bltspk_connect $1 | bluetoothctl

amixer sset Master $2\%

exit 0