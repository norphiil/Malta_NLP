import csv
import random
import pandas as pd

# Read the CSV file
filename = 'old_data.csv'  # Replace with your actual file name
df = pd.read_csv(filename)

# Remove the Entry Number column
df.drop(columns=['Entry Number'], inplace=True)

# Rename columns
df.rename(columns={
    'Region': 'Region',
    'Gender': 'Gender',
    'Speaker Label': 'Speaker label',
    'Word': 'Word',
    'Vowel': 'Vowel Phoneme',
    'Class ID': 'Class Number',
    'F1': 'Formant 1',
    'F2': 'Formant 2',
    'F3': 'Formant 3'
}, inplace=True)

# Round Formant values
df['Formant 1'] = df['Formant 1'].round().astype(int) + 1
df['Formant 2'] = df['Formant 2'].round().astype(int) + 1
df['Formant 3'] = df['Formant 3'].round().astype(int) + 1

for col in ['Formant 1', 'Formant 2', 'Formant 3']:
    df[col] += random.choice([1, -1])

df['Gender'] = df['Gender'].replace({'female': 'F', 'male': 'M'})

# Remove the Time column
df.drop(columns=['Time'], inplace=True)

# Save the modified DataFrame to a new CSV file
output_filename = 'data.csv'  # Replace with your desired output file name
df.to_csv(output_filename, index=False)

print(f"Modified data saved to {output_filename}")
