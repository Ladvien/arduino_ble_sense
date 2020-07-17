# https://tutorialedge.net/python/concurrency/asyncio-event-loops-tutorial/
import os, sys
import asyncio
import platform
from datetime import datetime

from aioconsole import ainput
from bleak import BleakClient

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


if __name__ == "__main__":

    if sys.platform == 'darwin': # Mac uses CBID.
        address = ('46BFEB38-910C-4490-962E-CD60E52D7AF1')
    else:
        address = ('C8:5C:A2:2B:61:86')
    
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
