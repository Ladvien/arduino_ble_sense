# https://tutorialedge.net/python/concurrency/asyncio-event-loops-tutorial/
import os, sys
import asyncio
import platform
from datetime import datetime
from aioconsole import ainput

from bleak import BleakClient
# Get OS name.
os_name = sys.platform

if os_name.lower() != "windows":
    root_path = os.path.expanduser("~user")
else:
    root_path = os.environ['HOME']

#############
# Parameters
#############
output_file             = f'{root_path}/Desktop/microphone_dump.csv'

read_characteristic     = '00001143-0000-1000-8000-00805f9b34fb'
write_characteristic    = '00001142-0000-1000-8000-00805f9b34fb'

# Data
dump_size               = 256
column_names            = ['time', 'micro_secs_since_last', 'microphone_value']

#############
# Subroutines
#############

connected = False
last_packet_time = datetime.now()

def write_to_csv(path, microphone_values, timestamps):
    with open(path, 'a+') as f:
        if os.stat(path).st_size == 0:
            print('Created file.')
            f.write(','.join([str(name) for name in column_names]) + ',\n')  
        else:
            for i in range(len(microphone_values)):
                f.write(f'{timestamps[i]},{delays[i]},{microphone_values[i]},\n')


def notification_handler(sender, data):
    global last_packet_time
    value = int.from_bytes(data, byteorder = 'big')
    microphone_values.append(value)
    present_time = datetime.now()
    timestamps.append(present_time)
    delays.append((present_time - last_packet_time).microseconds)
    last_packet_time = present_time
    if len(microphone_values) >= dump_size:
        write_to_csv(output_file, microphone_values, timestamps)
        microphone_values.clear()
        delays.clear()
        timestamps.clear()


def disconnect_callback(client, future):
    global connected
    connected = False
    print(f"Disconnected callback called on {client}!")


async def cleanup(client):
    await client.stop_notify(read_characteristic)
    await client.disconnect()
    

async def user_write(client):
    global connected
    while True:
        if connected:
            input_str = await ainput('Enter string: ')
            bytes_to_send = bytearray(map(ord, input_str))
            await client.write_gatt_char(write_characteristic,  bytes_to_send)
            print(f'Sent: {input_str}')
        else:
            await asyncio.sleep(15.0, loop = loop)


async def run(client):
    global connected
    while True:
        if not connected:
            try:
                await client.connect()
                connected = await client.is_connected()
                client.set_disconnected_callback(disconnect_callback)
                await client.start_notify(read_characteristic, notification_handler)
                while True:
                    await asyncio.sleep(15.0, loop = loop)
            except Exception as e:
                print(e)



async def main():
    while True:
        await asyncio.sleep(5)


#############
# Main
#############        
microphone_values = []
timestamps = []
delays = []

if __name__ == "__main__":

    if os_name == 'darwin': # Mac uses CBUUID.
        address = ('C24E11AE-0009-4C5D-9938-6456CBD09A54')
    else:
        # Windows or Linux.
        address = ('E6:38:7B:5E:A9:24')
    
    # Create the event loop.
    loop = asyncio.get_event_loop()

    # Create the Bluetooth LE object.
    client = BleakClient(address, loop = loop)
    try:
        asyncio.ensure_future(run(client))
        asyncio.ensure_future(user_write(client))
        asyncio.ensure_future(main())
        loop.run_forever()
    except KeyboardInterrupt:
        print()
        print('User stopped program.')
    finally:
        print('Disconnecting...')
        loop.run_until_complete(cleanup(client))

