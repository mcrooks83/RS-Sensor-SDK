import asyncio
import time

from sensor_sdk import SensorManager as sm
from sensor_sdk import data_classes as dc

# example implmentation of the sensor sdk
# the sdk accepts messages
# the implementing client must be able to send messages to the sdk 

# message list

# scan
# connect
# disconnect
# start_measuring (single sensor)
# start_measuring_all
# stop_measuring_all
# stop_measuring (single sensor)
# indentify
# export
# configure (data rate / payload type)

#TODO: 
# add payload class and be able to config sensors
# sync multiple sensor
# connect to all scanned sensors
# start / stop measuring on all sensors
# configure sensor 

async def main():
    def on_sdk_init(done: bool):
        print(f"sdk init: {done}")

    def on_battery_status(address, batt_level):
        print(f"sensor {address} battery level {batt_level}%")

    def on_sensors_discovered(scanned_sensors: [dc.ScannedSensor]):
        print(f"Discovered sensors {scanned_sensors}")

        # connect to the first scanned sensor
        manager.send_message("connect", scanned_sensors[0].address)

    def on_sensor_connected(connected_sensor: dc.ConnectedSensor):
        print(f"Connected Sensor {connected_sensor.address}")
        
        # start measuring
        manager.send_message("start_measuring", connected_sensor.address)
        
    def on_sensor_diconnected(address: str):
        print(f"sensor {address} disconnected")

    def on_sensor_data(data_packet: dc.SensorDataPacket):
        print(f"data recieved: {data_packet.address} {data_packet.data_packet}")

    def on_message_error(error: dc.MessageError):
        print(f"message error: {error.error_message}")
    # create a sensor manager
    manager = sm.SensorManager()
    #initialise
    done = await manager.init_sdk()

    # callbacks that must be implemeted
    manager.on_sdk_init = on_sdk_init
    manager.on_sensors_discovered = on_sensors_discovered
    manager.on_sensor_connected = on_sensor_connected
    manager.on_sensor_disconnected = on_sensor_diconnected
    manager.on_battery_status = on_battery_status
    manager.on_sensor_data = on_sensor_data
    manager.on_message_error = on_message_error

    ## test the sdk
    if(done):
        manager.send_message("scan", {})
        done = False
        



# create a client event loop 
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())