
import asyncio
import time
import threading
from sensor_sdk import helper_functions as hf
from sensor_sdk import data_classes as dc
from sensor_sdk import sensor_functions as sf
from sensor_sdk import sensor_config as sc
from sensor_sdk.rs_sdk import RSSensorSDK as SDK


####################################################################
## Sensor Manager
####################################################################
class SensorManager(SDK):

    def __init__(self):
        # sensor manager data
        self.scanned_sensors = []
        self.connected_sensors = []
        self.running = False
        self.export_dir = "export"

        # Create a thread to run the SensorManager
        thread = threading.Thread(target=self.run_manager_loop)
        thread.start()

    def run_manager_loop(self):
        print("run manager loop")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.message_queue = asyncio.Queue()
        self.loop.run_until_complete(self.manager_loop())
        
    
    def send_message(self, msg, address):
        print(f"Received message from client: {msg} from {address}")
        self.loop.call_soon_threadsafe(self.message_queue.put_nowait, {"message": msg, "address": address,})
       
    async def init_sdk(self, sensor_type):
        # send in the sensor type (default is Movella Dot)
        # create a sensor type class from the sensor_config
        # dont create the SensorType here / or create a high level sensor type and a sensor config for each connected sensor
        print("initialising sensor sdk ...")
        self.sensor_type = sc.SensorType(sensor_type)

        time.sleep(1)
        return True
    
    # callbacks
    def on_sensors_discovered(self, sensors):
        return super().on_sensors_discovered(sensors)

    def on_sdk_init(self, done):
        return super().on_sdk_init(done)
    
    def on_sensor_connected(self, sensor: dc.ConnectedSensor):
        return super().on_sensor_connected(sensor)
    
    def on_sensor_disconnected(self, address:str):
        return super().on_sensor_disconnected(address)
    
    def on_battery_status(self, address: str, battery_status: dc.BatteryStatus):
        return super().on_battery_status(address, battery_status)
    
    def on_sensor_data(self, address, data: dc.SensorDataPacket):
        return super().on_sensor_data(address, data)
    
    def on_message_error(self, message_error: dc.MessageError):
        return super().on_message_error(message_error)
    
    # sensor config access methods
    def set_data_rate(self, rate):
        self.sensor_type.set_data_rate(str(rate))
    
    def get_data_rate(self):
        return int(self.sensor_type.get_data_rate())
    
    def set_payload(self, payload):
        self.sensor_type.set_payload(payload)

    def get_payload(self):
        return self.sensor_type.get_payload()
    
    def get_sensor_type_config(self):
        return self.sensor_type.get_sensor_config()
    


    # class methods
    def add_scanned_sensors(self, s):
        self.scanned_sensors = s

    def get_scanned_sensors(self):
        return self.scanned_sensors

    def remove_all_scanned_sensors(self):
        self.scanned_sensors = []   

    def add_connected_sensor(self, s):
        self.connected_sensors.append(s) 

    def remove_all_connected_sensors(self):
        self.connected_sensors = []

    def remove_single_connected_sensor(self, address):
        connected_sensors = list(filter(lambda x: x.address != address, self.connected_sensors))
        self.connected_sensors = connected_sensors 


    
    # sdk event loop
    async def manager_loop(self):
        self.running = True
        self.on_sdk_init(True)
        while self.running:
            msg = await self.message_queue.get()
            #Scanning for sensors
            if msg["message"] == "scan":
                scanned_sensors = await sf.discover_sensors(self)  
                self.add_scanned_sensors(scanned_sensors)
                self.on_sensors_discovered(self.scanned_sensors) 

            #connecting to a sensor
            elif msg["message"] == "connect":
                connected_sensor = await sf.connect_to_sensor(self, msg["address"])
                if(connected_sensor):
                    self.on_sensor_connected(connected_sensor)

            # disconnect a sensor
            elif msg["message"] == "disconnect":
                disconnected = await sf.disconnect_from_sensor(self, msg["address"])
                if(disconnected):
                    self.remove_single_connected_sensor(msg["address"])
                    self.on_sensor_disconnected(msg["address"])

            # start measuring
            elif(msg["message"] == "start_measuring"):
                await sf.start_measuring(self, msg["address"])    

            elif(msg["message"] == "start_measuring_all"):
                pass
            # stop measuring
            elif(msg["message"] == "stop_measuring"):
                print("stop measuring", flush=True)
                await sf.stop_measuring(self, msg["address"])

            elif(msg["message"] == "stop_measuring_all"):
                pass
                
            # identify a sensor
            elif(msg["message"] == "identify"):
                await sf.indentify_sensor(self, msg["address"])

            # export 
            elif(msg["message"] == "export"):
                await sf.export_to_csv(self, msg["address"])
                
            elif msg["message"] == "quit":
                self.running = False

            else:
                # send error message
                error = dc.MessageError("no such message")
                self.on_message_error(error)


   



    



