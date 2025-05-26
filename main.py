import os
import sys
import psutil
import numpy as np
import time
import matplotlib.pyplot as plt
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.spec import OceanHR

# p = psutil.Process(os.getpid())
# p.cpu_affinity([0])
def manual_spec(num: int=10, t_int: float=7200, plot=False, **kwargs):


    # Load the class that detects the spectrometers and sets their integration time 
    OHR = OceanHR(t_int=t_int)

    
    # Measures spectra certain number of times
    t1 = time.time()
    measurement,t_array = OHR.measure(num) 
    t2 = time.time()
    print(f'Time to measure {num}: {(t2-t1)*1e3} ms')


    wavelengths = OHR.devs[0].get_wavelengths()
    if plot:
        fig, ax = plt.subplots()
        for i in range(num):
            plt.plot(wavelengths, measurement[2][i])
        ax.set_xlabel(r'$\lambda$ (nm)')
        ax.set_ylabel('Counts')
    
    data = {
        'wave': wavelengths,
        'spectra': measurement,
        'time': t_array,
    }
    return data

if __name__=="__main__":
    path_spectrometer = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_shots = os.path.join(path_spectrometer, 'shots')

    arguments = {}
    match len(sys.argv):
        case 1:
            raise Exception("Shot number is necessary")
        case 2:
            arguments['shot_number'] = sys.argv[1]
        case 3:
            arguments['shot_number'] = sys.argv[1]
            arguments['num'] = int(sys.argv[2])
        case 4:
            arguments['shot_number'] = sys.argv[1]
            arguments['num'] = int(sys.argv[2])
            arguments['t_int'] = int(sys.argv[3])
    
    data = manual_spec(**arguments)
    filename = os.path.join(path_shots, f'{arguments["shot_number"]}.json')
    print(f'Saving in {filename}...')

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)







