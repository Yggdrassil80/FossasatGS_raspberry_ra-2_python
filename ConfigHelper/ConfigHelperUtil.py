#!/usr/bin/python

import configparser as ConfigParser

def isMQTTActive():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read(["/data/fossa/fossasat1-gs/conf/fossa.conf"])
                t = cfg.get("MQTT", "isActive")
                return str(t)
        except:
                return "No informado"

def getStationName():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read(["/data/fossa/fossasat1-gs/conf/fossa.conf"])
                t = cfg.get("MQTT", "stationName")
                return str(t)
        except:
                return "Valor no informado"

def getStationLocation():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read(["/data/fossa/fossasat1-gs/conf/fossa.conf"])
                t = cfg.get("MQTT", "stationLocation")
                return str(t)
        except:
                return "Valor no informado"

def getMqttBroker():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read(["/data/fossa/fossasat1-gs/conf/fossa.conf"])
                t = cfg.get("MQTT", "broker")
                return str(t)
        except:
                return "Valor no informado"

def getMqttPort():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read(["/data/fossa/fossasat1-gs/conf/fossa.conf"])
                t = cfg.get("MQTT", "port")
                return int(t)
        except:
                return 0

def getMqttUsername():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read(["/data/fossa/fossasat1-gs/conf/fossa.conf"])
                t = cfg.get("MQTT", "username")
                return str(t)
        except:
                return "Valor no informado"

def getMqttPassword():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read(["/data/fossa/fossasat1-gs/conf/fossa.conf"])
                t = cfg.get("MQTT", "password")
                return str(t)
        except:
                return "Valor no informado"

def getMqttCertPath():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read(["/data/fossa/fossasat1-gs/conf/fossa.conf"])
                t = cfg.get("MQTT", "certPath")
                return str(t)
        except:
                return "Valor no informado"



