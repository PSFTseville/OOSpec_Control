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


def animate_spectra(data, shot_number=None, save_path=None):
    """
    Create an animation of the spectra data.

    Parameters:
    - data: Dictionary containing 'wave', 'spectra', and 'time'.
    - shot_number: Optional shot number for labeling.
    - save_path: Optional path to save the animation.
    """
    wavelengths = np.array(data['wave'])
    spectra = np.array(data['spectra']['2'])
    time_array = data['time']

    # Normalize spectra by subtracting the first spectrum
    spectra = spectra - spectra[0, :]

    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2)

    ax.set_xlim(800, 900)
    ax.set_ylim(np.min(spectra), np.max(spectra))
    ax.set_xlabel(r'$\lambda$ (nm)')
    ax.set_ylabel('Counts')
    ax.set_yscale('log')

    if shot_number is not None:
        ax.set_title(f'Shot Number: {shot_number}')

    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

    def init():
        line.set_data([], [])
        time_text.set_text('')
        return line, time_text

    def update(frame):
        line.set_data(wavelengths, spectra[frame])
        time_text.set_text(f'Time = {time_array[frame]} ms')
        return line, time_text

    ani = animation.FuncAnimation(fig, update, frames=len(spectra),
                                  init_func=init, blit=True, interval=200)

    if save_path:
        ani.save(save_path, writer='ffmpeg')
        print(f"Animation saved to {save_path}")

    plt.show()
    return ani


if __name__ == "__main__":
    # Example usage
    path_spectrometer = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_shots = os.path.join(path_spectrometer, 'Shots')

    shot_number = '000098'
    file_path = os.path.join(path_shots, f'{shot_number}.json')

    data = load_data(file_path)
    animate_spectra(data, shot_number=shot_number)

