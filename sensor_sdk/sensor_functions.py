from bleak import BleakClient
from sensor_sdk import helper_functions as hf
from sensor_sdk import data_classes as dc
from datetime import datetime

async def discover_sensors(sensor_manager):
    sensor_manager.remove_all_scanned_sensors()
    sensors = await hf.discover_sensors()
    scanned_sensors = []
    if(sensors):
        for s, a in sensors.values():
            if( len(list(a.manufacturer_data.keys())) != 0 and list(a.manufacturer_data.keys())[0] == sensor_manager.sensor_type.manufacturer_id):
                mac_address = hf.get_mac_address(a.manufacturer_data[sensor_manager.sensor_type.manufacturer_id].hex())
                scanned_sensor = dc.ScannedSensor(mac_address, s.address, s)
                scanned_sensors.append(scanned_sensor)
    return scanned_sensors

async def connect_to_sensor(sensor_manager, address):
    #find device in scanned sensors 
    sensor = list(filter(lambda x: x.address == address, sensor_manager.scanned_sensors))[0]
    device = BleakClient(sensor.ble_device, loop=sensor_manager.loop)
    await device.connect()

    connected_sensor = dc.ConnectedSensor(sensor.address, device, sensor.ble_device, sensor_manager)
    sensor_manager.connected_sensors.append(connected_sensor)

    payload = sensor_manager.sensor_type.config["ble_config"]["payloads"][sensor_manager.sensor_type.payload_name]
    await device.start_notify(payload["payload_size"], connected_sensor.on_sensor_data )

    #read initial battery
    battery_service = sensor_manager.sensor_type.config["ble_config"]["services"]["battery_service"]
    batt = await device.read_gatt_char(battery_service, response=True)
    connected_sensor.on_battery_status_update(connected_sensor.address, batt)
    await device.start_notify(battery_service, connected_sensor.on_battery_status_update)

    return connected_sensor

async def disconnect_from_sensor(sensor_manager, address):
    sensor = list(filter(lambda x: x.address == address, sensor_manager.connected_sensors))[0]
    disconnected = await sensor.ble_client.disconnect()
    return disconnected

async def start_measuring(sensor_manager, address):
    sensor = list(filter(lambda x: x.address == address, sensor_manager.connected_sensors))[0]
    print("Sensor", sensor)
    if(sensor):    
        start_char = sensor_manager.sensor_type.config["ble_config"]["characteristics"]["start_measurement"]
        measurement_service = sensor_manager.sensor_type.config['ble_config']["services"]["measurement_service"]
        await sensor.ble_client.write_gatt_char(measurement_service, start_char, response=True)

async def start_measuring_on_all_sensors(sensor_manager):
    pass

async def stop_measuring(sensor_manager, address):
    sensor = list(filter(lambda x: x.address == address, sensor_manager.connected_sensors))[0]
    stop_char = sensor_manager.sensor_type.config["ble_config"]["characteristics"]["stop_measurement"]
    measurement_service = sensor_manager.sensor_type.config['ble_config']["services"]["measurement_service"]
    await sensor.ble_client.write_gatt_char(measurement_service, stop_char, response=True)
    sensor_manager.stop_sensor_callback(sensor.address)

async def indentify_sensor(sensor_manager, address):
    sensor = list(filter(lambda x: x.address == address, sensor_manager.connected_sensors))[0]
    control_service = sensor_manager.sensor_type.config["ble_config"]["services"]["control_service"]
    indentify_char = sensor_manager.sensor_type.config['ble_config']["characteristics"]["identify"]
    await sensor.ble_client.write_gatt_char(control_service, indentify_char, response=True)
    
async def export_to_csv(sensor_manager, address):
    # should export all active sensors.  currently there is only one so use the address to find it.
    sensor = list(filter(lambda x: x.address == address, sensor_manager.connected_sensors))[0]
    data_to_write_to_csv = sensor.get_raw_data()

    now = int(datetime.timestamp(datetime.now()) * 1000)
    csv_file_name = f"{now}_{address}.csv"
    row_headers = sensor_manager.sensor_type.config["payloads"][sensor_manager.sensor_type.payload_name]["csv_header"]

    hf.check_and_create_export_diretort(sensor_manager.export_dir)

    done = hf.write_data_to_csv(sensor_manager.export_dir, csv_file_name, row_headers, data_to_write_to_csv)
    
    if(done):
        # remove raw data
        sensor.remove_raw_data()
        sensor_manager.export_to_csv_done_callback(sensor.address)

    