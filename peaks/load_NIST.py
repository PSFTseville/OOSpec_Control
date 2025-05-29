import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def load_NIST_data(file_path):
    """
    Load NIST data from a file in ASCII.
    
    Parameters:
    - file_path: Path to the NIST data file.
    
    Returns:
    - data: Dictionary containing 'wave', 'spectra', and 'time'.
    """
   
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # No header, so we can directly parse the data
    data = {
        'Intensity': [],
        'Wavelength': [],
        'Species': [],
        'Ref': []
    }
    
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) == 5:
                try:
                    data['Intensity'].append(float(parts[0]))
                except ValueError:
                    data['Intensity'].append(0.0)
                data['Wavelength'].append(float(parts[1]))
                data['Species'].append(parts[2] + ' ' + parts[3])
                data['Ref'].append(parts[4])
            elif len(parts) == 6:
                try:
                    data['Intensity'].append(float(parts[0]))
                except ValueError:
                    data['Intensity'].append(0.0)
                data['Wavelength'].append(float(parts[2]))
                data['Species'].append(parts[3] + ' ' + parts[4])
                data['Ref'].append(parts[5])
                
    return data
                

if __name__ == "__main__":
    # Example usage
    path_NIST = os.path.dirname(os.path.abspath(__file__))
    file_name = 'ArNIST.txt'  # Replace with your actual NIST data file name
    file_path = os.path.join(path_NIST, file_name)
    
    if os.path.exists(file_path):
        nist_data = load_NIST_data(file_path)
        print("NIST Data Loaded Successfully")
        print(nist_data)
    else:
        print(f"File {file_path} does not exist.")
    