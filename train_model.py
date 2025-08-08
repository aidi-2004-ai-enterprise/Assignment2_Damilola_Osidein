import seaborn as sns
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np

# Load the penguins dataset
df = sns.load_dataset('penguins')

# Drop rows with missing values
df = df.dropna()

# Define features and target
features = ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']
X = df[features]
y = df['species']

# Encode target variable (species) to numeric
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Create and train the XGBoost model
model = xgb.XGBClassifier(objective='multi:softmax', num_class=3, random_state=42)
model.fit(X_train, y_train)

# Save the model to a file
model.save_model('penguin_model.json')

# Print class mapping for reference
print("Class mapping:", dict(zip(range(len(le.classes_)), le.classes_)))