import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
import os

from peaks.load_NIST import load_NIST_data
from scipy.signal import find_peaks
from aniplot import load_data, load_shot
from peaks.check import multimax, compare_peaks_with_nist


if __name__ == "__main__":

    path_spectrometer = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_shots = os.path.join(path_spectrometer, 'Shots')

    shot_number=["000100"]
    data_list = []
    for shot in shot_number:
        data = load_shot(shot, path_shots)
        data_list.append(data)
    
    # Get the maximum spectrum across all shots
    max_spectra = multimax(data_list)
    

    
    #Find peaks in the maximum spectrum
    shot_index = 0 # Change this to select a specific shot
    height_threshold = 0.005 * np.max(max_spectra['spectra'][shot_index])  # Adjust height threshold as needed
    print(f"Analyzing peaks for shot {shot_number[shot_index]}")
    peaks, _ = find_peaks(max_spectra['spectra'][shot_index], height=height_threshold)  # Adjust height threshold as needed
    peak_wavelengths = max_spectra['wave'][shot_index][peaks]
    peak_counts = max_spectra['spectra'][shot_index][peaks]
    print(f"Number of peaks found: {len(peaks)}")
    print(f"Peaks found at indices: {peaks}")
    print(f"Peak wavelengths: {peak_wavelengths}")
    print(f"Peak counts: {peak_counts}")
    
    # Compare the peak wavelengths with NIST data
    nist_file_path = os.path.join(path_spectrometer,'OOSpec_Control', 'peaks','ArNIST.txt')  # Adjust path as needed
    ebs_file_path = os.path.join(path_spectrometer, 'OOSpec_Control', 'peaks', 'ArEBS_Air.txt')  # Adjust path as needed

    nist_data = load_NIST_data(nist_file_path)
    ebs_data = load_NIST_data(ebs_file_path)
    nist_wavelengths = np.array(nist_data['Wavelength'])  # Convert from A to nm
    ebs_wavelengths = np.array(ebs_data['Wavelength']) # Convert from A to nm
    nist_species = np.array(nist_data['Species'])
    ebs_species = np.array(ebs_data['Species'])
    
    data = {
        'Wavelength': np.concatenate((nist_wavelengths, ebs_wavelengths)),
        'Species': np.concatenate((nist_species, ebs_species)),
        'Intensity': np.concatenate((nist_data['Intensity'], ebs_data['Intensity'])),
        'Ref': np.concatenate((nist_data['Ref'], ebs_data['Ref']))
    }
    
    # Compare peaks with NIST data
    data_spec = compare_peaks_with_nist(peaks, peak_wavelengths, peak_counts, data)
       
    # Plot the maximum spectrum
    fig_spec, ax_spec = plt.subplots()
    for i in range(len(shot_number)):
        # Plot each maximum spectrum
        ax_spec.plot(max_spectra['wave'][i], max_spectra['spectra'][i], 
                     lw=2, label=f'Shot {shot_number[i]}', color='green')
    
    # plot the peaks
    colors = {
        'Ar I': 'blue',
        'Ar II': 'red',
        'Ar III': 'orange',
        'Ar IV': 'purple',
    }
    tolerance = 1.2  # nm tolerance for peak matching
    for i, key in enumerate(colors.keys()):
        mask = data_spec[key]['delta'] < tolerance
        ax_spec.scatter(data_spec[key]['wave'][mask], 
                        data_spec[key]['counts'][mask], 
                        label=f'{key} Peaks', marker='x', 
                        color=colors[key], zorder=i+5,
                        s=50)
    ax_spec.legend()
    ax_spec.set_xlabel(r'$\lambda$ (nm)')
    ax_spec.set_ylabel('Counts')
    ax_spec.set_yscale('log')
    ax_spec.set_xlim(np.min(max_spectra['wave'][0]), np.max(max_spectra['wave'][0]))
    plt.show()
    
    fig_spec.savefig(os.path.join(path_shots, f'{shot_number[shot_index]}_max_spectrum.png'), dpi=300)
    
     
    
    
