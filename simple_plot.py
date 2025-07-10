import os
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf

from scipy.stats import norm
from scipy.optimize import curve_fit
from plots.aniplot import load_shot
import scipy.constants as cons

def gaussian(x, a, mu, sigma):
    return a * np.exp(-(x - mu)**2 / (2 * sigma**2))

def broadening(spectrum, wavelengths, w_ini, w_end, M):
        # Find the indices for the wavelength range
        indices = np.where((wavelengths >= w_ini) & (wavelengths <= w_end))[0]
        spectra_range = spectrum[indices]
        
        # Locate maximum
        index_max = np.argmax(spectra_range)
        print(index_max)
        wave_range = wavelengths[indices]
        wave_array = np.linspace(w_ini, w_end, 1000)
        
        # Adjust to gaussian 
        popt, pconv = curve_fit(gaussian, wave_range, spectra_range, p0=[1, wave_range[index_max], 1])
        
        fitted_spectrum = gaussian(wave_array, *popt)
        
        # Plot the fitted spectrum
        fig, ax = plt.subplots()
        ax.plot(wave_range, spectra_range, label='Data', color='blue')
        ax.plot(wave_array, fitted_spectrum, label='Fitted Gaussian', color='red')
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Counts')
        ax.set_title(f'Shot {shot} - Gaussian Fit')
        ax.legend()
        plt.show()
        FWHM = 2*(2 * np.log(2))**(1/2) * popt[2]
        T_e = (FWHM / popt[1])**2 * M / (8 * np.log(2))
        data = {
            'a': popt[0],
            'mu': popt[1],
            'sigma': popt[2],
            'FWHM': FWHM,
            'T_e': T_e,
            'error': pconv,
        }
        return data
    

if __name__ == "__main__":
    # Example usage of the code
    print("This script is designed to load and process spectra data for sound generation.")
    print("Please ensure you have the necessary data files available.")
    shots = ['000100']
    # Define the path to the shots directory
    path_current = os.path.dirname(os.path.abspath(__file__))
    path_shots = os.path.join(os.path.dirname(path_current), 'Shots')

    m_He = 6.6464731*1e-27 * cons.c ** 2 / cons.eV
    m_He_uma = 4.002602
    m_Ar = 6.6335209*1e-26 * cons.c ** 2 / cons.eV
    
    w_ini = 805
    w_end = 820
    data_list = {}
    for shot in shots:
        data = load_shot(shot, path_shots)
        # Remove the background noise
        spectra = np.array(data['spectra']['2'])
        spectra = spectra - spectra[0, :]  # Subtract the first frame as background noise
        spectra = np.clip(spectra, 0, None)  # Ensure no negative values
        
        wavelengths = np.array(data['wave'])  # Assuming the wavelength data is the same for all shots
        
        
        data_broad = broadening(np.amax(spectra, axis=0), wavelengths, w_ini, w_end, m_Ar)
        
        data_list[shot] = {
            'spectra': spectra,
            'wavelengths': wavelengths,
            'w_ini': w_ini,
            'W_end': w_end,
            **data_broad
        }
        print(f"Processed shot {shot} successfully.")
    
    wavelengths = np.array(data['wave'])  # Assuming the wavelength data is the same for all shots

    fig_spec, ax_spec = plt.subplots()
    ax_spec.plot(data_list['000100']['wavelengths'], np.amax(data_list['000100']['spectra'], axis=0))
    ax_spec.set_xlabel('Wavelength (nm)')
    ax_spec.set_ylabel('Counts')
    # ax_spec.set_xlim(850, 950)