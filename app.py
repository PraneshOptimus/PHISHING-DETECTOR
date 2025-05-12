import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import re
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "chrome-extension://*"}})

logger.info("Loading model...")
model = joblib.load('phishing_url_detector.pkl')
logger.info("Model loaded successfully")

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
    logger.info("Received request to /predict")
    try:
        data = request.get_json()
        logger.info(f"Parsed JSON: {data}")
        url = data.get('url', '')
        if not url:
            logger.warning("URL is required")
            return jsonify({'error': 'URL is required'}), 400
        features = extract_features(url)
        features_df = pd.DataFrame([features])
        prediction = model.predict(features_df)[0]
        probability = model.predict_proba(features_df)[0].max()
        result = 'phishing' if prediction == 1 else 'benign'
        logger.info(f"Prediction: {result}, Confidence: {probability}")
        return jsonify({
            'url': url,
            'result': result,
            'confidence': float(probability)
        })
    except Exception as e:
        logger.error(f"Invalid JSON: {str(e)}")
        return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
