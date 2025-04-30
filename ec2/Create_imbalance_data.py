from sklearn.datasets import load_iris
import pandas as pd

# Load the iris dataset
iris = load_iris()
X = pd.DataFrame(iris.data, columns=iris.feature_names)
y = pd.Series(iris.target)

# Separate the data into three classes
# (0, 1, 2) for the three species of iris
# (Setosa, Versicolor, Virginica)
X_0 = X[y == 0]
X_1 = X[y == 1]
X_2 = X[y == 2]

# Create an imbalanced dataset
X_0_sample = X_0.sample(75, replace=True, random_state=42)  # 75 (oversampling)
X_1_sample = X_1.sample(50, replace=False, random_state=42)  # 50 (original)
X_2_sample = X_2.sample(25, replace=False, random_state=42) # 25 (undersampling) 


# Recombine the samples to create an imbalanced dataset
X_imbalanced = pd.concat([X_0_sample, X_1_sample, X_2_sample])
y_imbalanced = ([0]*75) + ([1]*50) + ([2]*25)
y_imbalanced = pd.Series(y_imbalanced)

imbalanced_data = X_imbalanced.copy()  # Create a copy of the X_imbalanced DataFrame
imbalanced_data['target'] = y_imbalanced  # Add the target column to the DataFrame

# Save the imbalanced dataset to a CSV file
imbalanced_data.to_csv('./ec2/imbalanced_iris_dataset.csv', index=False)

print("Imbalanced dataset created and saved to 'imbalanced_iris_dataset.csv'")

# Verify the class distribution in the imbalanced dataset
print("Class distribution in the imbalanced dataset:")
print(y_imbalanced.value_counts())
