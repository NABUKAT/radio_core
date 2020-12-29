#!/bin/bash

function bltspk_status(){
  echo 'info '$1 \
    && sleep 1 \
    && echo 'quit'
}

ret=`bltspk_status $1 | bluetoothctl | grep Connected | grep no | wc -l`

exit $ret