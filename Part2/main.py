import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, f1_score
import numpy as np

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('features.csv')

# Separate features and labels
X = df[['Formant1', 'Formant2', 'Formant3']]
y = df['Class']

# Run the experiment multiple times
num_experiments = 5
f1_scores = []

for i in range(num_experiments):
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=i)

    # Instantiate the k-NN classifier with k=5
    k = 5
    knn = KNeighborsClassifier(n_neighbors=k)

    # Train the classifier
    knn.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = knn.predict(X_test)

    # Generate the confusion matrix
    conf_matrix = confusion_matrix(y_test, y_pred)
    print(f"Experiment {i+1} - Confusion Matrix:\n", conf_matrix)

    # Calculate the F1 score
    f1 = f1_score(y_test, y_pred, average='weighted')
    f1_scores.append(f1)

# Calculate the average F1 score
average_f1_score = np.mean(f1_scores)
print("Average F1 Score after 5 experiments:", average_f1_score)
