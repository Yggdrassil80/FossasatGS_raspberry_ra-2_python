import paho.mqtt.client as paho
import ConfigHelper
import logging

#broker = "fossa.apaluba.com"
#port = 8883

loggermqtt = logging.getLogger('mqtt Logger1')
loggermqtt.setLevel(logging.INFO)
fh3 = logging.FileHandler('/data/fossa/fossasat1-gs/logs/mqttService.log')
fh3.setLevel(logging.INFO)
formatter1 = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s]')
fh3.setFormatter(formatter1)
loggermqtt.addHandler(fh3)

def createWelcomeMessage(station, stationLocation, version):

    message1 = "\n\r{\"station\":\"" + station + "\",\"station_location\":"
    message2 = "[" + stationLocation + "],\"version\":" + version + "}"
    return message1 + message2

def createMsgInfoMessage(stationName, stationLocation):

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
    data = "{\"station\":\"" + stationName + "\",\"station_location\":[" + stationLocation + "],\"rssi\":" + rssi + ",\"snr\":" + snr + ",\"frequency_error\":" + freqErr + ",\"batteryChargingVoltage\":" + batteryChargingVoltage + ",\"batteryChargingCurrent\":" + batteryChargingCurrent + ",\"batteryVoltage\":" + batteryChargingCurrent + ",\"solarCellAVoltage\":" + solarCellAVoltage + ",\"solarCellBVoltage\":" + solarCellBVoltage + ",\"solarCellCVoltage\":" + solarCellBVoltage + ",\"batteryTemperature\":" + batteryTemperature + ",\"boardTemperature\":" + boardTemperature + ",\"mcuTemperature\":" + mcuTemperature + ",\"resetCounter\":" + resetCounter + ",\"powerConfig\":" + powerConfig + "}"

    return data

def createPongMessage(stationName, stationLocation, unixGSTime):

    rssi = "0.0"
    snr = "0.0"
    freqErr = "0.0"

    part1 = "{\"station\":\"" + stationName + "\",\"station_location\":["
    part2 = stationLocation + "],\"unix_GS_time\":" + str(unixGSTime) + ",\"rssi\":" + rssi + ",\"snr\":" + snr 
    part3 = ",\"frequency_error\":" + freqErr + ",\"pong\":1}"

    print("[createPongMessage][" + part1 + part2 + part3 + "]")

    return part1 + part2 + part3

def createRelayMessage(stationName, stationLocation):
    
    return stationName + "Dummy Relay Message"



def on_publish(client, userdata, result):
    #loggermqtt.info("[on_publish][Data published with code: " + str(result) + "]")
    print("[on_publish][Data published with code: " + str(result) + "]")
    print("publicado con code: " + str(result))
    print("data published \n")
    pass

def on_connect(client, userdata, flags,rc):
    #loggermqtt.info("[on_connect][Connected with code: " + str(rc) + "]")
    print("[on_connect][Connected with code: " + str(rc) + "]")
    print("Conected with code: " + str(rc))

try:

    loggermqtt.info("[MqttService][INI]")
    broker = ConfigHelper.getMqttBroker()
    loggermqtt.info("[MqttService][broker: " + broker + "]")
    port = ConfigHelper.getMqttPort()
    loggermqtt.info("[MqttService][port: " + str(port) + "]")
    username = ConfigHelper.getMqttUsername()
    loggermqtt.info("[MqttService][username: " + username + "]")
    password= ConfigHelper.getMqttPassword()
    loggermqtt.info("[MqttService][password: " + password + "]")
    certPath = ConfigHelper.getMqttCertPath()
    loggermqtt.info("[MqttService][certpath: " + certPath + "]")
    stationName = ConfigHelper.getStationName()
    loggermqtt.info("[MqttService][stationName: " + stationName + "]")
    stationLocation = ConfigHelper.getStationLocation()
    loggermqtt.info("[MqttService][stationLocation: " + stationLocation + "]")
    loggermqtt.info("[MqttService][Config Params read OK]")
    client1 = paho.Client()
    client1.on_publish = on_publish
    client1.on_connect = on_connect

#client1.tls_set("path_toca.crt")
    #client1.tls_set("/data/mqtt_test/fossa-mqtt.crt")
    client1.tls_set(certPath)
    client1.username_pw_set(username, password)
    loggermqtt.info("[MqttService][Starting connection mqtt service...")
    rc = client1.connect(broker, port)
    loggermqtt.info("[MqttService][Mqtt service connected OK]")
#print ("Publicando en /msg")
#ret = client1.publish("YGGGS01/msg","[YGG-GS01:mqtt_pusblish_test]")

#print ("Publicando en /sysinfo")
#ret = client1.publish("YGGGS01/sys_info","[YGG-GS01:mqtt_pusblish_test]")

    welcomeMessage = createWelcomeMessage(stationName, stationLocation, "YGG_custom")
    loggermqtt.info("[MqttService][welcomeMessage: " + welcomeMessage + "]")
    statusMessage = ""
    dataMessage = createMsgInfoMessage(stationName, stationLocation)
    loggermqtt.info("[MqttService][dataMessage: " + dataMessage + "]")
    pongMessage = createPongMessage(stationName, stationLocation, 1576447659)
    loggermqtt.info("[MqttService][pongMessage: " + pongMessage + "]")

    print ("Publicando en /welcome")
    #message = "\n\r{\"station\":\"YGG-GS01\",\"station_location\":[41.40,2.18],\"version\":1912042}"
    #msg = bytes(welcomeMessage).encode('utf-8')
    
    ret = client1.publish(stationName + "/welcome",welcomeMessage)
    
    ret = client1.publish(stationName + "/sys_info", dataMessage)

    ret = client1.publish(stationName + "/status", "1")

    ret = client1.publish(stationName + "/pong", pongMessage)

    #ret = client1.publish(stationName + "/relay", relayMessage)

    ret = client1.publish(stationName + "/status", "0")

#print ("Publicando en /status")
#ret = client1.publish("YGGGS01/status","[YGG-GS01:mqtt_pusblish_test]")
except Exception, e:
    print(e)
    print("ERROR")
