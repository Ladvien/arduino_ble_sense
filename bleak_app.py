import logging
import asyncio
import platform
from datetime import datetime


from bleak import BleakClient
from bleak import _logger as logger

#############
# Parameters
#############

output_file             = '/home/ladvien/Desktop/microphone_dump.csv'

read_characteristic     = '00001143-0000-1000-8000-00805f9b34fb'
write_characteristic    = '00001142-0000-1000-8000-00805f9b34fb'

# Data
dump_size               = 256
column_names            = ['time', 'microphone_value']

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
        print('Dumped data...')
        microphone_values.clear()
        timestamps.clear()

def disconnect_callback(client, future):
    print(f"Disconnected callback called on {client}!")

async def run(address, loop):
    async with BleakClient(address, loop = loop) as client:
        x = await client.is_connected()

        client.set_disconnected_callback(disconnect_callback)
        await client.write_gatt_char(write_characteristic, bytearray([2, 2, 3, 4]))
        await client.start_notify(read_characteristic, notification_handler)
        await asyncio.sleep(30.0, loop = loop)
        await client.stop_notify(read_characteristic)

#############
# Main
#############        
microphone_values = []
timestamps = []

if __name__ == "__main__":
    import os

    address = (
        "C8:5C:A2:2B:61:86"
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address, loop))
