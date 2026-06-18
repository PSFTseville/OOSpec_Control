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

# set font size for plots
plt.rcParams.update({'font.size': 18})
# markersize
plt.rcParams['lines.markersize'] = 12

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
    
    fig, ax = plt.subplots(figsize=(8.5,6.1))
    # Plot the maximum spectrum
    ax.plot(max_spectra['wave'][0], max_spectra['spectra'][0], lw=2, label='Spectrum', color='black')
    # Set how precise are the peaks
    tolerance = 2  # nm tolerance for peak matching
    for i, key in enumerate(spec.keys()):
        color = spec[key]
        mask = abs(data_spec[key]['delta']) < tolerance
        ax.scatter(data_spec[key]['wave'][mask], 
                   data_spec[key]['counts'][mask], 
                   label=f'{key}', marker='x', 
                   color=color, zorder=i+5, s=75)
    # Set the legend outside the plot
    ax.legend(loc='upper left', bbox_to_anchor=(0.65, 1), fontsize='small')
    ax.set_xlabel(r'$\lambda$ (nm)')
    ax.set_ylabel('Counts')
    if log:
        ax.set_yscale('log')
    ax.set_ylim(ylim[0], ylim[1])
    ax.set_title('Shot: #' + shot_number)
    ax.set_xlim(np.min(max_spectra['wave'][0]), np.max(max_spectra['wave'][0]))
    plt.show()

    fig.savefig(os.path.join(path_shots, 'Plots', f'{shot_number}_max_spectrum.png'), dpi=400, bbox_inches='tight')
    # fig.savefig(os.path.join(path_shots, 'Plots', f'{shot_number[0]}_max_spectrum.svg'), bbox_inches='tight')

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


def plot_peaks(matches_dict):
    """Plots side-by-side bars for each peak on separate Y-axes.

    Multiple matches from the same species within a single peak are stacked as
    separate segments using varying alphas of the same base color.
    """
    # 1. Gather all unique species across the matches to assign base colors
    all_species = []
    for peak_data in matches_dict.values():
        for _, species, _ in peak_data["matches"]:
            all_species.append(species)

    unique_species = np.unique(all_species) if all_species else np.array([])

    # 2. Extract X-axis info and measured counts
    detected_wavelengths = np.array(
        [p["wavelength"] for p in matches_dict.values()]
    )
    measured_counts = np.array([p["counts"] for p in matches_dict.values()])

    num_peaks = len(detected_wavelengths)
    x_indices = np.arange(num_peaks)
    bar_width = 0.35

    # 3. Set up the figure and dual axes
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    # 4. Plot Measured Counts (Left Bar)
    ax1.bar(
        x_indices - bar_width / 2,
        measured_counts,
        width=bar_width,
        label="Measured Counts",
        color="darkgray",
        edgecolor="black",
        alpha=0.8,
    )

    # 5. Map unique species to standard Matplotlib colors
    cmap = plt.get_cmap("tab10")
    species_colors = {
        spec: cmap(i % 10) for i, spec in enumerate(unique_species)
    }

    # 6. Track the bottom position for stacking on the right bar
    bottoms = np.zeros(num_peaks)

    # Keep track of species we've added to the legend to avoid duplicates
    tracked_legend_species = set()

    # 7. Step through each peak and stack matches one by one
    for i, (peak_idx, peak_data) in enumerate(matches_dict.items()):
        # Dictionary to track how many times a species has appeared *in this peak*
        # to dynamically calculate the alpha degradation
        species_match_count = {}
        
        # plot a text with their number of peak detection order on top of the bar
        ax1.text(
            x_indices[i] + bar_width / 2,
            0.99 * measured_counts.max(),
            str(peak_idx),
            ha="center",
            va="bottom",
            fontsize=8,
            color="black",
        )

        for _, species, intensity in peak_data["matches"]:
            # Determine alpha based on how many times this species has matched this peak
            match_idx = species_match_count.get(species, 0)
            species_match_count[species] = match_idx + 1

            # Alpha drops by 25% for every duplicate match (minimum alpha of 0.25)
            alpha_val = max(1.0 - (match_idx * 0.25), 0.25)
            base_color = species_colors[species]

            # Only add a label for the legend if it's the first time seeing this species
            label = None
            if species not in tracked_legend_species:
                label = str(species)
                tracked_legend_species.add(species)
            


            # Plot the individual contribution segment
            ax2.bar(
                x_indices[i] + bar_width / 2,
                intensity,
                width=bar_width,
                bottom=bottoms[i],
                color=base_color,
                alpha=alpha_val,
                edgecolor="white",  # White border separates matches of the same color
                linewidth=0.8,
                label=label,
            )

            # Roll the baseline up for the specific peak stack
            bottoms[i] += intensity

    # 8. Add a global black border around the entire right bar stacks for visual cleanliness
    ax2.bar(
        x_indices + bar_width / 2,
        bottoms,
        width=bar_width,
        fill=False,
        edgecolor="black",
        linewidth=1,
    )

    # 9. Axes Labels and Formatting
    ax1.set_xticks(x_indices)
    ax1.set_xticklabels([f"{wl:.2f} nm" for wl in detected_wavelengths], rotation=45)

    ax1.set_xlabel("Detected Peak Wavelength")
    ax1.set_ylabel("Measured Intensity (Counts)", color="dimgray")
    ax2.set_ylabel("Tabulated Database Intensity (NIST)", color="indigo")

    ax1.tick_params(axis="y", labelcolor="dimgray")
    ax2.tick_params(axis="y", labelcolor="indigo")

    ax1.set_title(
        "Dual-Axis Comparison: Measured Counts vs. Discrete Tabulated Matches"
    )

    # Unify legends from both axes into a single legend block
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        title="Legend",
        bbox_to_anchor=(1.12, 1),
        loc="upper left",
    )

    plt.tight_layout()
    plt.show()
    


