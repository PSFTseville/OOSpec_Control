import os
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf


from plots.aniplot import load_shot

def spectra_to_audio(spectra, sample_rate=44100, duration_per_frame=0.01, amplitude_multiplier=1e-6):
    """
    Fast conversion of spectra to audio using vectorized additive synthesis.
    """
    num_frames, num_bins = spectra.shape
    frame_samples = int(sample_rate * duration_per_frame)
    
    # Time vector for one frame
    t = np.linspace(0, duration_per_frame, frame_samples, endpoint=False)
    
    # Frequency bin mapping (adjust as needed)
    freqs = np.linspace(200, 5000, num_bins)  # Hz, linear scale
    
    # Shape: (num_bins, frame_samples)
    sinusoids = np.sin(2 * np.pi * freqs[:, np.newaxis] * t[np.newaxis, :])
    
    # Preallocate final audio
    audio = np.zeros(num_frames * frame_samples)

    for i in range(num_frames):
        frame = spectra[i]
        # Shape of frame_spectrum = (frame_samples,)
        frame_audio = np.dot(frame, sinusoids)
        # Add to the final audio array
        audio[i * frame_samples:(i + 1) * frame_samples] = frame_audio

    # Normalize
    audio /= np.max(np.abs(audio) + 1e-12)
    return audio

if __name__ == "__main__":
    # Example usage of the code
    print("This script is designed to load and process spectra data for sound generation.")
    print("Please ensure you have the necessary data files available.")
    shots = ['000210']
    # Define the path to the shots directory
    path_current = os.path.dirname(os.path.abspath(__file__))
    path_shots = os.path.join(os.path.dirname(path_current), 'Shots')


    for shot in shots:
        try:
            data = load_shot(shot, path_shots)
        except FileNotFoundError as e:
            print(f"Error loading shot {shot}: {e}")
        except Exception as e:
            print(f"An error occurred while processing shot {shot}: {e}")
    
        # Remove the bsackground noise
        spectra = np.array(data['spectra']['2'])
        spectra = spectra - spectra[0, :]  # Subtract the first frame as background noise
        
        audio = spectra_to_audio(spectra[420:480, ::-1], sample_rate=44100, duration_per_frame=0.04)
        
        output_path = os.path.join(path_shots, 'Audio','{}_audio.wav'.format(shot))
        # Save the audio file
        sf.write(output_path, audio, 44100)
        print(f"Audio saved to {output_path}")    
    
    
    
    
    
    