#!/usr/bin/env python3

""" A simple continuous receiver class. """

# Copyright 2015 Mayer Analytics Ltd.
#
# This file is part of pySX127x.
#
# pySX127x is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pySX127x is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You can be released from the requirements of the license by obtaining a commercial license. Such a license is
# mandatory as soon as you develop commercial activities involving pySX127x without disclosing the source code of your
# own applications, or shipping pySX127x with a closed source product.
#
# You should have received a copy of the GNU General Public License along with pySX127.  If not, see
# <http://www.gnu.org/licenses/>.


from time import sleep
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD
import logging
import ConfigHelper
import paho.mqtt.client as paho
import datetime

BOARD.setup()
BOARD.reset()

parser = LoRaArgumentParser("Fossasat1 - Ground Station - Reciver")

#Logger for scientific data
logger = logging.getLogger('fossa_logger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('fossa-gs-data.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s]')
fh.setFormatter(formatter)
logger.addHandler(fh)

#Logger of reciver
loggerpy1 = logging.getLogger('pyLora Logger1')
loggerpy1.setLevel(logging.DEBUG)
fh2 = logging.FileHandler('fossa-gs.log')
fh2.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s]')
fh2.setFormatter(formatter)
loggerpy1.addHandler(fh2)

#constants
VOLTAGE_MULTIPLIER = 20 #20 mV resolution
VOLTAGE_UNIT = 1000
CURRENT_MULTIPLIER = 10 #10 uA resolution
CURRENT_UNIT = 1000000
TEMPERATURE_MULTIPLIER = 10 #0.01 deg C resolution
TEMPERATURE_UNIT = 1000

#status codes
ERR_NONE = 0
ERR_CALLSIGN_INVALID = -1
ERR_FRAME_INVALID = -2
ERR_INCORRECT_PASSWORD = -3
ERR_LENGTH_MISMATCH = -4

#communication protocol definitions
RESPONSE_OFFSET = 0x10
PRIVATE_OFFSET = 0x20

#public commands (unencrypted uplink messages)
CMD_PING = '\x00'
RESP_PONG = '\x10'
CMD_RETRANSMIT = '\x01'
RESP_RETRANSMIT = '\x11'
CMD_RETRANSMIT_CUSTOM = '\x02'
RESP_RETRANSMIT_CUSTOM = '\x12'
CMD_TRANSMIT_SYSTEM_INFO = '\x03'
RESP_TRANSMIT_SYSTEM_INFO = '\x13'
CMD_GET_LAST_PACKET_INFO = '\x04'
RESP_GET_LAST_PACKET_INFO = '\x14'

MQTT_ACTIVE = "1"

#Procedure to detect witch command are present into data
def get_command(cmd_byte):
    cmd = "undefined"
    try:
        if cmd_byte == CMD_PING:
            cmd = "CMD_PING"
        elif cmd_byte == RESP_PONG:
            cmd = "RESP_PONG"
        elif cmd_byte == CMD_RETRANSMIT:
            cmd = "CMD_RETRANSMIT"
        elif cmd_byte == RESP_RETRANSMIT:
            cmd = "RESP_RETRANSMIT"
        elif cmd_byte == CMD_RETRANSMIT_CUSTOM:
            cmd = "CMD_RETRANSMIT_CUSTOM"
        elif cmd_byte == RESP_RETRANSMIT_CUSTOM:
            cmd = "RESP_RETRANSMIT_CUSTOM"
        elif cmd_byte == CMD_TRANSMIT_SYSTEM_INFO:
            cmd = "CMD_TRANSMIT_SYSTEM_INFO"
        elif cmd_byte == RESP_TRANSMIT_SYSTEM_INFO:
            cmd = "RESP_TRANSMIT_SYSTEM_INFO"
        elif cmd_byte == CMD_GET_LAST_PACKET_INFO:
            cmd = "CMD_GET_LAST_PACKET_INFO"
        elif cmd_byte == RESP_GET_LAST_PACKET_INFO:
            cmd = "RESP_GET_LAST_PACKET_INFO"
        else:
            cmd = "undefined"
    except Exception as e:
        loggerpy1.error("[get_command][ERROR] " + e)
    return cmd

