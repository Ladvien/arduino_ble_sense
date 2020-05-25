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

async def cleanup(client):
    await client.stop_notify(read_characteristic)
    await client.disconnect()


async def run(client):
    await client.connect()
    await client.is_connected()
    client.set_disconnected_callback(disconnect_callback)
    await client.start_notify(read_characteristic, notification_handler)
    while True:
        await asyncio.sleep(15.0, loop = loop)

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
    
    # Create the event loop.
    loop = asyncio.get_event_loop()
    
    # Create the Bluetooth LE object.
    client = BleakClient(address, loop = loop)
    try:
        loop.run_until_complete(run(client))
    except KeyboardInterrupt:
        print()
        print('User stopped program.')
    finally:
        print('Disconnecting...')
        loop.run_until_complete(cleanup(client))
