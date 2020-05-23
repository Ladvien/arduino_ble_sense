import logging
import asyncio
import platform
from datetime import datetime


from bleak import BleakClient
from bleak import _logger as logger

#############
# Parameters
#############

output_file         = '/home/ladvien/Desktop/microphone_dump.csv'

characteristics = [
    '00002101-0000-1000-8000-00805f9b34fb',
]

# Data
dump_size           = 256
column_names        = ['time', 'microphone_value']
microphone_values   = []
timestamps         = []

#############
# Subroutines
#############
def write_to_csv(path, microphone_values, timestamps):
    with open(path, 'a+') as f:
        if os.stat(path).st_size == 0:
            print('Created file.')
            f.write(','.join([str(name) for name in column_names]) + ',\n')  
        else:
            for i in range(len(microphone_values)):
                f.write(f'{timestamps[i]},{microphone_values[i]},\n')

def notification_handler(sender, data):
    value = int.from_bytes(data, byteorder = 'big')
    microphone_values.append(value)
    timestamps.append(datetime.now())

    if len(microphone_values) >= dump_size:
        write_to_csv(output_file, microphone_values, timestamps)

async def run(address, loop):
    async with BleakClient(address, loop = loop) as client:
        x = await client.is_connected()

        for characteristic in characteristics:
                await client.start_notify(characteristic, notification_handler)
                await asyncio.sleep(30.0, loop = loop)
                await client.stop_notify(characteristic)

#############
# Main
#############        
if __name__ == "__main__":
    import os

    address = (
        "C8:5C:A2:2B:61:86"
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address, loop))
    print(microphone_values)