#Procedure to extract payload data from specific messages
def get_payload(cmd, pkg):
    loggerpy1.info("[get_payload][INI]")
    try:
        payload = ""
        for i in pkg:
            payload = payload + i
        if cmd != "CMD_PING" or cmd != "CMD_PONG":
            return payload[11:]
        else:
            return ""
    except Exception as e:
        loggerpy1.error("[get_payload][ERROR] " + e)
    return ""

#Class to implement continuos reception
class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):
        loggerpy1.info("[__init__][INI]")
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        loggerpy1.debug("[__init__][MODE.SLEEP]")
        self.set_dio_mapping([0] * 6)
        loggerpy1.info("[__init__][FIN]")

    def on_rx_done(self):
        try:
           loggerpy1.debug("[on_rx_done][INI]")
           print("\nRxDone")
           self.clear_irq_flags(RxDone=1)
           payload = self.read_payload(nocheck=True)
           msg = list(bytes(payload).decode("utf-8",'ignore'))
           logger.info(msg)
           print(msg)
           snr = self.get_pkt_snr_value()
           loggerpy1.debug("[on_rx_done][SNR: " + str(snr) + "]")
           command = get_command(msg[10])
           time = datetime.datetime.now()
           unixGSTime = time.timestamp() * 1000
           sendMsgMQTT(str(msg),command,str(unixGSTime))
           loggerpy1.debug("[on_rx_done][Get Command: " + str(command) + "]")
           payload1 = get_payload(command, msg)
           loggerpy1.debug("[on_rx_done][Get Process payload: " + str(payload1) + "]")
           logger.info(command + "|" + payload1)
           print(command + "|" + payload)
           self.set_mode(MODE.SLEEP)
           loggerpy1.debug("[on_rx_done][MODE.SLEEP]")
           sleep(1)
           self.reset_ptr_rx()
           loggerpy1.debug("[on_rx_done][Reset PTR]")
           sleep(1)
           self.set_mode(MODE.RXCONT)
           loggerpy1.debug("[on_rx_done][FIN]")
        except Exception as e:
           loggerpy1.error("[on_rx_done][ERROR] " + e)

    def on_tx_done(self):
        loggerpy1.info("[on_tx_done][INI]")
        print("\nTxDone")
        print(self.get_irq_flags())
        loggerpy1.info("[on_tx_done][FIN]")

    def on_cad_done(self):
        print("\non_CadDone")
        print(self.get_irq_flags())

    def on_rx_timeout(self):
        print("\non_RxTimeout")
        print(self.get_irq_flags())

    def on_valid_header(self):
        print("\non_ValidHeader")
        print(self.get_irq_flags())

    def on_payload_crc_error(self):
        print("\non_PayloadCrcError")
        print(self.get_irq_flags())

    def on_fhss_change_channel(self):
        print("\non_FhssChangeChannel")
        print(self.get_irq_flags())

    def start(self):
        loggerpy1.info("[start][INI]")
        loggerpy1.info("[start][Reset PTR]")
        self.reset_ptr_rx()
        loggerpy1.info("[start][Reset PTR]")
        self.set_mode(MODE.RXCONT)
        loggerpy1.info("[start][MODE.RXCONT]")
        while True:
            sleep(5)
            rssi_value = self.get_rssi_value()
            snr = self.get_pkt_snr_value()
            status = self.get_modem_status()
            sys.stdout.flush()
            #sys.stdout.write("\r%d %d %d" % (rssi_value, status['rx_ongoing'], status['modem_clear']))
            rxo = status['rx_ongoing']
            loggerpy1.info("[start][rssi: " + str(rssi_value) + "][snr: " + str(snr) + "][rx_ongoing: " + str(rxo) + "]")


                #rx_coding_rate    = status >> 5 & 0x03,
                #modem_clear       = status >> 4 & 0x01,
                #header_info_valid = status >> 3 & 0x01,
                #rx_ongoing        = status >> 2 & 0x01,
                #signal_sync       = status >> 1 & 0x01,
                #signal_detected   = status >> 0 & 0x01



            #self.reset_ptr_rx()
            #loggerpy1.info("[start][Reset PTR]")
            #sleep(5)
        loggerpy1.info("[start][FIN]")

