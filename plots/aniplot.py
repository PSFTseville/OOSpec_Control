import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
import os


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

def load_shot(shot_number, path_shots):
    """
    Load the spectra data for a specific shot number.

    Parameters:
    - shot_number: The shot number to load.
    - path_shots: Path to the directory containing the shot files.

    Returns:
    - data: Dictionary containing 'wave', 'spectra', and 'time'.
    """
    file_path = os.path.join(path_shots, f'{shot_number}.json')
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")
    return load_data(file_path)


def animate_spectra(data, shot_number=None, save_path=None, t_min=None, t_max=None):
    """
    Create an animation of the spectra data, optionally cropped in time.

    Parameters:
    - data: Dictionary containing 'wave', 'spectra', and 'time'.
    - shot_number: Optional shot number for labeling.
    - save_path: Optional path to save the animation.
    - t_min: Optional minimum time for cropping (in seconds).
    - t_max: Optional maximum time for cropping (in seconds).
    """
    wavelengths = np.array(data['wave'])
    spectra = np.array(data['spectra']['2'])
    time_array = np.array(data['time'])

    # Normalize and align time
    spectra = spectra - spectra[0, :]
    spectra = np.clip(spectra, 0, None)
    time_array = time_array - time_array[0]

    # Apply time cropping
    if t_min is not None or t_max is not None:
        mask = np.ones_like(time_array, dtype=bool)
        if t_min is not None:
            mask &= time_array >= t_min
        if t_max is not None:
            mask &= time_array <= t_max
        time_array = time_array[mask]
        spectra = spectra[mask]

    fig, ax = plt.subplots()
    ax.set_ylim(np.min(spectra), np.max(spectra))
    ax.set_xlabel(r'$\lambda$ (nm)')
    ax.set_ylabel('Counts')

    if shot_number is not None:
        ax.set_title(f'Shot Number: {shot_number}')

    def init():
        ax.clear()
        ax.plot([], [], lw=2)

    def update(frame):
        ax.clear()
        ax.plot(wavelengths, spectra[frame], lw=2)
        ax.set_xlim(np.min(wavelengths), np.max(wavelengths))
        ax.set_ylim(np.min(spectra), np.max(spectra))
        ax.set_xlabel(r'$\lambda$ (nm)')
        ax.set_ylabel('Counts')
        ax.text(0.02, 0.95, f'Time = {time_array[frame]:.3f} s', transform=ax.transAxes)

    ani = animation.FuncAnimation(fig, update, frames=len(spectra),
                                  init_func=init, blit=False, interval=1000)

    if save_path:
        ani.save(save_path, writer='ffmpeg')
        print(f"Animation saved to {save_path}")

    plt.show()
    return ani


if __name__ == "__main__":
    # Example usage
    path_spectrometer = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_shots = os.path.join(path_spectrometer, 'Shots')

    shot_number="000100"
    data = load_shot(shot_number=shot_number, path_shots=path_shots)
    


    ani = animate_spectra(
        data,
        shot_number=shot_number,
        save_path=os.path.join(path_shots, f'{shot_number}_animation.mp4'),
        t_min=6.7,  # crop start at 0.5 s
        t_max=7.5   # crop end at 2.0 s
    )
    
    wavelengths = np.array(data['wave'])
    spectra = np.array(data['spectra']['2'])
    time_array = np.array(data['time'])

    # Normalize and align time
    spectra = spectra - spectra[0, :]
    spectra = np.clip(spectra, 0, None)
    time_array = time_array - time_array[0]
    
    # Get the maximum spectrum
    max_spectrum = np.max(spectra, axis=0)
    # Plot the maximum spectrum
    fig_spec, ax_spec = plt.subplots()
    ax_spec.plot(wavelengths, max_spectrum, lw=2)
    ax_spec.set_xlabel(r'$\lambda$ (nm)')
    ax_spec.set_ylabel('Counts')
    ax_spec.set_title(f'Max Spectrum for Shot Number: {shot_number}')
    ax_spec.set_yscale('log')
    plt.show()
    
    fig_spec.savefig(os.path.join(path_shots, f'{shot_number}_max_spectrum.png'), dpi=400)
