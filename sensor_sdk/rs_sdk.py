### SDK interfac ###

from abc import ABC, abstractmethod
from sensor_sdk import data_classes as dc

# callbacks that are to be implmented by calling class
class RSSensorSDK(ABC):
    @abstractmethod
    def on_sdk_init(self,done: bool):
        pass
    
    @abstractmethod
    def on_sensors_discovered(self, scanned_sensors: [dc.ScannedSensor]):
        pass

    @abstractmethod
    def on_sensor_connected(self, connected_sensor: dc.ConnectedSensor):
        pass

    @abstractmethod
    def on_sensor_disconnected(self, address: str):
        pass

    @abstractmethod
    def on_battery_status(self, battery_status: dc.BatteryStatus):
        pass

    @abstractmethod
    def on_sensor_data(self, address, data: dc.SensorDataPacket ):
        pass

    @abstractmethod
    def on_message_error(self, error_message: dc.MessageError):
        pass
