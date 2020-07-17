# https://tutorialedge.net/python/concurrency/asyncio-event-loops-tutorial/
import os, sys
import asyncio
import platform
from datetime import datetime

from aioconsole import ainput
from bleak import BleakClient

from typing import Callable, Any

root_path = os.environ["HOME"]
output_file = f"{root_path}/Desktop/microphone_dump.csv"
column_names = ["time", "micro_secs_since_last", "microphone_value"]


class DataToFile:
    def __init__(self):
        pass

    def write_to_csv(self, path: str, microphone_values: list, timestamps: list):
        with open(path, "a+") as f:
            if os.stat(path).st_size == 0:
                print("Created file.")
                f.write(",".join([str(name) for name in column_names]) + ",\n")
            else:
                for i in range(len(microphone_values)):
                    f.write(f"{timestamps[i]},{delays[i]},{microphone_values[i]},\n")


class Connection:
    def __init__(
        self,
        client: BleakClient,
        read_characteristic: str,
        write_characteristic: str,
        notification_handler: Callable[[str, Any], None],
        data_dump_size: int = 256,
    ):
        self.client = client
        self.read_characteristic = read_characteristic
        self.write_characteristic = write_characteristic
        self.notification_handler = notification_handler

        self.data_to_file = DataToFile()
        self.last_packet_time = datetime.now()
        self.dump_size = data_dump_size
        self.connected = False

    def disconnect_callback(self, client, future):
        global connected
        connected = False
        print(f"Disconnected callback called on {client}!")

    async def cleanup(self):
        await self.client.stop_notify(read_characteristic)
        await self.client.disconnect()

    async def manager(self, client: BleakClient):
        while True:
            if not await client.is_connected():
                try:
                    client.set_disconnected_callback(self.disconnect_callback)
                    await client.start_notify(
                        self.read_characteristic, self.notification_handler
                    )
                    while True:
                        await asyncio.sleep(15.0, loop=loop)
                except Exception as e:
                    print(e)


def record_time_info(timestamps: list, delays: list):
    global last_packet_time
    present_time = datetime.now()
    timestamps.append(present_time)
    delays.append((present_time - last_packet_time).microseconds)
    last_packet_time = present_time

def clear_lists(microphone_values: list, timestamps: list, delays: list):
    microphone_values.clear()
    delays.clear()
    timestamps.clear()

def notification_handler(sender: str, data: Any):
    # Convert from byte to int.
    microphone_values.append(int.from_bytes(data, byteorder="big"))
    record_time_info()
    if len(microphone_values) >= dump_size:
        write_to_csv(output_file, microphone_values, timestamps)
        clear_lists(microphone_values, timestamps, delays)


async def user_console(client: BleakClient, connection: Connection):
    while True:
        if await client.is_connected():
            input_str = await ainput("Enter string: ")
            bytes_to_send = bytearray(map(ord, input_str))
            await client.write_gatt_char(write_characteristic, bytes_to_send)
            print(f"Sent: {input_str}")
        else:
            await asyncio.sleep(15.0, loop=loop)


async def main():
    while True:
        # YOUR CODE WOULD GO HERE.
        await asyncio.sleep(5)


#############
# Main
#############
read_characteristic = "00001143-0000-1000-8000-00805f9b34fb"
write_characteristic = "00001142-0000-1000-8000-00805f9b34fb"

if __name__ == "__main__":

    # Get OS name.
    os_name = sys.platform

    if os_name == "darwin":  # Mac uses CBID.
        address = "46BFEB38-910C-4490-962E-CD60E52D7AF1"
    else:
        address = "C8:5C:A2:2B:61:86"

    # Create the event loop.
    loop = asyncio.get_event_loop()

    # Create the Bluetooth LE object.
    client = BleakClient(address, loop=loop)
    connection = Connection(
        client, read_characteristic, write_characteristic, notification_handler
    )
    try:
        asyncio.ensure_future(connection.manager(client))
        # asyncio.ensure_future(user_console(client, connection))
        # asyncio.ensure_future(main())
        loop.run_forever()
    except KeyboardInterrupt:
        print()
        print("User stopped program.")
    # finally:
    #     print("Disconnecting...")
    #     loop.run_until_complete(connection.cleanup())