#Procedure thats send station status to MQTT server
def sendStatusMQTT(status):
    act = ConfigHelper.isMQTTActive()
    try:
        if act == MQTT_ACTIVE:

            loggerpy1.info("[sendStatusMQTT][INI]")
            broker = ConfigHelper.getMqttBroker()
            loggerpy1.debug("[sendStatusMQTT][broker: " + broker + "]")
            port = ConfigHelper.getMqttPort()
            loggerpy1.debug("[sendStatusMQTT][port: " + str(port) + "]")
            username = ConfigHelper.getMqttUsername()
            loggerpy1.debug("[sendStatusMQTT][username: " + username + "]")
            password= ConfigHelper.getMqttPassword()
            loggerpy1.debug("[sendStatusMQTT][password: " + password + "]")
            certPath = ConfigHelper.getMqttCertPath()
            loggerpy1.debug("[sendStatusMQTT][certpath: " + certPath + "]")
            loggerpy1.debug("[sendStatusMQTT][Config Params read OK]")

            client1 = paho.Client()
            client1.on_publish = on_publish
            client1.on_connect = on_connect
            client1.tls_set(certPath)
            client1.username_pw_set(username, password)
            loggerpy1.info("[sendStatusMQTT][Starting connection mqtt service...")
            rc = client1.connect(broker, port)
            loggerpy1.info("[sendStatusMQTT][Mqtt service connected OK]")
            ret = client1.publish(stationName + "/status", status)
            client1.disconnect()
        else:
            loggerpy1.info("[sendStatusMQTT][MQTT Disconnect by Conf]")
    except Exception as e:
        loggerpy1.error("[sendStatusMQTT][ERROR] " + e)

#Procedure to send welcome message to MQTT Server
def sendWelcomeMQTT(stationName, StationLoc, ver):
    act = ConfigHelper.isMQTTActive()
    if act == MQTT_ACTIVE:
        msg = createWelcomeMessage(stationName, StationLoc, ver)
        loggerpy1.info("[sendWelcomeMQTT][INI]")
        broker = ConfigHelper.getMqttBroker()
        loggerpy1.debug("[sendWelcomeMQTT][broker: " + broker + "]")
        port = ConfigHelper.getMqttPort()
        loggerpy1.debug("[sendWelcomeMQTT][port: " + str(port) + "]")
        username = ConfigHelper.getMqttUsername()
        loggerpy1.debug("[sendWelcomeMQTT][username: " + username + "]")
        password= ConfigHelper.getMqttPassword()
        loggerpy1.debug("[sendWelcomeMQTT][password: " + password + "]")
        certPath = ConfigHelper.getMqttCertPath()
        loggerpy1.debug("[sendWelcomeMQTT][certpath: " + certPath + "]")
        loggerpy1.debug("[sendWelcomeMQTT][Config Params read OK]")

        client1 = paho.Client()
        client1.on_publish = on_publish
        client1.on_connect = on_connect
        client1.tls_set(certPath)
        client1.username_pw_set(username, password)
        loggerpy1.info("[sendWelcomeMQTT][Starting connection mqtt service...")
        rc = client1.connect(broker, port)
        loggerpy1.info("[sendWelcomeMQTT][Mqtt service connected OK]")
        ret = client1.publish(stationName + "/welcome", msg)
        client1.disconnect()

