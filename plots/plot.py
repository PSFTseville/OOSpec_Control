import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
import os
from scipy.stats import linregress
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from peaks.load_NIST import load_NIST_data
from scipy.signal import find_peaks
from plots.aniplot import load_data, load_shot
from peaks.check import multimax, compare_peaks_with_nist, multisum

def plot_max_spectra(shot_number, path_shots: str, lines_files: list, spec: dict, 
                     ylim: list=[1e0, 5e5], min_peak: float=0.01, cal=None, 
                     sum=False, log=True, **kwargs):
    """
    Plot the maximum spectra from a shot file.

    Args:
        shot_number (str): Shot number to load data from.
        path_shots (str): Path to the directory containing shot files.
        lines_files (list): List of paths to line files for comparison.
        spec (dict): Species to check with its respective color for plot.
        ylim (list): Y-axis limits for the plot.
        min_peak (float): Minimum peak height as a fraction of the maximum spectrum to consider a peak.
        **kwargs: Additional keyword arguments for plotting.
    """
    
    data = load_shot(shot_number, path_shots)
    
    # Get the maximum spectrum
    if sum:
        max_spectra = multisum([data])
    else:
        max_spectra = multimax([data])
    # Recalibrate the wavelengths??
    if cal is not None:
        with open(cal, 'r') as f:
            cal_data = json.load(f)
        # Apply calibration to the wavelengths
        max_spectra['wave'][0] = np.array(max_spectra['wave'][0]) * cal_data['slope'] + cal_data['intercept']
    
    #Find peaks in the maximum spectrum
    # height_threshold = min_peak * np.max(max_spectra['spectra'][0])  # Adjust height threshold as needed
    height_threshold = min_peak * ylim[1]  # Adjust height threshold as needed
    # height_threshold = min_peak
    print(f"Analyzing peaks for shot {shot_number[0]}")
    peaks, _ = find_peaks(max_spectra['spectra'][0], height=height_threshold, distance=3)  # Adjust height threshold as needed
    peak_wavelengths = max_spectra['wave'][0][peaks]
    peak_counts = max_spectra['spectra'][0][peaks]
    print(f"Number of peaks found: {len(peaks)}")
    print(f"Peaks found at indices: {peaks}")
    print(f"Peak wavelengths: {peak_wavelengths}")
    print(f"Peak counts: {peak_counts}")
    
    # Load tabulated data for lines
    data_lines = {
        'Wavelength': np.array([]),
        'Species': np.array([]),
        'Intensity': np.array([]),
        'Ref': np.array([])
    }
    for i, line_file in enumerate(lines_files):
        line_data = load_NIST_data(line_file)
        data_lines['Wavelength'] = np.concatenate((data_lines['Wavelength'], line_data['Wavelength']))
        data_lines['Species'] = np.concatenate((data_lines['Species'], line_data['Species']))
        data_lines['Intensity'] = np.concatenate((data_lines['Intensity'], line_data['Intensity']))
        data_lines['Ref'] = np.concatenate((data_lines['Ref'], line_data['Ref']))
    
    # Compare peaks with data
    data_spec = compare_peaks_with_nist(peaks, peak_wavelengths, peak_counts, data_lines, species=list(spec.keys()))
    
    fig, ax = plt.subplots()
    # Plot the maximum spectrum
    ax.plot(max_spectra['wave'][0], max_spectra['spectra'][0], lw=2, label='Spectrum', color='black')
    # Set how precise are the peaks
    tolerance = 1.2  # nm tolerance for peak matching
    for i, key in enumerate(spec.keys()):
        color = spec[key]
        mask = abs(data_spec[key]['delta']) < tolerance
        ax.scatter(data_spec[key]['wave'][mask], 
                   data_spec[key]['counts'][mask], 
                   label=f'{key}', marker='x', 
                   color=color, zorder=i+5, s=50)
    # Set the legend outside the plot
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    ax.set_xlabel(r'$\lambda$ (nm)')
    ax.set_ylabel('Counts')
    if log:
        ax.set_yscale('log')
    ax.set_ylim(ylim[0], ylim[1])
    ax.set_title('Shot: ' + shot_number)
    ax.set_xlim(np.min(max_spectra['wave'][0]), np.max(max_spectra['wave'][0]))
    plt.show()
    
    fig.savefig(os.path.join(path_shots, 'Plots', f'{shot_number}_max_spectrum.png'), dpi=900, bbox_inches='tight')
    # fig.savefig(os.path.join(path_shots, 'Plots', f'{shot_number}_max_spectrum.svg'), bbox_inches='tight')

    return data_spec, max_spectra

