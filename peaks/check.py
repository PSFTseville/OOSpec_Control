import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
import os

from peaks.load_NIST import load_NIST_data
from scipy.signal import find_peaks
from plots.aniplot import load_data, load_shot

def multimax(data_list):
    """
    Find the maximum spectrum across multiple data sets.
    
    Parameters:
    - data_list: List of dictionaries containing 'wave', 'spectra', and 'time'.
    
    Returns:
    - max_spectrum: Maximum spectrum for each data sets.
    """
    max_spectrum = {
        'wave': [],
        'spectra': [],
        'time': []
    }
    for data in data_list:
        wavelengths = np.array(data['wave'])
        spectra = np.array(data['spectra']['2'])
        time_array = np.array(data['time'])

        # Normalize and align time
        spectra = spectra - spectra[0, :]
        spectra = np.clip(spectra, 0, None)
        time_array = time_array - time_array[0]
        

        # Update max_spectrum
        max_spectrum['wave'].append(wavelengths)
        max_spectrum['spectra'].append(np.amax(spectra, axis=0))
        # Get the time point for the maximum spectrum
        max_time_index = np.argmax(spectra, axis=0)
        max_spectrum['time'].append(time_array[max_time_index])
    return max_spectrum

def multisum(data_list):
    """
    Sum the spectra across multiple data sets.
    
    Parameters:
    - data_list: List of dictionaries containing 'wave', 'spectra', and 'time'.
    
    Returns:
    - summed_spectrum: Summed spectrum for each data sets.
    """
    summed_spectrum = {
        'wave': [],
        'spectra': [],
        'time': []
    }
    for data in data_list:
        wavelengths = np.array(data['wave'])
        spectra = np.array(data['spectra']['2'])
        time_array = np.array(data['time'])

        # Normalize and align time
        spectra = spectra - spectra[0, :]
        spectra = np.clip(spectra, 0, None)
        time_array = time_array - time_array[0]
        
        # Update summed_spectrum
        summed_spectrum['wave'].append(wavelengths)
        summed_spectrum['spectra'].append(np.sum(spectra, axis=0))
        # Get the time point for the summed spectrum
        summed_time_index = np.argmax(np.sum(spectra, axis=0))
        summed_spectrum['time'].append(time_array[summed_time_index])
        
    return summed_spectrum

def compare_peaks_with_nist(peaks, peak_wavelengths, peak_counts, nist_data,
                            tolerance=0.1, species=None):
    """
    Compare the detected peaks with NIST data.
    
    Parameters:
    - peaks: Indices of the detected peaks.
    - peak_wavelengths: Wavelengths of the detected peaks.
    - peak_counts: Counts of the detected peaks.
    - nist_data: Dictionary containing NIST data with 'Wavelength' and 'Species'.
    
    Returns:
    - data_spec: Dictionary containing species-specific peak information.
    """
    nist_wavelengths = np.array(nist_data['Wavelength']) * 1e-1  # Convert from cm to nm
    nist_species = np.array(nist_data['Species'])
    nist_intensities = np.array(nist_data['Intensity'])
    
    if species is None:
        species = ['Ar I', 'Ar II', 'Ar III', 'Ar IV', 'Ar V', 'Ar VI',
                'Ar VII', 'Ar VIII', 'Ar IX', 'Ar X', 'Ar XI', 'Ar XII',
                'Ar XIII', 'Ar XIV', 'Ar XV', 'Ar XVI', 'Ar XVII', 'Ar XVIII',
                'N I', 'N II', 'O I', 'O II', 'C I', 'C II', 'Fe I', 'Fe II',
                'He I', 'He II']
    
    # Check 
    data_spec = {spec: {
        'wave': [],
        'wave_mes': [],
        'counts': [],
        'delta': [],
        'intensity': [],
    } for spec in species}

    
    for i, peak in enumerate(peaks):
        peak_wl = peak_wavelengths[i]
        peak_count = peak_counts[i]
        
        # Find closest NIST wavelength
        closest_index = np.argmin(np.abs(nist_wavelengths - peak_wl))
        closest_wl = nist_wavelengths[closest_index]
        delta = np.abs(closest_wl - peak_wl)
        closest_species = nist_species[closest_index]
        closest_intensity = nist_intensities[closest_index]
        
        if isinstance(closest_species, np.str_):
            closest_species = closest_species.strip()
        
        if delta < tolerance:  # nm tolerance for peak matching
            print(f"Peak wavelength {peak_wl:.2f} nm is closest to NIST wavelength {closest_wl:.2f} nm ({closest_species})")
            
            data_spec[closest_species]['wave'].append(closest_wl)
            data_spec[closest_species]['wave_mes'].append(peak_wl)
            data_spec[closest_species]['counts'].append(peak_count)
            data_spec[closest_species]['delta'].append(peak_wl - closest_wl)
            data_spec[closest_species]['intensity'].append(closest_intensity)
    
        # Convert lists to numpy arrays for easier handling
    for key in data_spec:
        data_spec[key]['wave'] = np.array(data_spec[key]['wave'])
        data_spec[key]['wave_mes'] = np.array(data_spec[key]['wave_mes'])
        data_spec[key]['counts'] = np.array(data_spec[key]['counts'])
        data_spec[key]['delta'] = np.array(data_spec[key]['delta'])
        data_spec[key]['intensity'] = np.array(data_spec[key]['intensity'])
        

    
    return data_spec