#!/bin/bash
for i in {1..1000}
do
   echo "Starting $i Game"
   python server.py | grep "Finished" >> stats.dat &
   sleep 0.5
   python client.py
   sleep 0.5
done
