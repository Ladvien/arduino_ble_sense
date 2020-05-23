# -*- coding: utf-8 -*-
"""
Notifications
-------------
Example showing how to add notifications to a characteristic and handle the responses.
Updated on 2019-07-03 by hbldh <henrik.blidh@gmail.com>
"""

import logging
import asyncio
import platform

from bleak import BleakClient
from bleak import _logger as logger

characteristics = [
    '00002101-0000-1000-8000-00805f9b34fb',
]

def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    print("{0}: {1}".format(sender, data))


async def run(address, loop, debug=False):
    if debug:
        import sys

        loop.set_debug(True)
        l = logging.getLogger("asyncio")
        l.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        l.addHandler(h)
        logger.addHandler(h)

    async with BleakClient(address, loop = loop) as client:
        x = await client.is_connected()
        logger.info("Connected: {0}".format(x))

        for CHARACTERISTIC_UUID in characteristics:
            try:
                await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
                await asyncio.sleep(30.0, loop = loop)
                await client.stop_notify(CHARACTERISTIC_UUID)
            except:
                pass

if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    address = (
        "C8:5C:A2:2B:61:86"
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address, loop, True))


# [NEW] Primary Service (Handle 0x778d)
#         /org/bluez/hci0/dev_C8_5C_A2_2B_61_86/service0006
#         00001801-0000-1000-8000-00805f9b34fb
#         Generic Attribute Profile
# [NEW] Characteristic (Handle 0x778d)
#         /org/bluez/hci0/dev_C8_5C_A2_2B_61_86/service0006/char0007
#         00002a05-0000-1000-8000-00805f9b34fb
#         Service Changed
# [NEW] Descriptor (Handle 0xae30)
#         /org/bluez/hci0/dev_C8_5C_A2_2B_61_86/service0006/char0007/desc0009
#         00002902-0000-1000-8000-00805f9b34fb
#         Client Characteristic Configuration
# [NEW] Primary Service (Handle 0x778d)
#         /org/bluez/hci0/dev_C8_5C_A2_2B_61_86/service000a
#         00001101-0000-1000-8000-00805f9b34fb
#         Serial Port
# [NEW] Characteristic (Handle 0x7df0)
#         /org/bluez/hci0/dev_C8_5C_A2_2B_61_86/service000a/char000b
#         00002101-0000-1000-8000-00805f9b34fb
#         Unknown
# [NEW] Descriptor (Handle 0xae30)
#         /org/bluez/hci0/dev_C8_5C_A2_2B_61_86/service000a/char000b/desc000d
#         00002902-0000-1000-8000-00805f9b34fb