# Calibration.py
def get_calibration_data(spectra_file):
    """
    Load calibration data for Mercury and Helium spectra.
    
    Returns:
    - Wavelengths: List of wavelengths from the Mercury calibration file.
    - Counts: List of counts from the Mercury calibration file.
    """
    # Define the path to the calibration files
    Counts = []
    Wavelengths = []
    with open(spectra_file, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                wavelength = float(parts[0])
                count = float(parts[1])
                Wavelengths.append(wavelength)
                Counts.append(count)
                
    return Wavelengths, Counts

def plot_close_lines(ax, index_mes, peak_mes, peak_tab,color='red'):
    """
    Plot vertical lines for close peaks in the spectrum.
    
    Parameters:
    - ax: Matplotlib axis object to plot on.
    - peak_mes: List of measured peak wavelengths.
    - peak_tab: List of tabulated peak wavelengths.
    """
    peaks = {
        'wave': [],
        'wave_mes': [],
        'index_mes': [],
    }
    for i, wave in enumerate(peak_mes):
        # Check closeness to tabulated peaks
        close_peaks = [p for p in peak_tab if abs(p - wave) < 1.5]  # 1.5 nm tolerance
        if close_peaks:
            for close_peak in close_peaks:
                ax.axvline(close_peak, color=color, linestyle='--', linewidth=0.5)
                ax.text(close_peak, 50000, f'{close_peak:.3f} nm', 
                        rotation=90, verticalalignment='bottom', color=color, fontsize=8)
                peaks['wave'].append(close_peak)
                peaks['wave_mes'].append(wave)
                peaks['index_mes'].append(index_mes[i])
    peaks['wave'] = np.array(peaks['wave'])
    peaks['wave_mes'] = np.array(peaks['wave_mes'])
    
    return peaks
    
if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    from scipy.signal import find_peaks
    import json
    from scipy.stats import linregress
    
    from  peaks.load_NIST import load_NIST_data


    path = os.path.dirname(os.path.abspath(__file__))
    cal_path = os.path.join(path, 'peaks')
    # Spectrometer measurements for calibration
    Hg_spectra_file = os.path.join(cal_path, 'CalHg.txt')
    He_spectra_file = os.path.join(cal_path, 'CalHe.txt')

    Hg_wavelengths, Hg_counts = get_calibration_data(Hg_spectra_file)
    He_wavelengths, He_counts = get_calibration_data(He_spectra_file)
    
    # Load NIST data for Mercury and Helium
    Hg_nist_data = load_NIST_data(os.path.join(cal_path, 'HgNIST.txt'))
    He_nist_data = load_NIST_data(os.path.join(cal_path, 'HeNIST.txt'))
    Hg_nist_wavelengths = np.array(Hg_nist_data['Wavelength']) * 1e-1  # Convert from cm to nm
    He_nist_wavelengths = np.array(He_nist_data['Wavelength']) * 1e-1  # Convert from cm to nm
    Hg_nist_intensity = np.array(Hg_nist_data['Intensity'])
    He_nist_intensity = np.array(He_nist_data['Intensity'])

    # Find peaks in the Mercury and Helium spectra
    Hg_peaks, _ = find_peaks(Hg_counts, height=0.1 * np.max(Hg_counts), distance=15)
    He_peaks, _ = find_peaks(He_counts, height=0.1 * np.max(He_counts), distance=15)
    He_peaks_wavelengths = np.array(He_wavelengths)[He_peaks]
    Hg_peaks_wavelengths = np.array(Hg_wavelengths)[Hg_peaks]
    He_peaks_counts = np.array(He_counts)[He_peaks]
    Hg_peaks_counts = np.array(Hg_counts)[Hg_peaks]

    # Plot the calibration spectra
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(Hg_wavelengths, Hg_counts, label='Mercury Calibration', color='blue')
    ax.plot(He_wavelengths, He_counts, label='Helium Calibration', color='orange')
    ax.scatter(Hg_peaks_wavelengths, Hg_peaks_counts, color='blue', marker='o', label='Hg Peaks')
    for i, wave in enumerate(Hg_peaks_wavelengths):
        ax.text(wave, Hg_peaks_counts[i], f'{wave:.3f} nm', 
                verticalalignment='bottom', color='red', fontsize=8)
    ax.scatter(He_peaks_wavelengths, He_peaks_counts, color='orange', marker='o', label='He Peaks')
    for i, wave in enumerate(He_peaks_wavelengths):
        ax.text(wave, He_peaks_counts[i], f'{wave:.3f} nm', 
                verticalalignment='bottom', color='red', fontsize=8)
    close_Hg = plot_close_lines(ax, Hg_peaks, Hg_peaks_wavelengths, Hg_nist_wavelengths[Hg_nist_intensity > 100], color='blue')
    close_He = plot_close_lines(ax, He_peaks, He_peaks_wavelengths, He_nist_wavelengths[He_nist_intensity > 100], color='orange')
    ax.set_xlabel(r'$\lambda$ (nm)')
    ax.set_ylabel('Counts')
    ax.set_xlim(np.min(Hg_wavelengths), np.max(Hg_wavelengths))
    ax.set_title('Calibration Spectra for Mercury and Helium')
    
    wave_mes = np.concatenate((close_Hg['wave_mes'], close_He['wave_mes']))
    wave_tab = np.concatenate((close_Hg['wave'], close_He['wave']))
    index_mes = np.concatenate((close_Hg['index_mes'], close_He['index_mes']))
    
    # Perform linear regression to find the calibration coefficients
    slope, intercept, r_value, p_value, std_err = linregress(wave_mes, wave_tab)
    slope_index, intercept_index, r_value_index, p_value_index, std_err_index = linregress(index_mes, wave_tab)
    
    print(f"Calibration slope: {slope:.6f}, intercept: {intercept:.6f}, r_value: {r_value**2:.10f}, p_value: {p_value:.6f}, std_err: {std_err:.6f}")
    print(f"Calibration slope (index): {slope_index:.6f}, intercept: {intercept_index:.6f}, r_value: {r_value_index**2:.10f}, p_value: {p_value_index:.6f}, std_err: {std_err_index:.6f}")
    
    # Save calibration data to a JSON file
    cal_data = {
        'slope': slope,
        'intercept': intercept,
        'r_value': r_value,
        'p_value': p_value,
        'std_err': std_err,
        'slope_index': slope_index,
        'intercept_index': intercept_index,
        'r_value_index': r_value_index,
        'p_value_index': p_value_index,
        'std_err_index': std_err_index,
        'wave_mes': wave_mes.tolist(),
        'wave_tab': wave_tab.tolist(),
        'index_mes': index_mes.tolist(),
    }
    
    cal_file_path = os.path.join(cal_path, 'cal.json')
    with open(cal_file_path, 'w') as f:
        json.dump(cal_data, f, indent=4)
    print(f"Calibration data saved to {cal_file_path}")
    





            
