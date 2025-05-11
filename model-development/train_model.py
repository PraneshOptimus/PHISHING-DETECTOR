import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import re

# Load dataset (replace with your dataset)
data = pd.read_csv('datasets.csv')

# Feature extraction function
def extract_features(url):
    return {
        'url_length': len(url),
        'has_at_symbol': int('@' in url),
        'has_hyphen': int('-' in url),
        'has_https': int('https' in url.lower()),
        'num_dots': url.count('.'),
        'uses_ip': int(bool(re.match(r'\d+\.\d+\.\d+\.\d+', url))),
    }

# Extract features
features = data['url'].apply(extract_features).apply(pd.Series)
X = features
y = data['label']  # 1 for phishing, 0 for benign

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, 'phishing_url_detector.pkl')

# Evaluate
print("Accuracy:", model.score(X_test, y_test))