def plot_species_contributions(
    matches_dict, species, L, vertical_labels=False, log_scale=False
):
    """Plots side-by-side bars for each peak on separate Y-axes.

    The right bar represents the calculated physical contribution (T_ij * L_j)
    after solving the linear emissivity system.

    Parameters:
    - matches_dict: dict, the self.matches dictionary containing peak data.
    - species: List or array of strings used in the solver.
    - L: NumPy array of shape (N,), the calculated impurity emissivity levels.
    - vertical_labels: bool, if True, rotates the Y-axis labels/ticks vertically.
    - log_scale: bool, if True, sets both Y-axes to a logarithmic scale.
    """
    # 1. Gather all unique species across the matches to assign base colors
    all_species = []
    for peak_data in matches_dict.values():
        for _, db_spec, _ in peak_data["matches"]:
            all_species.append(db_spec)

    unique_db_species = (
        np.unique(all_species) if all_species else np.array([])
    )
    species_list = list(species)

    # 2. Extract X-axis info and measured counts
    detected_wavelengths = np.array(
        [p["wavelength"] for p in matches_dict.values()]
    )
    measured_counts = np.array([p["counts"] for p in matches_dict.values()])

    num_peaks = len(detected_wavelengths)
    x_indices = np.arange(num_peaks)
    bar_width = 0.35

    # 3. Set up the figure and dual axes
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    # Apply logarithmic scale if requested
    if log_scale:
        ax1.set_yscale("log")
        ax2.set_yscale("log")

    # 4. Plot Measured Counts (Left Bar)
    ax1.bar(
        x_indices - bar_width / 2,
        measured_counts,
        width=bar_width,
        label="Measured Counts",
        color="darkgray",
        edgecolor="black",
        alpha=0.8,
    )

    # 5. Map unique database species text to standard Matplotlib colors
    cmap = plt.get_cmap("tab10")
    species_colors = {
        spec: cmap(i % 10) for i, spec in enumerate(unique_db_species)
    }

    # 6. Track the bottom position for stacking on the right bar
    # If log scale is active, stacking must start above 0 (e.g., 1 or a tiny value)
    start_base = 1.0 if log_scale else 0.0
    bottoms = np.full(num_peaks, start_base)
    tracked_legend_species = set()

    # 7. Step through each peak and stack matches weighted by L
    for i, (peak_idx, peak_data) in enumerate(matches_dict.items()):
        species_match_count = {}

        # Place the peak detection index label dynamically above the measured bar
        ax1.text(
            x_indices[i] - bar_width / 2,
            measured_counts[i] + (0.01 * measured_counts.max()),
            str(peak_idx),
            ha="center",
            va="bottom",
            fontsize=9,
            color="black",
            weight="bold",
        )

        for _, db_species, intensity in peak_data["matches"]:
            db_species_str = str(db_species).strip()
            base_element = (
                db_species_str.split()[0] if db_species_str else ""
            )

            # Find the corresponding L index using the exact logic of your solver
            L_factor = 0.0
            if db_species_str in species_list:
                j = species_list.index(db_species_str)
                L_factor = L[j]
            elif base_element in species_list:
                j = species_list.index(base_element)
                L_factor = L[j]

            # Calculate actual physical contribution: T_ij * L_j
            calculated_contribution = intensity * L_factor

            # Skip drawing zero or negative contribution segments
            if calculated_contribution <= 0:
                continue

            # Determine alpha based on duplicate matches within this single peak
            match_idx = species_match_count.get(db_species_str, 0)
            species_match_count[db_species_str] = match_idx + 1
            alpha_val = max(1.0 - (match_idx * 0.25), 0.25)

            base_color = species_colors[db_species_str]

            label = None
            if db_species_str not in tracked_legend_species:
                label = db_species_str
                tracked_legend_species.add(db_species_str)

            # Plot calculated physical contribution segment
            ax2.bar(
                x_indices[i] + bar_width / 2,
                calculated_contribution,
                width=bar_width,
                bottom=bottoms[i],
                color=base_color,
                alpha=alpha_val,
                edgecolor="white",
                linewidth=0.8,
                label=label,
            )

            bottoms[i] += calculated_contribution

    # 8. Add a global black border around the right-hand calculated bars
    # We adjust the bottom parameter logic slightly if it's a log plot to prevent edge issues
    ax2.bar(
        x_indices + bar_width / 2,
        bottoms - start_base,
        width=bar_width,
        bottom=start_base,
        fill=False,
        edgecolor="black",
        linewidth=1,
    )

    # 9. Axes Labels and Formatting
    ax1.set_xticks(x_indices)
    ax1.set_xticklabels([f"{wl:.2f} nm" for wl in detected_wavelengths], rotation=45)
    ax1.set_xlabel("Detected Peak Wavelength")

    # Handle vertical alignment preference for Y-axis titles
    label_rotation = 90 if vertical_labels else None

    ax1.set_ylabel(
        "Measured Intensity (Counts)", color="dimgray", rotation=label_rotation
    )
    ax2.set_ylabel(
        "Calculated Emissivity Contribution ($T \\cdot L$)",
        color="indigo",
        rotation=label_rotation,
    )

    if vertical_labels:
        ax1.tick_params(axis="y", labelcolor="dimgray", labelrotation=90)
        ax2.tick_params(axis="y", labelcolor="indigo", labelrotation=90)
    else:
        ax1.tick_params(axis="y", labelcolor="dimgray")
        ax2.tick_params(axis="y", labelcolor="indigo")

    ax1.set_title(
        "Dual-Axis Comparison: Measured Counts vs. Solved Physical Contributions"
    )

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        title="Legend",
        bbox_to_anchor=(1.12, 1),
        loc="upper left",
    )

    plt.tight_layout()
    plt.show()


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
        'He I': 'blue',
        'He II': 'red',
        # 'Ar I': 'orange',
        # 'Ar II': 'yellow',
        # 'Ar III': 'purple',
        # 'Ar IV': 'pink',
        'N I': 'green',
        'N II': 'purple',
        'O I': 'cyan',
        'O II': 'magenta',
        'C I': 'brown',
        'C II': 'pink',
        # 'Fe I': 'gray',
        # 'Fe II': 'olive',
    }

    shot_number=['000287']
    # shot_number=["000181","000210","000211"]
    # line_files = [nist_file_path, ebs_file_path, N_file_path, O_file_path, 
    #               C_file_path, He_file_path, Fe_file_path]
    line_files = [He_file_path, O_file_path, C_file_path]
    # line_files = [nist_file_path]
    marklines = []
    data_list = {
    }
    for shot in shot_number:
        data_list[shot] = plot_max_spectra(shot, path_shots, line_files, 
                                           colors, ylim=[1e1, 7e4], 
                                           min_peak=0.001, cal=cal_file_path, 
                                           sum=False, log=True, marklines=marklines)[0]
        
        wave_He_II = 656.01
        wave_He_I = 667.82
        if data_list[shot]['He II']['wave'].size > 0:
            index_HeII = np.argmin(np.abs(data_list[shot]['He II']['wave'] - wave_He_II))
            counts_HeII = data_list[shot]['He II']['wave'][index_HeII]
            print(f"Shot {shot}: Closest He II line to {wave_He_II} nm is {index_HeII}")
        else:
            print(f"Shot {shot}: No He II lines found.")
            counts_HeII = 0

        if data_list[shot]['He I']['wave'].size > 0:
            index_HeI = np.argmin(np.abs(data_list[shot]['He I']['wave'] - wave_He_I))
            counts_HeI = data_list[shot]['He I']['wave'][index_HeI]
            print(f"Shot {shot}: Closest He I line to {wave_He_I} nm is {index_HeI}")
        else:
            print(f"Shot {shot}: No He I lines found.")
            counts_HeI = 0
            
        ratio = 10*counts_HeII / counts_HeI if counts_HeI != 0 else np.inf
        print(f"Shot {shot}: He II / He I ratio: {ratio}")
        Zeff = (ratio + 4) / (ratio + 2) if ratio != np.inf else np.inf
        print(f"Shot {shot}: Estimated Zeff: {Zeff}")
        

    # # Example of using barplotcheck for a specific shot and species
    # pltdata = barplotcheck(**data_list['000211']['Ar I'])
        
    
    
    
    
    # ArI = data_list['000110']['Ar I']
    # mask = ArI['counts'] > 5e3
    
    # peaks_tab = ArI['wave'][mask]
    # peaks_mes = ArI['wave_mes'][mask]
    
    # slope, intercept, r_value, p_value, std_err = linregress(peaks_mes, peaks_tab)
    # print(f"Slope: {slope}, Intercept: {intercept}, R-squared: {r_value**2}")
    
    
    
    