def barplotcheck(wave: np.array=None, counts: np.array=None, intensity: np.array=None, delta: np.array=None, **kwargs):
    """
    Create a bar plot to compare measured peaks with tabulated intensities.

    Args:
        wave (array): Measured wavelengths.
        counts (array): Measured counts.
        intensity (array): Tabulated intensities.
        delta (array): Difference between measured and tabulated wavelengths.
        **kwargs: Additional keyword arguments for plotting.
    """
    fig, ax = plt.subplots()
    width = 0.4  # Width of the bars
    x = np.arange(len(wave))  # the label locations

    bars1 = ax.bar(x - width/2, counts, width, label='Measured Counts', color='blue', alpha=0.7)
    error = ax.errorbar(x - width/2, counts, xerr=abs(delta), fmt='o', color='black', capsize=5, label='Wavelength Error')
    ax_t = ax.twinx()  # instantiate a second axes that shares the same x-axisº
    bars2 = ax_t.bar(x + width/2, intensity, width, label='Tabulated Intensity', color='orange', alpha=0.7)
    ax_t.set_ylabel('Tabulated Intensity')
    ax.set_ylabel('Measured Counts')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{w:.1f}" for w in wave], rotation=45)
    ax.set_xlabel('Wavelength (nm)')
    ax.set_title('Comparison of Measured Peaks with Tabulated Intensities')
    # log scale
    ax.set_yscale('log')
    ax.legend(loc='upper left')
    ax_t.legend(loc='upper right')  
    plt.tight_layout()
    plt.show()
    
    return fig, ax, ax_t


if __name__ == "__main__":

    path_spectrometer = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path_shots = os.path.join(path_spectrometer, 'Shots')
    # Compare the peak wavelengths with NIST data
    nist_file_path = os.path.join(path_spectrometer,'OOSpec_Control', 'peaks','ArNIST.txt')  # Adjust path as needed
    ebs_file_path = os.path.join(path_spectrometer, 'OOSpec_Control', 'peaks', 'ArEBS_Air.txt')  # Adjust path as needed
    N_file_path = os.path.join(path_spectrometer, 'OOSpec_Control', 'peaks', 'NNIST.txt')  # Adjust path as needed
    O_file_path = os.path.join(path_spectrometer, 'OOSpec_Control', 'peaks', 'ONIST.txt')  # Adjust path as needed
    C_file_path = os.path.join(path_spectrometer, 'OOSpec_Control', 'peaks', 'CNIST.txt')  # Adjust path as needed
    He_file_path = os.path.join(path_spectrometer, 'OOSpec_Control', 'peaks', 'HeNIST.txt')  # Adjust path as needed
    Fe_file_path = os.path.join(path_spectrometer, 'OOSpec_Control', 'peaks', 'FeNIST.txt')  # Adjust path as needed
    
    # Callibration file paths
    cal_file_path = os.path.join(path_spectrometer, 'OOSpec_Control', 'peaks', 'cal.json')

    # Define the colors for each species
    
    colors = {
        # 'He I': 'blue',
        # 'He II': 'red',
        'Ar I': 'orange',
        'Ar II': 'yellow',
        # 'Ar III': 'purple',
        # 'Ar IV': 'pink',
        # 'N I': 'green',
        # 'N II': 'purple',
        # 'O I': 'cyan',
        # 'O II': 'magenta',
        # 'C I': 'brown',
        # 'C II': 'pink',
        # 'Fe I': 'gray',
        # 'Fe II': 'olive',
    }

    # shot_number=["000160", "000177", "000178", "000179", "000180", "000181",
    #              "000210", "000211", "000212", "000213", "000214", "000215", 
    #              "000216", "000217", "000218", "000219", "000221"]
    shot_number=["000181","000210","000211"]
    # line_files = [nist_file_path, ebs_file_path, N_file_path, O_file_path, 
    #               C_file_path, He_file_path, Fe_file_path]
    # line_files = [He_file_path]
    line_files = [nist_file_path]
    data_list = {
    }
    for shot in shot_number:
        data_list[shot] = plot_max_spectra(shot, path_shots, line_files, 
                                           colors, ylim=[1e1, 5e4], 
                                           min_peak=0.001, cal=cal_file_path, 
                                           sum=False, log=True)[0]
        
        
    
    # Example of using barplotcheck for a specific shot and species
    pltdata = barplotcheck(**data_list['000211']['Ar I'])
        
    
    
    
    
    # ArI = data_list['000110']['Ar I']
    # mask = ArI['counts'] > 5e3
    
    # peaks_tab = ArI['wave'][mask]
    # peaks_mes = ArI['wave_mes'][mask]
    
    # slope, intercept, r_value, p_value, std_err = linregress(peaks_mes, peaks_tab)
    # print(f"Slope: {slope}, Intercept: {intercept}, R-squared: {r_value**2}")
    
    
    
    
