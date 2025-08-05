from abc import ABC, abstractmethod
import abc
from typing import Literal

class  IDevice(ABC):     
    
    @property
    @abc.abstractmethod   
    def device_type(self) -> int:
        pass
    
    def set_device_type(self, value: int):
        pass
    
    def set_storage_path(self, path: str):
        pass
    
    def set_file_prefix(self, pre: str):
        pass
    
    def set_acq_param(self, channels, sample_rate = 500, sample_range = 188):
        pass
    
    @property
    def device_no(self) -> str:
        pass
    
    def produce(self, data, type:Literal['signal', 'impedance']="signal") -> None:
        pass
    
    def start_listening(self):
        pass
    
    def stop_listening(self):
        pass
    
    def set_device_no(self, value: str):
        pass
    
    def from_parent(cls, parent) :
        pass
        
    def start_implementation(self) -> None:
        pass
    
    def stop_implementation(self) -> None:
        pass
    
    def start_acquisition(self) -> None:
        pass
    
    def stop_acquisition(self) -> None:
        pass
    
    def subscribe(self, type="signal") -> None:
        pass
    
    def unsubscribe(self, topic) -> None:
        pass
    
    def start_stimulation(self, type="signal", duration=0) -> None:
        pass
    
    def stop_stimulation(self) -> None:
        pass
    
    def gen_set_acquirement_param(self) -> bytes:
        pass
        
    
    
class RscDevice(IDevice):
    def __init__(self, socket):
        super().__init__(socket)
        
    def start_implementation(self):
        """
        Start the device implementation
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def stop_implementation(self):
        """
        Stop the device implementation
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def start_acquisition(self):
        """
        Start data acquisition
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def stop_acquisition(self):
        """
        Stop data acquisition
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def subscribe(self, type="signal"):
        """
        Subscribe to data of a specific type (default is "signal")
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def unsubscribe(self, topic):
        """
        Unsubscribe from a specific topic
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def start_stimulation(self, type="signal", duration=0):
        """
        Start stimulation of a specific type (default is "signal") for a given duration
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def stop_stimulation(self):
        """
        Stop stimulation
        """
        raise NotImplementedError("This method should be overridden by subclasses")
        
class ProxyDevice(IDevice):
    def __init__(self, socket, proxy_socket):
        super().__init__(socket)
        self.proxy_socket = proxy_socket