#!/bin/bash

progname="radiko_client"
proc="/opt/radio_core/radiko.sh"

case "$1" in
start)
  echo -n $"Starting $progname: "
  nohup $proc -p "$2" > /dev/null &
;;
stop)
  echo -n $"Stopping $progname: "
  proc=`ps alx | grep [f]fplay | head -n 1 | awk '{print $3}'`
  kill $proc
  proc=`ps alx | grep [f]fplay | head -n 1 | awk '{print $3}'`
  kill $proc
;;
*)
  echo $"Usage: $0 {start|stop}"
  exit 1
esac

exit $RETVAL
