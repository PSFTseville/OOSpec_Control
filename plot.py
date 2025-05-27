import numpy as np
import matplotlib.pyplot as plt
import json
import os


def plot_spectra(data, shot_number=None, save_path=None):
    """
    Plot the spectra data.

    Parameters:
    - data: Dictionary containing 'wave', 'spectra', and 'time'.
    - shot_number: Optional shot number for labeling.
    - save_path: Optional path to save the plot.
    """
    wavelengths = data['wave']
    spectra = data['spectra']
    t_array = data['time']
    
    fig, ax = plt.subplots()
    for i, spectrum in enumerate(spectra):
        ax.plot(wavelengths, spectrum, label=f'Spectrum t={t_array[i]} ms')
    
    ax.set_xlabel(r'$\lambda$ (nm)')
    ax.set_ylabel('Counts')
    
    if shot_number is not None:
        ax.set_title(f'Shot Number: {shot_number}')
    
    if save_path:
        plt.savefig(save_path)
        print(f"Plot saved to {save_path}")
    
    plt.show()
    

def load_data(file_path):
    """
    Load the spectra data from a JSON file.

    Parameters:
    - file_path: Path to the JSON file containing the spectra data.

    Returns:
    - data: Dictionary containing 'wave', 'spectra', and 'time'.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    # Example usage
    path_spectrometer = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_shots = os.path.join(path_spectrometer, 'Shots')
    
    shot_number = '000098'
    file_path = os.path.join(path_shots, f'{shot_number}.json')
    
    data = load_data(file_path)
    
    plot_spectra(data, shot_number=shot_number, save_path=os.path.join(path_shots, f'{shot_number}_plot.png'))