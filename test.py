import os
import sys
import psutil

# Add OceanDirect path
# sys.path.append('/usr/local/OceanOptics/OceanDirect/python')
sys.path.append('C:\Program Files\Ocean Optics\OceanDirect SDK\Python')

from oceandirect.OceanDirectAPI import *
import numpy as np

# p = psutil.Process(os.getpid())
# p.cpu_affinity([0])


oos = OceanDirectAPI()
oos.find_usb_devices()
ids = oos.get_device_ids()

dev = oos.open_device(ids[0])
