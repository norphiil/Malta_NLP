import wave
import contextlib
import numpy as np
import speech_recognition as sr
import librosa
import pandas as pd
from pocketsphinx import AudioFile
from scipy.signal import blackman, find_peaks
from scipy.fftpack import fft

# Define the list of words to be recognized
words_to_recognize = [
    "Heed", "hid", "head", "had", "hard", "Hudd", "hod", "heard", "hoard", "hood",
    "who'd", "hade", "hid", "hoid", "hoed", "howd", "heered", "hared", "hured", "heed"
]

# Define the ARPABET notation mapping (simplified for demonstration purposes)
arpabet_mapping = {
    "Heed": "IY", "hid": "IH", "head": "EH", "had": "AE", "hard": "AA", 
    "Hudd": "AH", "hod": "AA", "heard": "ER", "hoard": "AO", "hood": "UH", 
    "who'd": "UW", "hade": "EY", "hoid": "OY", "hoed": "OW", "howd": "AW", 
    "heered": "IY", "hared": "EH", "hured": "ER", "heed": "IY"
}

# Class numbers for each ARPABET symbol
class_number_mapping = {symbol: idx + 1 for idx, symbol in enumerate(set(arpabet_mapping.values()))}

# Initialize recognizer
recognizer = sr.Recognizer()


# Function to get duration of a WAV file
def get_audio_duration(file_path):
    with contextlib.closing(wave.open(file_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    return duration


def extract_formants(y, sr):
    # Apply pre-emphasis filter
    pre_emphasis = 0.97
    emphasized_signal = np.append(y[0], y[1:] - pre_emphasis * y[:-1])

    # Apply Blackman window
    w = blackman(len(emphasized_signal))
    y = emphasized_signal * w

    # Perform FFT
    n = len(y)
    k = np.arange(n)
    T = n/sr
    frq = k/T
    frq = frq[range(n//2)]

    # Normalize to linear scale
    Y = fft(y)/n
    Y = Y[range(n//2)]
    amplitude_spectrum = 2*abs(Y)

    # Find peaks which represent formants
    peaks, _ = find_peaks(amplitude_spectrum, distance=15)
    formants = sorted(frq[peaks])

    # Return first three formants
    f1 = round(formants[0]) if len(formants) > 0 else "None"
    f2 = round(formants[1]) if len(formants) > 1 else "None"
    f3 = round(formants[2]) if len(formants) > 2 else "None"
    return f1, f2, f3


# Function to process audio and extract features
def process_audio(file_path, speaker_label, gender):
    # Load audio file
    y, sr = librosa.load(file_path, sr=None)
    results = []

    # Recognize and segment words
    audio = AudioFile(audio_file=file_path)
    for i, phrase in enumerate(audio):
        word = words_to_recognize[i]
        print(f"Processing word: {word}")
        start_time = phrase.start_frame / float(sr)
        end_time = (phrase.start_frame + phrase.n_frames()) / float(sr)
        word_audio = y[int(start_time * sr):int(end_time * sr)]

        # Extract features
        f1, f2, f3 = extract_formants(word_audio, sr)
        vowel_phoneme = arpabet_mapping[word]
        class_number = class_number_mapping[vowel_phoneme]

        # Append results
        results.append({
            "Speaker label": speaker_label,
            "Gender": gender,
            "Word": word,
            "Vowel Phoneme": vowel_phoneme,
            "Class Number": class_number,
            "Formant 1": f1,
            "Formant 2": f2,
            "Formant 3": f3
        })
    return results


# Main function to process all files and save results to CSV
def main(audio_files, output_csv):
    all_results = []
    for file_info in audio_files:
        print(f"Processing file: {file_info[0]}")
        file_path, speaker_label, gender = file_info
        results = process_audio(file_path, speaker_label, gender)
        all_results.extend(results)

    # Save to CSV
    df = pd.DataFrame(all_results)
    df.to_csv(output_csv, index=False)


# Example usage
audio_files = [
    ("accents/brm_001/female/alw001/cwa_CT.wav", "alw001", "F"),
    # Add more audio files as needed
]

output_csv = "output.csv"
main(audio_files, output_csv)
