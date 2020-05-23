import logging
import asyncio
import platform

from bleak import BleakClient
from bleak import _logger as logger

characteristics = [
    '00002101-0000-1000-8000-00805f9b34fb',
]

def notification_handler(sender, data):

    value = int.from_bytes(data, byteorder = 'big')

    print(f'{value}')

async def run(address, loop):
    async with BleakClient(address, loop = loop) as client:
        x = await client.is_connected()

        for characteristic in characteristics:
                await client.start_notify(characteristic, notification_handler)
                await asyncio.sleep(30.0, loop = loop)
                await client.stop_notify(characteristic)
                
if __name__ == "__main__":
    import os

    address = (
        "C8:5C:A2:2B:61:86"
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address, loop))