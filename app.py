from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import re
import os

app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "chrome-extension://*"}})

model = joblib.load('phishing_url_detector.pkl')

def extract_features(url):
    return {
        'url_length': len(url),
        'has_at_symbol': int('@' in url),
        'has_hyphen': int('-' in url),
        'has_https': int('https' in url.lower()),
        'num_dots': url.count('.'),
        'uses_ip': int(bool(re.match(r'\d+\.\d+\.\d+\.\d+', url))),
    }

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        url = data.get('url', '')
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        features = extract_features(url)
        features_df = pd.DataFrame([features])
        prediction = model.predict(features_df)[0]
        probability = model.predict_proba(features_df)[0].max()
        result = 'phishing' if prediction == 1 else 'benign'
        return jsonify({
            'url': url,
            'result': result,
            'confidence': float(probability)
        })
    except Exception as e:
        return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)