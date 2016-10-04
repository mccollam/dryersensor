# dryersensor
Send status via MQTT about a clothes dryer from an Onion Omega with MPU-6050 sensor

This uses a modified version of an [MPU-6050 library](https://github.com/mccollam/mpu6050) based on the [original](https://github.com/Tijndagamer/mpu6050) by Martijn Tijndagamer.

Usage
-----
First, install the required packages by running ``setup.sh`` on the Onion Omega.

Issues
------
For now, this is calling out to the shell interface for Mosquitto.  It appears that OpenWRT libmosquitto packages are improperly built without Python support, and the Onion Omega does not have space to install pip and get it that way.  (There's probably a better way to fix this but using the mosquitto-client tools works for now.)
