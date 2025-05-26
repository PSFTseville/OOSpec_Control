import os
import sys
import psutil
import time

# Add OceanDirect path
# sys.path.append('/usr/local/OceanOptics/OceanDirect/python')
sys.path.append('C:\Program Files\Ocean Optics\OceanDirect SDK\Python')

from oceandirect.OceanDirectAPI import *
import numpy as np


class OceanHR(OceanDirectAPI):

    def __init__(self, **kwargs):
        self.path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.path_shot = os.path.join(os.path.dirname(self.path), 'Shots')
        super().__init__()
        self.find_usb_devices()
        self.ids = self.get_device_ids()

        self.devs = []
        for id in self.ids:
            self.devs.append(self.open_device(id))
         
        self.reset_measurement()
        self._set_integration_time(**kwargs)
    
    def _set_integration_time(self, t_int: float=100000, **kwargs):
        self.integrantion_time = t_int
        for i, id in enumerate(self.ids):
            self.devs[i].set_integration_time(t_int)

    def reset_measurement(self):
        self.measurement = {}
        for i, id in enumerate(self.ids):
            self.measurement[id] = []

    def measure(self, num=10):
        self.t_array = []
        for j in range(num):
            for i, id in enumerate(self.ids):
                self.t_array.append(time.time())
                self.measurement[id].append(self.devs[i].get_formatted_spectrum())
        return self.measurement, self.t_array
    
