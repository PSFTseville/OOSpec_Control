import numpy as np

Z_spec = {
    'He': 2,
    'H': 1,
    'C': 6,
    'O': 8,
    'N': 7,
    'Ar': 18,
    'Fe': 26
}


def solve_species_level(species, matches_dict, exclude_peaks=None):
    """Constructs the contribution matrix T and solves for the impurity
    emissivity levels L, handling species ionization notations (e.g., 'X I', 'X II').

    Parameters:
    - species: List or array of strings, the target species names (can be base elements
               like ['Fe', 'O'] or specific ions like ['Fe I', 'Fe II']).
    - matches_dict: dict, the self.matches dictionary containing peak data.
    - exclude_peaks: List or array of keys to exclude from the calculation.

    Returns:
    - L: NumPy array of shape (N,), the calculated impurity emissivity levels.
    - T: NumPy array of shape (M_filtered, N), the filtered contribution matrix.
    - I: NumPy array of shape (M_filtered,), the filtered measured intensity vector.
    """
    if exclude_peaks is None:
        exclude_peaks = []

    # 1. Filter out the excluded peaks
    valid_keys = [key for key in matches_dict.keys() if key not in exclude_peaks]

    num_peaks = len(valid_keys)
    num_species = len(species)
    species_list = list(species)

    # 2. Initialize Matrix T and Vector I
    T = np.zeros((num_peaks, num_species))
    I = np.zeros(num_peaks)

    # 3. Populate T and I
    for i, peak_key in enumerate(valid_keys):
        peak_data = matches_dict[peak_key]
        I[i] = peak_data["counts"]

        for _, db_species, intensity in peak_data["matches"]:
            # Ensure db_species is a string to manipulate it cleanly
            db_species_str = str(db_species).strip()

            # Extract the base element name (e.g., "Fe I" -> "Fe")
            base_element = db_species_str.split()[0] if db_species_str else ""

            # Route the matching intensity to the correct column matrix index
            if db_species_str in species_list:
                # Exact match case (e.g., target list contains 'Fe I' explicitly)
                j = species_list.index(db_species_str)
                T[i, j] += intensity
            elif base_element in species_list:
                # General match case (e.g., target list contains 'Fe', grouping 'Fe I' & 'Fe II')
                j = species_list.index(base_element)
                T[i, j] += intensity

    # 4. Solve the linear system I = T * L for L via least-squares
    L, residuals, rank, s = np.linalg.lstsq(T, I, rcond=None)
    
    # Make it relative to Z^2
    for i, spec in enumerate(species):
        if spec in Z_spec:
            L[i] /= Z_spec[spec] ** 2
    
    L_ratio = L / L[0]  # Normalize by the first species

    return L, L_ratio, T, I
    
    