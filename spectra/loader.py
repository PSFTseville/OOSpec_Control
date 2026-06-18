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