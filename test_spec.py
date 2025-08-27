import os
import sys
import psutil
import numpy as np
import time
import matplotlib.pyplot as plt
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.com.spec import OceanHR

if __name__=="__main__":
    OHR = OceanHR(t_int=7200)
    print(f'Next shot: {OHR.check_last_shot()+1:06d}')
