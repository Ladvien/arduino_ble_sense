"""
    samples.subscribe_indicate_thermometer_sample
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is an example of subscribing to an indicate property of a
    characteristic. This example was tested with the Health Thermometer Profile,
    but can be easily modified to work with any other profile.
"""
import pygatt
from time import sleep

def data_handler_cb(handle, value):
    """
        Indication and notification come asynchronously, we use this function to
        handle them either one at the time as they come.
    :param handle:
    :param value:
    :return:
    """
    print("Data: {}".format(value.hex()))
    print("Handle: {}".format(handle))


def main():
    """
        Main function. The comments below try to explain what each section of
        the code does.
    """

    # pygatt uses pexpect and if your device has a long list of characteristics,
    # pexpect will not catch them all. We increase the search window to
    # 2048 bytes for the this example. By default, it is 200.
    # Note: We need an instance of GATToolBackend per each device connection
    adapter = pygatt.GATTToolBackend(search_window_size=2048)

    try:
        # Start the adapter
        adapter.start()
        # Connect to the device with that given parameter.
        # For scanning, use adapter.scan()
        try:
            device = adapter.connect('C8:5C:A2:2B:61:86', timeout = 20)
            # Set the security level to medium
            device.bond()
            # Observes the given characteristics for indications.
            # When a response is available, calls data_handle_cb

            chars = device.discover_characteristics(timeout = 20)
            print('here')
            for uuid in chars.keys():
                print("Read UUID %s: %s" % (uuid, binascii.hexlify(device.char_read(uuid))))
        except Exception as e:
            print(e)
        # device.subscribe("00002a1c-0000-1000-8000-00805f9b34fb",
        #                  callback=data_handler_cb,
        #                  indication=True)

        input("Press enter to stop program...\n")

    finally:
        # Stop the adapter session
        adapter.clear_bond('C8:5C:A2:2B:61:86')
        adapter.stop()
        sleep(2)

    return 0


if __name__ == '__main__':
    exit(main())
