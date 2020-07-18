# https://tutorialedge.net/python/concurrency/asyncio-event-loops-tutorial/
import os, sys
import asyncio
import platform
from datetime import datetime

from aioconsole import ainput
from bleak import BleakClient
import pandas as pd
from typing import Callable, Any

root_path = os.environ["HOME"]
output_file = f"{root_path}/Desktop/microphone_dump.csv"
column_names = ["time", "micro_secs_since_last", "microphone_value"]


class DataToFile:
    def __init__(self, write_path, column_names):
        self.path = write_path
        self.column_names = column_names

    def write_to_csv(self, data: tuple):
        prev_leng = 0
        for column in data:
            if len(column) != prev_leng and prev_leng != 0:
                raise Exception("Not all columns are the same length.")
            prev_leng = len(column)

        with open(self.path, "a+") as f:
            if os.stat(self.path).st_size == 0:
                print("Created file.")
                f.write(",".join([str(name) for name in self.column_names]) + ",\n")
            else:
                for row_idx in range(len(data[0])):
                    row = ""
                    for col_idx in range(len(data)):
                        row += f"{data[col_idx][row_idx]},"
                    row += "\n"
                    f.write(row)
                        # f.write(f"{timestamps[i]},{delays[i]},{data[i]},\n")
class Connection:
    def __init__(
        self,
        client: BleakClient,
        read_characteristic: str,
        write_characteristic: str,
        data_dump_handler: Callable[[str, Any], None],
        data_dump_size: int = 256,
    ):
        self.client = client
        self.read_characteristic = read_characteristic
        self.write_characteristic = write_characteristic
        self.data_dump_handler = data_dump_handler

        self.last_packet_time = datetime.now()
        self.dump_size = data_dump_size
        self.connected = False

        self.rx_data = []
        self.rx_timestamps = []
        self.rx_delays = []

    def disconnect_callback(self, client):
        self.connected = False
        print(f"Disconnected from {client}!")

    async def cleanup(self):
        await self.client.stop_notify(read_characteristic)
        await self.client.disconnect()

    async def manager(self, client: BleakClient):
        while True:
            if not self.connected:
                try:
                    await client.connect()
                    self.connected = await client.is_connected()
                    client.set_disconnected_callback(self.disconnect_callback)
                    await client.start_notify(
                        self.read_characteristic, self.notification_handler,
                    )
                    while True:
                        await asyncio.sleep(15.0, loop=loop)
                except Exception as e:
                    print(e)

    def record_time_info(self):
        present_time = datetime.now()
        self.rx_timestamps.append(present_time)
        self.rx_delays.append((present_time - self.last_packet_time).microseconds)
        self.last_packet_time = present_time

    def clear_lists(self):
        self.rx_data.clear()
        self.rx_delays.clear()
        self.rx_timestamps.clear()

    def notification_handler(self, sender: str, data: Any):
        self.rx_data.append(int.from_bytes(data, byteorder="big"))
        self.record_time_info()
        if len(self.rx_data) >= self.dump_size:
            data = (self.rx_data, self.rx_timestamps, self.rx_delays)
            self.data_dump_handler(data)
            self.clear_lists()


#############
# Loops
#############
async def user_console(client: BleakClient, connection: Connection):
    while True:
        if connection.connected:
            input_str = await ainput("Enter string: ")
            bytes_to_send = bytearray(map(ord, input_str))
            await client.write_gatt_char(write_characteristic, bytes_to_send)
            print(f"Sent: {input_str}")
        else:
            await asyncio.sleep(2.0, loop=loop)


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

    if sys.platform == "darwin":
        # Mac.
        address = "46BFEB38-910C-4490-962E-CD60E52D7AF1"
    else:
        # Windows or Linux.
        address = "E6:38:7B:5E:A9:24"

    # Create the event loop.
    loop = asyncio.get_event_loop()
    data_to_file = DataToFile(output_file, column_names)
    # Create the Bluetooth LE object.
    client = BleakClient(address, loop=loop)
    connection = Connection(
        client, read_characteristic, write_characteristic, data_to_file.write_to_csv
    )
    try:
        asyncio.ensure_future(connection.manager(client))
        asyncio.ensure_future(user_console(client, connection))
        asyncio.ensure_future(main())
        loop.run_forever()
    except KeyboardInterrupt:
        print()
        print("User stopped program.")
    finally:
        print("Disconnecting...")
        loop.run_until_complete(connection.cleanup())
