import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
df = pd.read_csv("cleaned_dataset.csv")

# Replace "None" with NaN (so we can handle missing values)
df.replace("None", pd.NA, inplace=True)

# Fill missing symptoms with empty string
df.fillna("", inplace=True)

# Convert symptoms into a single string per row (text-based approach)
df["combined_symptoms"] = df.iloc[:, 1:].apply(lambda x: " ".join(x), axis=1)

# Select features (X) and target (y)
X = df["combined_symptoms"]
y = df["Disease"]

# Convert text symptoms into numerical features using TF-IDF
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer()
X_vectorized = vectorizer.fit_transform(X)

# Split into train & test sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Test the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")

# Save the trained model
joblib.dump(model, "symptom_checker_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")
print("Model & vectorizer saved successfully!")