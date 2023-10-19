####### types of sensors #######

# provide a list of sensors that are supported
# each sensor will have its own BLE config 
# config is currently global, on the sensor manager - can each sensor be configured separatly?

class SensorType:
    def __init__(self, sensor_type):
        self.config = {}
        self.data_rate = "60"
        self.payload_name = "CUSTOM_PAYLOAD_5"
        self.manufacturer_id = 2182

        for key in sensor_types:
            if key == sensor_type:
                self.config = sensor_types[key]
                self.manufacturer_id = self.config["manufacturer_id"]
    
    def set_data_rate(self, rate):
        self.data_rate = rate
    def get_data_rate(self):
        return self.data_rate
    def set_payload(self, payload):
        self.payload_name = payload
    def get_payload(self):
        return self.payload_name
    def get_sensor_config(self):
        return self.config
        
payload_sizes ={
    "short" : "15172004-4947-11e9-8646-d663bd873d93",
    "medium": "15172003-4947-11e9-8646-d663bd873d93",
    "long"  : "15172002-4947-11e9-8646-d663bd873d93"
}

sensor_types = {
    "Movella Dot":  {
        "manufacturer_id": 2182,
        "ble_config" : {
            "services": {
                "battery_service" : "15173001-4947-11e9-8646-d663bd873d93",
                "control_service"  : "15171002-4947-11e9-8646-d663bd873d93",
                "measurement_service"  : "15172001-4947-11e9-8646-d663bd873d93",
            },
            "characteristics": {
                "identify": b'\x01\x01\x02\n\x00\x1e\x00\tXsens DOT\x00\x00\x00\x00\x00\x00\x00<\x00\x00\x00\x00\x00\x00\x00',
                "start_measurement": b"\x01\x01\x1A",
                "stop_measurement": b"\x01\x00\x1A",
                "data_rates": {
                    "20": b'\x04\x00\x02\n\x00\x1e\x00\tXsens DOT\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00',
                    "60": b'\x04\x00\x02\n\x00\x1e\x00\tXsens DOT\x00\x00\x00\x00\x00\x00\x00\x3C\x00\x00\x00\x00\x00\x00'
                }
            },
            "payloads": {
                "CUSTOM_PAYLOAD_5":{
                    "csv_header" : ["timestamp", "q_w", "q_x", "q_y", "q_z", "acc_x", "acc_y", "acc_z", "gyr_x", "gyr_y", "gyr_z" ],
                    "payload_size": payload_sizes["long"] 

                }
            }
        }
    }




}