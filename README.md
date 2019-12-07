# Libraries needed

pip3 install paho-mqtt
pip3 install configparser 

# Startup Commands

## Start Reciver

python3 fossasat1.py -s 11 -f 436.700 -b BW125 --cr CR4_8 -p 32

## Start Sender

python3 sender_fossasat1.py -s 11 -f 436.700 -b BW125 --cr CR4_8 -p 32 -S

## Start Reciver as a Service

Two previous configurations works with a cmd console printing the results on the screen (NOTE: all events are writed into logs too).

But, if you prefer start raspberry and dont check or start anything, you can create a service in raspbian.

To create a Revicer service, you can do this:

1. Edit <home>/services/fossaService.service

'''
[Unit]
Description=Fossa Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /data/fossa/fossasat1-gs/fossasat1.py -s 11 -f 436.700 -b BW125 --cr CR4_8 -p 32 
Restart=always
RestartSec=0

[Install]
WantedBy=multi-user.target
'''

NOTE: For fossasat1 "-p 32" configuration is actually not confirmed, only supposed.

and change all needed configurations

2. Execute: 

sudo cp fossaService.service /etc/systemd/system/fossaService.service"

3. Execute:

sudo systemctl daemon-reload 

4. Execute:

sudo systemctl enable fossaService.service

5. Execute

sudo systemctl start fossaService.service

NOTE: use "stop" instead of "start" if you will stop service

IMPORTANT: For startup errors in service, you can check /var/data/syslog o /var/data/daemon.log

# Configuration

There are some configuration placed here conf/fossa.conf

[MQTT] <-- Section of MQTT confs 
broker=fossa.apaluba.com <-- MQTT Broker 
port=8883 <-- MQTT port 
username= <-- MQTT 
username (ask G0lile4) 
password= <-- MQTT password (ask G0lile4) 
certPath=/data/fossa/fossasat1-gs/fossa-mqtt.crt <-- path where are placed the certificate needed to connect to MQTT server 
tiempoEnvio=2 <-- at moment not used 
stationName=YGG-GS02 <-- station name 
stationLocation=42.3071,2.2102 <-- station location 
isActive=1 <-- flag to activate or desactivate (1/0) send information to MQTT server

IMPORTANT: 

- To use this parameters the function that can read them are placed in ConfigHelper python module. Is you add, modify or delete configuration, is necessary modify these code.
- Another important thing is that all functions has hardcoded the conf path (sorry ;))

# Design

TODO

# Logs

At the moment, all logs are placed staticly here /data/fossa/fossasat1/logs 

- /data/fossa/fossasat1-gs/logs/fossasat-1.log: All data recived and parsed is stored here
- /data/fossa/fossasat1-gs/logs/Reciver_pyLora.log: All data about Reciver functionaly
- /data/fossa/fossasat1-gs/logs/Sender_pyLora.log: All data about Sender functionality

# Credits

The code of this project are mainly based in two public repositories

- https://pypi.org/project/paho-mqtt/:

Where is possible to find all configurations and much more information about MQTT communications with python.

- https://pypi.org/project/pyLoRa/

Here there are a very good examples about how to build a sender and reciver with raspberry pi and ra_02 LoRa chipset.

NOTE: Related pinout, we only use SPI wiring and GPIO4 for IRQ.
