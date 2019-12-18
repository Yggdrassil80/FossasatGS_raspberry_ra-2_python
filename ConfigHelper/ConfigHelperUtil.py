#!/usr/bin/python

import ConfigParser as ConfigParser

CONF_PATH = "/data/fossa/fossasat1-gs/conf/fossa.conf"

def getFrecuency():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("LORA", "frequency")
                return str(t)
        except:
                return "No informado"

def getSpreadFactor():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("LORA", "spreadFactor")
                return str(t)
        except:
                return "No informado"

def getBW():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("LORA", "bw")
                return str(t)
        except:
                return "No informado"

def getSyncWord():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("LORA", "syncWord")
                return str(t)
        except:
                return "No informado"

def getLongPreamble():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("LORA", "longpreamble")
                return str(t)
        except:
                return "No informado"

def getCodingRate():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("LORA", "codingRate")
                return str(t)
        except:
                return "No informado"

def isMQTTActive():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("MQTT", "isActive")
                return str(t)
        except:
                return "No informado"

def getStationName():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("MQTT", "stationName")
                return str(t)
        except:
                return "Valor no informado"

def getStationLocation():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("MQTT", "stationLocation")
                return str(t)
        except:
                return "Valor no informado"

def getMqttBroker():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("MQTT", "broker")
                return str(t)
        except:
                return "Valor no informado"

def getMqttPort():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("MQTT", "port")
                return int(t)
        except:
                return 0

def getMqttUsername():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("MQTT", "username")
                return str(t)
        except:
                return "Valor no informado"

def getMqttPassword():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("MQTT", "password")
                return str(t)
        except:
                return "Valor no informado"

def getMqttCertPath():
        try:
                cfg = ConfigParser.ConfigParser()
                cfg.read([CONF_PATH])
                t = cfg.get("MQTT", "certPath")
                return str(t)
        except:
                return "Valor no informado"



