#!/bin/bash

filecount=$(ps -e | grep screen -w | wc -l)

if [ "$filecount" -eq "0" ]; then
  cd security/
  screen -dmS sec python3 client.py

  while :
  do
    sleep 180
    pingres=$(ping 8.8.8.8 -c 4 | grep packets)
    pingres=(${pingres//;/ })
    echo ${pingres[0]}
    if [${pingres[0]} -eq "0"]; then
      reboot
    fi
  done
else
  echo "Program is already launched"
fi
