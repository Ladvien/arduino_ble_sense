sudo apt-get update
sudo apt-get -y install libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev
cd ~
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.33.tar.gz
tar xvfz bluez-5.33.tar.gz
cd bluez-5.33
./configure --disable-systemd
make
sudo make install
sudo cp ./src/bluetoothd /usr/local/bin/