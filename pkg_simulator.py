#!/usr/bin/env python

""" A simple beacon transmitter class to send a 1-byte message (0x0f) in regular time intervals. """

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


import sys
import time
import logging

from time import sleep
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD


#Logger de funcionamiento interno de la libreria
loggerpy = logging.getLogger('pyLora Logger')
loggerpy.setLevel(logging.INFO)
fh1 = logging.FileHandler('/data/fossa/fossasat1-gs/logs/pkg-simulator.log')
fh1.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s]')
fh1.setFormatter(formatter)
loggerpy.addHandler(fh1)

BOARD.setup()

parser = LoRaArgumentParser("A simple LoRa beacon")
parser.add_argument('--single', '-S', dest='single', default=False, action="store_true", help="Single transmission")
parser.add_argument('--wait', '-w', dest='wait', default=1, action="store", type=float, help="Waiting time between transmissions (default is 0s)")

#constants
VOLTAGE_MULTIPLIER = 20 #20 mV resolution
VOLTAGE_UNIT = 1000
CURRENT_MULTIPLIER = 10 #10 uA resolution
CURRENT_UNIT = 1000000
TEMPERATURE_MULTIPLIER = 10 #0.01 deg C resolution
TEMPERATURE_UNIT = 1000
CALLSIGN = "FOSSASAT-1"

#status codes
ERR_NONE = 0
ERR_CALLSIGN_INVALID = -1
ERR_FRAME_INVALID = -2
ERR_INCORRECT_PASSWORD = -3
ERR_LENGTH_MISMATCH = -4

#communication protocol definitions
RESPONSE_OFFSET = b'0x10'
PRIVATE_OFFSET = b'0x20'

#public commands (unencrypted uplink messages)
CMD_PING = b'0x00'
CMD_RETRANSMIT = b'0x01'
CMD_RETRANSMIT_CUSTOM = b'0x02'
CMD_TRANSMIT_SYSTEM_INFO = b'0x03'
CMD_GET_LAST_PACKET_INFO = b'0x04'

#public responses (unencrypted downlink messages)
RESP_PONG = CMD_PING + RESPONSE_OFFSET
RESP_REPEATED_MESSAGE = CMD_RETRANSMIT + RESPONSE_OFFSET
RESP_REPEATED_MESSAGE_CUSTOM = CMD_RETRANSMIT_CUSTOM + RESPONSE_OFFSET
RESP_SYSTEM_INFO = CMD_TRANSMIT_SYSTEM_INFO + RESPONSE_OFFSET
RESP_LAST_PACKET_INFO = CMD_GET_LAST_PACKET_INFO + RESPONSE_OFFSET

def print_menu():

    choice ='0'
    while choice =='0':
       print("")
       print("*****************FOSSASAT1-GS******************")
       print("[1] Send PING")
       print("[2] Send Relay Message")
       print("[3] Send Custom Relay Message")
       print("[4] Send Clain Sat INFO")
       print("[9] Exit")
       print("***********************************************")
       print("")

       choice = input ("Choose an option: ")

       if choice == "9":
          break
       elif choice == "1":
          message = b'FOSSASAT-1\x00'
       elif choice == "2":
          millis = int(round(time.time() * 1000))
          print(millis)
          message = b'FOSSASAT-1\x01\x0C:' + bytearray(str(millis),'utf-8') + b':YGG-GS01:41.4069:2.1822'
       elif choice == "3":
          millis = int(round(time.time() * 1000))
          message = b'FOSSASAT-1\x02\x00\x00\x00\x00\x00\x00\x00\x00' + bytearray(str(millis),'utf-8') + b':YGG-GS01:41.4069:2.1822'
       elif choice == "4":
          message = b'FOSSASAT-1\x03'
       else:
          print("Unrecognized option")

    return message

class LoRaBeacon(LoRa):

    tx_counter = 0

    def __init__(self, verbose=False):
        loggerpy.info("[__init__][INI]")
        super(LoRaBeacon, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        loggerpy.info("[__init__][MODE.SLEEP]")
        self.set_dio_mapping([1,0,0,0,0,0])
        loggerpy.info("[__init__][FIN]")

    def on_rx_done(self):
        loggerpy.info("[on_rx_done][INI]")
        print("\nRxDone")
        print(self.get_irq_flags())
        print(map(hex, self.read_payload(nocheck=True)))
        self.set_mode(MODE.SLEEP)
        loggerpy.info("[on_rx_done][MODE.SLEEP]")
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        loggerpy.info("[on_rx_done][MODE.RXCONT]")
        loggerpy.info("[on_rx_done][FIN]")

    def on_tx_done(self):
        loggerpy.info("[on_tx_done][INI]")
        global args
        self.set_mode(MODE.STDBY)
        loggerpy.info("[on_tx_done][MODE.STDBY]")
        self.clear_irq_flags(TxDone=1)
        sys.stdout.flush()
        self.tx_counter += 1
        sys.stdout.write("\rtx #%d" % self.tx_counter)
        #if args.single:
        #    print
        #    sys.exit(0)
        #sleep(args.wait)
        #y = b'hola'
        #data = list(y)
        #self.write_payload(data)
        #self.set_mode(MODE.TX)
        loggerpy.info("[on_tx_done][FIN]")

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
        loggerpy.info("[start][INI]")
        global args
        self.tx_counter = 0
        out = True
        while out:
            message = print_menu()
            if message != "X":
                self.write_payload(list(message))
                self.set_mode(MODE.TX)
                loggerpy.info("[start][MODE.TX]")
                sleep(2)
            else:
                out = False
        loggerpy.info("[start][FIN]")

lora = LoRaBeacon(verbose=False)
args = parser.parse_args(lora)
lora.set_pa_config(pa_select=1)
#lora.set_rx_crc(True)
#lora.set_agc_auto_on(True)
#lora.set_lna_gain(GAIN.NOT_USED)
#lora.set_coding_rate(CODING_RATE.CR4_6)
#lora.set_implicit_header_mode(False)
#lora.set_pa_config(max_power=0x04, output_power=0x0F)
#lora.set_pa_config(max_power=0x04, output_power=0b01000000)
#lora.set_low_data_rate_optim(True)
#lora.set_pa_ramp(PA_RAMP.RAMP_50_us)
lora.set_sync_word(0xFF)

print(lora)
#assert(lora.get_lna()['lna_gain'] == GAIN.NOT_USED)
assert(lora.get_agc_auto_on() == 1)

print("Beacon config:")
print("  Wait %f s" % args.wait)
print("  Single tx = %s" % args.single)
print("")
try: input("Press enter to start...")
except: pass

try:
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