def sendMsgMQTT(message,command,unixGSTime):
    act = ConfigHelper.isMQTTActive()

    try:
        if act == MQTT_ACTIVE:

            loggerpy1.info("[sendMsgMQTT][INI]")
            broker = ConfigHelper.getMqttBroker()
            loggerpy1.debug("[sendMsgMQTT][broker: " + broker + "]")
            port = ConfigHelper.getMqttPort()
            loggerpy1.debug("[sendMsgMQTT][port: " + str(port) + "]")
            username = ConfigHelper.getMqttUsername()
            loggerpy1.debug("[sendMsgMQTT][username: " + username + "]")
            password= ConfigHelper.getMqttPassword()
            loggerpy1.debug("[sendMsgMQTT][password: " + password + "]")
            certPath = ConfigHelper.getMqttCertPath()
            loggerpy1.debug("[sendMsgMQTT][certpath: " + certPath + "]")
            loggerpy1.debug("[sendMsgMQTT][Config Params read OK]")
            print("pasa5")
            msg=createMessage(message,command,unixGSTime)
            print("pasa6 msg " + str(msg))

            client1 = paho.Client()
            client1.on_publish = on_publish
            client1.on_connect = on_connect
            client1.tls_set(certPath)
            client1.username_pw_set(username, password)
            loggerpy1.info("[sendMsgMQTT][Starting connection mqtt service...")
            rc = client1.connect(broker, port)
            loggerpy1.info("[sendMsgMQTT][Mqtt service connected OK]")

            #if msg[0] == "S":
            #    print("pasa7")
            #    ret = client1.publish(stationName + "/sys_info", msg[1:])
            #else:
            #    ret = client1.publish(stationName + "/msg", msg)
            client1.disconnect()
        else:
            loggerpy1.info("[sendMsgMQTT][MQTT Disconnect by Conf]")
    except Exception as e:
        loggerpy1.info("[sendMsgMQTT][ERROR] " + e)

#Procedure to create a message for MQTT using command information
def createMessage(msg,command,unixGSTime):

    loggerpy1.info("[createMessage][INI]")
    #detectar de que tipo de mensaje se trata
    data = ""
    #Ejemplos tipos de mensaje
    #Galile0/welcome {"station":"G4lile0","station_location":[40.64,-3.98],"version":1912042}
    #Galile0/sys_info {"station":"G4lile0","station_location":[40.64,-3.98],"rssi":-39,"snr":12.25,"frequency_error":4782.031,"batteryChargingVoltage":2.7,"batteryChargingCurrent":4,"batteryVoltage":3.38,"solarCellAVoltage":0.96,"solarCellBVoltage":1,"solarCellCVoltage":1.06,"batteryTemperature":-36.61,"boardTemperature":36.63,"mcuTemperature":14,"resetCounter":0,"powerConfig":255}
    #Galile0/pong {"station":"G4lile0","station_location":[40.64,-3.98],"rssi":-36,"snr":12.5,"frequency_error":4408.738}
    #Galile0/msg {"station":"G4lile0","station_location":[40.64,-3.98],"rssi":-39,"snr":12.25,"frequency_error":4710.728,"msg":"Transmission test 4-dec"}

    try:
        stationName = ConfigHelper.getStationName()
        stationLoc = ConfigHelper.getStationLocation()

        rssi = "0.0"
        snr = "0.0"
        freqErr = "0.0"
        batteryChargingVoltage = "0.0"
        batteryChargingCurrent = "0.0"
        batteryVoltage = "0.0"
        solarCellAVoltage = "0.0"
        solarCellBVoltage = "0.0"
        solarCellCVoltage = "0.0"
        batteryTemperature = "0.0"
        boardTemperature = "0.0"
        mcuTemperature = "0.0"
        resetCounter = "0"
        powerConfig = "255"

        payload = get_payload(command, msg)
        if command == RESP_PONG: #0x10
            loggerpy1.info("[createMessage][Processing PONG...]")
            data = createPongMessage(stationName, stationLoc, unixGSTime)
        if command == RESP_RETRANSMIT:
            data = "{\"station\":\"" + stationName + "\",\"station_location\":[" + stationLoc + "],\"rssi\":" + rssi + ",\"snr\":" + snr + ",\"frequency_error\":" + freqErr + ",\"msg\":" + payload  + "}"
        if command == RESP_RETRANSMIT_CUSTOM:
            data = "{\"station\":\"" + stationName + "\",\"station_location\":[" + stationLoc + "],\"rssi\":" + rssi + ",\"snr\":" + snr + ",\"frequency_error\":" + freqErr + ",\"msg\":" + payload  + "}"
        if command == RESP_GET_LAST_PACKET_INFO:
            data = "{\"station\":\"" + stationName + "\",\"station_location\":[" + stationLoc + "],\"rssi\":" + rssi + ",\"snr\":" + snr + ",\"frequency_error\":" + freqErr + ",\"msg\":" + payload  + "}"
        if command == RESP_TRANSMIT_SYSTEM_INFO: #0x13
            loggerpy1.info("[createMessage][Processing SYS_INFO...]")
            batteryChargingVoltage = "0.0"
            batteryChargingCurrent = "0.0"
            batteryVoltage = "0.0"
            solarCellAVoltage = "0.0"
            solarCellBVoltage = "0.0"
            solarCellCVoltage = "0.0"
            batteryTemperature = "0.0"
            boardTemperature = "0.0"
            mcuTemperature = "0.0"
            resetCounter = "0"
            powerConfig = "255"
            data = "{\"station\":\"" + stationName + "\",\"station_location\":[" + stationLoc + "],\"rssi\":" + rssi + ",\"snr\":" + snr + ",\"frequency_error\":" + freqErr + ",\"batteryChargingVoltage\":" + batteryChargingVoltage + ",\"batteryChargingCurrent\":" + batteryChargingCurrent + ",\"batteryVoltage\":" + batteryChargingCurrent + ",\"solarCellAVoltage\":" + solarCellAVoltage + ",\"solarCellBVoltage\":" + solarCellBVoltage + ",\"solarCellCVoltage\":" + solarCellBVoltage + ",\"batteryTemperature\":" + batteryTemperature + ",\"boardTemperature\":" + boardTemperature + ",\"mcuTemperature\":" + mcuTemperature + ",\"resetCounter\":" + resetCounter + ",\"powerConfig\":" + powerConfig + "}"

    except Exception as e:
        loggerpy1.error("[createMessage][ERROR] " + e)

    return data

