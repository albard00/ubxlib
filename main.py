#!/usr/bin/python3

import time
import logging

from ubxlib.server import GnssUBlox
from ubxlib.ubx_ack import UbxAckAck
from ubxlib.ubx_cfg_tp5 import UbxCfgTp5Poll
from ubxlib.ubx_upd_sos import UbxUpdSosPoll, UbxUpdSosAction
from ubxlib.ubx_mon_ver import UbxMonVerPoll


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('gnss_tool')
logger.setLevel(logging.DEBUG)


msg_stop = bytearray.fromhex('06 04 04 00 00 00 08 00')    # stop
msg_cold_start = bytearray.fromhex('06 04 04 00 FF FF 01 00')  # Cold Start
msg_cfg_port_poll = bytearray.fromhex('06 00 01 00 01')  # UBX-CFG-PRT poll
msg_nav_status_poll = bytearray.fromhex('01 03 00 00')

# msg_cfg_port_uart_9600 = bytearray.fromhex('06 00 14 00 01 00 00 00 c0 08 00 00 80 25 00 00 07 00 01 00 00 00 00 00')
msg_cfg_port_uart_115200 = bytearray.fromhex('06 00 14 00 01 00 00 00 c0 08 00 00 00 c2 01 00 07 00 01 00 00 00 00 00')

msg_upd_sos_save = bytearray.fromhex('09 14 04 00 00 00 00 00')
msg_upd_sos_clear = bytearray.fromhex('09 14 04 00 01 00 00 00')

r = GnssUBlox('/dev/ttyS3')
r.setup()

"""
# Remove backup
m = UbxUpdSosAction()
m.f.cmd = UbxUpdSosAction.CLEAR
m.pack()
print(m)
print(m.f.cmd)
# quit()

r.expect(UbxAckAck.CID)
r.send(m)
r.wait()
"""

m = UbxMonVerPoll()
res = r.poll(m)
print(res)

for i in range(0, 1):
    print(f'***** {i} ***********************')

    logger.debug('getting SOS state')
    msg_upd_sos_poll = UbxUpdSosPoll()
    res = r.poll(msg_upd_sos_poll)
    print(res)
    if res:
        print(f'SOS state is {res.f.response}')

    msg_cfg_tp5_poll = UbxCfgTp5Poll()
    res = r.poll(msg_cfg_tp5_poll)
    print(res)

    res.f.flags |= 1
    # res.fields['flags'] = 1 + 2 + 16    # Active, lock to GPS, isLength
    res.f.freqPeriod = 1000     # 1 us = kHz
    res.f.pulseLenRatio = 500   # 500 ns = 50% duty cycle
    # print(res)
    res.pack()

    r.expect(UbxAckAck.CID)
    r.send(res)
    r.wait()

    time.sleep(0.87)

r.cleanup()
