import numpy as np
import matplotlib.pyplot as plt
import os 
import sys
from scipy.signal import find_peaks



sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from loader import load_shot, load_data
from peaks.load_NIST import load_NIST_data
from plots.plot import plot_peaks, plot_species_contributions
from spectra.compute import solve_species_level

species_files = {
    'He': 'HeNIST.txt',
    'Hg': 'HgNIST.txt',
    'C': 'CNIST.txt',
    'H': 'HNIST.txt',
    'O': 'ONIST.txt',
    'N': 'NNIST.txt',
    'Fe': 'FeNIST.txt',
    'Ar': 'ArNIST.txt',
    'Ne': 'NeNIST.txt',
}



class Spectrum:
    def __init__(self, shot: str=None, shotfiles=None, file=None,
                 species: list=None, **kwargs):
        
        self.shot = shot
        self.shotfiles = shotfiles
        self.file = file
        if species is None:
            raise ValueError("Species list must be provided.")
        else:
            self.species = species
        self._load_data(**kwargs)
        self._find_peaks(**kwargs)
        self._load_spec(**kwargs)
        self.compare_peaks(**kwargs)
        self.L, self.L_ratio, self.T, self.I = self.compute_levels(**kwargs)

    def _load_data(self, remove_background=False, spectype=None, **kwargs):
        
        if self.shot is not None and self.shotfiles is not None:
            self.data = load_shot(self.shot, self.shotfiles)
        elif self.file is not None:
            # Load data from the specified file
            self.data = load_data(self.file)
        
        self.wavelengths = np.array(self.data['wave'])
        self.spectra = np.array(self.data['spectra']['2'])
        self.time_array = np.array(self.data['time'])
        
        if remove_background:
            self.spectra = self.spectra - self.spectra[0, :]
            self.spectra = np.clip(self.spectra, 0, None)
        else:
            # remove the minimum value of the spectra to ensure non-negative values
            self.spectra = self.spectra - np.min(self.spectra, axis=0)
        
        if spectype is not None:
            if spectype == 'max':
                self.spectrum = np.amax(self.spectra, axis=0)
                self.time_of_max = self.time_array[np.argmax(self.spectra, axis=0)]
            elif spectype == 'sum':
                self.spectrum = np.sum(self.spectra, axis=0)
                self.time_of_max = None  # Not applicable for summed spectrum
            else:
                raise ValueError(f"Unknown spectype: {spectype}. Use 'max' or 'sum'.")

    def _load_spec(self, **kwargs):
        """
        Load the spectrum data based on the provided parameters.
        
        Parameters:
        - kwargs: additional keyword arguments for loading data.
        """
        
        wave_list = np.array([])
        intensity_list = np.array([])
        ion_list = np.array([])
        for spec in self.species:
            if spec in species_files:
                file = species_files[spec]
                path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'peaks', file)
                data = load_NIST_data(path)

                wave_list = np.concatenate((wave_list, np.array(data['Wavelength']) * 1e-1))  # Convert from cm to nm
                intensity_list = np.concatenate((intensity_list, np.array(data['Intensity'])))
                ion_list = np.concatenate((ion_list, np.array(data['Species'])))
            else:
                raise ValueError(f"NIST data for species '{spec}' not found.")
            
        self.wavelengths_database = wave_list
        self.intensities_database = intensity_list
        self.ions_database = ion_list

    def _find_peaks(self, threshold=0.001, distance=3, **kwargs):
        """
        Find peaks in the spectrum data based on a threshold.
        
        Parameters:
        - threshold: float, the minimum value to consider as a peak.
        
        Returns:
        - peaks: list of tuples, each containing (x, y) coordinates of the peaks.
        """
        
        threshold_abs = threshold * np.max(self.spectrum)
        
        self.peaks, _ = find_peaks(self.spectrum, threshold=threshold_abs, distance=distance)
        self.peak_wavelengths = self.wavelengths[self.peaks]
        # Sum the counts of the 5 bins pre and post
        self.peak_counts = self.spectrum[self.peaks]
        self.peak_counts_sum = np.array([np.sum(self.spectrum[max(0, peak-5):min(len(self.spectrum), peak+6)]) for peak in self.peaks])
        
    def compare_peaks(self, tolerance=5, **kwargs):
        """
        Compare the detected peaks with the NIST database.
        
        Parameters:
        - tolerance: float, the maximum difference in wavelength to consider a match.
        
        Returns:
        - matches: list of tuples, each containing (detected_peak_wavelength, matched_database_wavelength, species).
        """
        
        precision = self.wavelengths[1] - self.wavelengths[0]  # Assuming uniform spacing
        toleranc_abs = tolerance * precision
        
        # Make a 2D array of detected peaks and database peaks
        detected_peaks_2d = np.expand_dims(self.peak_wavelengths, axis=1)
        database_peaks_2d = np.expand_dims(self.wavelengths_database, axis=0)
        
        diff_matrix = np.abs(detected_peaks_2d - database_peaks_2d)
        matches_mask = np.where(np.abs(diff_matrix) <= toleranc_abs)
        
        # For each detected peak assign all their matches in the database
        self.matches = {}
        for i, peak_wavelength in enumerate(self.peak_wavelengths):
            peak = {'wavelength': peak_wavelength, 
                    'counts': self.peak_counts_sum[i],
                    'counts_raw': self.peak_counts[i],
                    'matches': []}
            matched_indices = matches_mask[1][matches_mask[0] == i]
            for idx in matched_indices:
                matched_wavelength = self.wavelengths_database[idx]
                matched_species = self.ions_database[idx]
                matched_intensity = self.intensities_database[idx]
                peak['matches'].append((matched_wavelength, matched_species, matched_intensity))
            self.matches[i] = peak

    def plot_spectrum(self, ax=None, show_peaks=True, scale='linear', **kwargs):
        """
        Plot the spectrum data.
        
        Parameters:
        - ax: matplotlib axis object. If None, a new figure and axis will be created.
        - show_peaks: bool, whether to mark the detected peaks on the plot.
        - scale: str, the scale of the y-axis ('linear' or 'log').
        """
        if ax is None:
            fig, ax = plt.subplots()
        
        ax.plot(self.wavelengths, self.spectrum, label='Spectrum', color='blue')
        
        if show_peaks:
            # Plot each peak as a dot with their number of detection order
            for i, peak in self.matches.items():
                ax.plot(peak['wavelength'], peak['counts_raw'], 'ro')  # Red dot for the peak
                ax.annotate(str(i), (peak['wavelength'], peak['counts_raw']), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
        
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Counts')
        if scale == 'log':
            ax.set_yscale('log')
        ax.set_title(f'Shot {self.shot} - Spectrum')
        ax.legend()
        
        plt.show()
    
    
    def plot_peaks(self, contributions=True, **kwargs):
        """Plots detected peaks as stacked bars showing the contributions of matching database species.

        Parameters:
        - matches_dict: dict, the self.matches dictionary containing peak wavelengths,
                        counts, and a list of tuples for matches.
        """
        
        if contributions:
            plot_species_contributions(self.matches, self.species, self.L, **kwargs)
        else:
            plot_peaks(self.matches)
        
    
    def compute_levels(self, exclude_peaks=None, **kwargs):
        """
        Computes the impurity emissivity levels for the detected species.

        Parameters:
        - exclude_peaks: List or array of ints/keys, the keys of the matches_dict
                         to exclude from the calculation (default: None).

        Returns:
        - L: NumPy array of shape (N,), the calculated impurity emissivity levels.
        - L_ratio: NumPy array of shape (N,), the normalized impurity emissivity levels.
        - T: NumPy array of shape (M_filtered, N), the filtered contribution matrix.
        - I: NumPy array of shape (M_filtered,), the filtered measured intensity vector.
        """
        
        L, L_ratio, T, I = solve_species_level(self.species, self.matches, exclude_peaks=exclude_peaks)
        
        return L, L_ratio, T, I
    
    
                    
    


if __name__ == "__main__":
    # Example usage of the Spectrum class
    shot_number = '000178'
    path_shots = '/home/jessalsua/DAQ/Shots'
    
    
    
    spectrum = Spectrum(shot=shot_number, shotfiles=path_shots, remove_background=False, spectype='max',
                        species=['He', 'C', 'O', 'N', 'Ar'], tolerance=5, threshold=2.5e-4,
                        exclude_peaks=[0, 16, 17, 29, 30, 31])
    
    spectrum.plot_spectrum(show_peaks=True, scale='log')
    
    # L, L_ratio, T, I = spectrum.compute_levels(exclude_peaks=[32])  # Example of excluding the first two peaks from the calculation
    
    spectrum.plot_peaks(vertical_labels=True, contributions=False)
    spectrum.plot_peaks(contributions=True, log_scale=True, vertical_labels=True)
    
    
    # print the impurity level of each species
    for i, spec in enumerate(spectrum.species):
        print(f"Impurity level of {spec}: {spectrum.L[i]:.4f} (normalized by atomic number squared)")
        # compare with Helium level
        if spec != 'He':
            print(f"Relative to Helium: {(spectrum.L_ratio[i]) / (spectrum.L_ratio[0]):.4f}")
    
    C_air = spectrum.L_ratio[2:] / spectrum.L_ratio[2:].sum()  # Example of calculating the relative concentration of each species compared to the total of all species except Helium 
    
    # Print concentration to compare with air
    for i, spec in enumerate(spectrum.species[2:]):
        print(f"Air comparison for {spec}: {C_air[i]:.4f}")