#Procedure to create a pong menssage for mqtt
def createPongMessage(stationName, stationLocation, unixGSTime):

    rssi = "0.0"
    snr = "0.0"
    freqErr = "0.0"

    msg = "{\"station\":\"" + stationName + "\",\"station_location\":[" + stationLocation + "],\"unix_GS_time\":" + str(unixGSTime) + ",\"rssi\":" + rssi + ",\"snr\":" + snr + ",\"frequency_error\":" + freqErr + ",\"pong\":1}"

    loggerpy1.debug("[createPongMessage][" + msg + "]")

    return msg

#Procedure to create welcome message
def createWelcomeMessage(station, stationLocation, version):

    message1 = "\n\r{\"station\":\"" + station + "\",\"station_location\":"
    message2 = "[" + stationLocation + "],\"version\":" + version + "}"
    return message1 + message2

def on_publish(client, userdata, result):
    loggerpy1.info("[on_publish][Data published with code: " + str(result) + "]")
    pass

def on_connect(client, userdata, flags,rc):
    loggerpy1.info("[on_connect][Connected with code: " + str(rc) + "]")

#######################################################################################################
#                                  fossasat-1-gs main code                                            #
#######################################################################################################

lora = LoRaRcvCont(verbose=False)
args = parser.parse_args(lora)

lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1)
#lora.set_rx_crc(True)
#lora.set_coding_rate(CODING_RATE.CR4_6)
#lora.set_pa_config(max_power=0, output_power=0)
#lora.set_lna_gain(GAIN.G1)
#lora.set_implicit_header_mode(False)
#lora.set_low_data_rate_optim(True)
#lora.set_pa_ramp(PA_RAMP.RAMP_50_us)
#lora.set_agc_auto_on(True)

#lora.set_sync_word(int.from_bytes(b'\x0F\x0F', "big"))
lora.set_sync_word(0xFF)


#print SX12XX registers
loggerpy1.debug("[Main] " + str(lora))
print(lora)

assert(lora.get_agc_auto_on() == 1)

#try: input("Press enter to start...")
#except: pass
sleep(1)

try:
    stationName = ConfigHelper.getStationName()
    loggerpy1.info("[MqttService][stationName: " + stationName + "]")
    stationLocation = ConfigHelper.getStationLocation()
    loggerpy1.info("[MqttService][stationLocation: " + stationLocation + "]")
    sendWelcomeMQTT(stationName, stationLocation, "YGG Custom Version")
    sendStatusMQTT(1)
    lora.set_mode(MODE.STDBY)
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    print(lora)
    BOARD.teardown()
    sendStatusMQTT(0)