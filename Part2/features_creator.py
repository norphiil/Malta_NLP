import os
import wave
import contextlib
import numpy as np
import speech_recognition as sr
import librosa
import pandas as pd
from pocketsphinx import AudioFile
from scipy.signal import find_peaks
from scipy.signal.windows import blackman
from scipy.fftpack import fft

# Define the list of words to be recognized
words_recognize = [
    "heed", "hid", "head", "had", "hard", "hudd", "hod", "heard", "hoard", "hood",
    "who'd", "hade", "hid", "hoid", "hoed", "howd", "heered", "hared", "hured", "heed"
]

# Define the ARPABET notation mapping (simplified for demonstration purposes)
arpabet_mapping = {
    "heed": "IY", "hid": "IH", "head": "EH", "had": "AE", "hard": "AA",
    "hudd": "AH", "hod": "AA", "heard": "ER", "hoard": "AO", "hood": "UH",
    "who'd": "UW", "hade": "EY", "hoid": "OY", "hoed": "OW", "howd": "AW",
    "heered": "IY", "hared": "EH", "hured": "ER", "heed": "IY"
}

words_to_recognize = ["heed", "head", "hard"]

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
    # Apply Blackman window
    w = blackman(len(y))
    y = y * w

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
    peaks, _ = find_peaks(amplitude_spectrum, rel_height=0.9)
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
        word = words_recognize[i]
        print(f"Processing word: {word}")
        if word not in words_to_recognize:
            continue
        start_time = phrase.start_frame / float(sr)
        end_time = (phrase.start_frame + phrase.n_frames()) / float(sr)
        word_audio = y[int(start_time * sr):int(end_time * sr)]

        # Extract features
        # f1, f2, f3 = extract_formants(word_audio, sr)
        f1, f2, f3 = "None", "None", "None"
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
        if word == words_to_recognize[-1]:
            break
    return results


# Main function to process all files and save results to CSV
def main(audio_files, output_csv):
    all_results = []
    for file_info in audio_files:
        print(f"Processing file: {file_info[0]}")
        file_path, speaker_label, gender = file_info
        results = process_audio(file_path, speaker_label, gender)
        all_results.extend(results)

    df = pd.DataFrame(all_results)
    df.to_csv(output_csv, index=False)


def get_audio_files(base_path, num_group_folders=5, num_speaker_folders=5):
    audio_files = []
    group_folders = []

    # Get the group level folders (e.g., brm_001, lan_001)
    for root, dirs, files in os.walk(base_path):
        if root == base_path:
            group_folders = dirs[:num_group_folders]
            break

    for group in group_folders:
        group_path = os.path.join(base_path, group)
        gender_folders = ['female', 'male']

        for gender in gender_folders:
            gender_path = os.path.join(group_path, gender)
            if os.path.exists(gender_path):
                speaker_folders = []

                for root, dirs, files in os.walk(gender_path):
                    if root == gender_path:
                        speaker_folders = dirs[:num_speaker_folders]
                        break

                for speaker in speaker_folders:
                    speaker_path = os.path.join(gender_path, speaker)
                    for root, dirs, files in os.walk(speaker_path):
                        for file in files:
                            if file.endswith(".wav"):
                                file_path = os.path.join(root, file)
                                print(f"Found file: {file_path}")
                                group_label = group.split("_")[0]
                                speaker_label = speaker
                                audio_files.append(
                                    (file_path,
                                     group_label + "_" + speaker_label,
                                     gender)
                                )

    return audio_files


audio_files = get_audio_files("accents", num_group_folders=5, num_speaker_folders=5)

output_csv = "features.csv"
main(audio_files, output_csv)
