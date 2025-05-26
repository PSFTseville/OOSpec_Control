# import socket
import os  # To run shell commands (optional)
# from com.turbo import Turbo
# import time
import json



def decompose_command(command):
    command = command.strip()
    command = command.split(':')
    order = command[-1].split(' ')
    # delete last command
    del command[-1]
    command = command + order
    return command

def execute_command(command, OceanHR):
    match command[0]:
        case 'PREP':
            OceanHR.reset_measurement()
            if len(command)>1:
                OceanHR._set_integration_time(int(command[1]))
            return None
        case 'TRIG':
            if len(command)>1:
                return OceanHR.measure(int(command[1]))
            else:
                return OceanHR.measure()
        case 'SAVE':
            if len(command)>1:
                    filename = os.path.join(OceanHR.path_shot, f'{command[1]}.json')
                    data = {
                        'wave': OceanHR.devs[0].get_wavelengths(),
                        'spectra': OceanHR.measurement,
                        'time': OceanHR.t_array,
                    }
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=4)
                
        case _:
            print('Invalid command')
            return None




if __name__ == '__main__':
    # Set up socket server
    command = 'TURB:POW'
    command = decompose_command(command)
    print(command)