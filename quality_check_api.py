"""
MOSIP Biometric Quality Check API
Mock endpoint for testing biometric quality
"""

from flask import Flask, request, jsonify
import base64
import numpy as np
import cv2
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Quality thresholds
QUALITY_THRESHOLDS = {
    'FINGERPRINT': 60.0,
    'IRIS': 65.0,
    'FACE': 70.0
}

class BiometricQualityAnalyzer:
    """Analyze biometric image quality"""

    @staticmethod
    def decode_image(image_base64):
        """Decode Base64 image to OpenCV format"""
        try:
            image_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            return image
        except Exception as e:
            logger.error(f"Error decoding image: {e}")
            raise ValueError(f"Failed to decode image: {str(e)}")

    @staticmethod
    def calculate_sharpness(image):
        """Calculate sharpness using Laplacian variance
        Higher value = sharper image"""
        if image is None:
            return 0.0

        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        # Normalize to 0-100 scale (typical sharp images have variance > 500)
        sharpness = min(100, (laplacian_var / 500) * 100)
        return round(sharpness, 2)

    @staticmethod
    def calculate_brightness(image):
        """Calculate brightness (0-100)
        Optimal range: 40-80"""
        if image is None:
            return 0.0

        brightness = np.mean(image)
        # Normalize to 0-100
        brightness_score = (brightness / 255) * 100

        # Penalize if too dark or too bright
        if brightness < 50:
            brightness_score *= 0.7  # Too dark
        elif brightness > 200:
            brightness_score *= 0.8  # Too bright

        return round(brightness_score, 2)

    @staticmethod
    def calculate_contrast(image):
        """Calculate contrast using standard deviation
        Higher contrast = higher std dev"""
        if image is None:
            return 0.0

        contrast = np.std(image)
        # Normalize to 0-100 (typical contrast std dev: 30-70)
        contrast_score = min(100, (contrast / 70) * 100)
        return round(contrast_score, 2)

    @staticmethod
    def detect_blur(image):
        """Detect motion blur (0-100, lower is more blurry)"""
        if image is None:
            return 0.0

        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        blur_score = laplacian.var()
        # Normalize: typically blur_score < 100 = blurry, > 500 = sharp
        normalized_blur = min(100, (blur_score / 500) * 100)
        return round(normalized_blur, 2)

    @staticmethod
    def analyze_quality(image_base64, biometric_type='FINGERPRINT'):
        """Comprehensive quality analysis"""
        try:
            # Decode image
            image = BiometricQualityAnalyzer.decode_image(image_base64)

            if image is None:
                raise ValueError("Failed to decode image")

            # Calculate quality metrics
            sharpness = BiometricQualityAnalyzer.calculate_sharpness(image)
            brightness = BiometricQualityAnalyzer.calculate_brightness(image)
            contrast = BiometricQualityAnalyzer.calculate_contrast(image)
            blur = BiometricQualityAnalyzer.detect_blur(image)

            # Overall quality score (weighted average)
            weights = {
                'sharpness': 0.35,
                'blur': 0.25,
                'contrast': 0.25,
                'brightness': 0.15
            }

            overall_quality = (
                sharpness * weights['sharpness'] +
                blur * weights['blur'] +
                contrast * weights['contrast'] +
                brightness * weights['brightness']
            )

            return {
                'overall': round(overall_quality, 2),
                'sharpness': sharpness,
                'brightness': brightness,
                'contrast': contrast,
                'blur': blur,
                'details': {
                    'sharpness_description': 'Good' if sharpness > 70 else 'Fair' if sharpness > 50 else 'Poor',
                    'brightness_description': 'Optimal' if 40 <= brightness <= 80 else 'Too Dark' if brightness < 40 else 'Too Bright',
                    'contrast_description': 'Good' if contrast > 60 else 'Fair' if contrast > 40 else 'Low',
                    'blur_description': 'Sharp' if blur > 70 else 'Slight Blur' if blur > 50 else 'Blurry'
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing quality: {e}")
            raise

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'MOSIP Biometric Quality Check API'
    }), 200

@app.route('/quality/check', methods=['POST'])
def quality_check():
    """
    Quality check endpoint

    Expected JSON request:
    {
        "image": "base64_encoded_image",
        "biometric_type": "FINGERPRINT|IRIS|FACE",
        "bio_attribute": "Right Index",
        "field_id": "biometrics",
        "capture_timestamp": 1696945445000,
        "mdm_quality_score": 75.5,
        "retry_count": 1
    }

    Response:
    {
        "quality_score": 85.5,
        "passed": true,
        "threshold": 70.0,
        "details": "...",
        "recommendations": "..."
    }
    """

    try:
        # Validate request
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Invalid JSON payload',
                'passed': False,
                'quality_score': 0
            }), 400

        # Extract fields
        image_base64 = data.get('image')
        biometric_type = data.get('biometric_type', 'FINGERPRINT')
        bio_attribute = data.get('bio_attribute', 'Unknown')
        field_id = data.get('field_id', 'biometrics')
        mdm_quality_score = data.get('mdm_quality_score', 0)
        retry_count = data.get('retry_count', 1)

        # Validate required fields
        if not image_base64:
            return jsonify({
                'error': 'Missing required field: image',
                'passed': False,
                'quality_score': 0
            }), 400

        logger.info(f"Processing {biometric_type} quality check for {bio_attribute}")

        # Analyze quality
        quality_metrics = BiometricQualityAnalyzer.analyze_quality(
            image_base64,
            biometric_type
        )

        overall_quality = quality_metrics['overall']
        threshold = QUALITY_THRESHOLDS.get(biometric_type, 65.0)
        passed = overall_quality >= threshold

        # Build details string
        details = (
            f"Sharpness: {quality_metrics['sharpness']}% ({quality_metrics['details']['sharpness_description']}) | "
            f"Brightness: {quality_metrics['brightness']}% ({quality_metrics['details']['brightness_description']}) | "
            f"Contrast: {quality_metrics['contrast']}% ({quality_metrics['details']['contrast_description']}) | "
            f"Blur: {quality_metrics['blur']}% ({quality_metrics['details']['blur_description']})"
        )

        # Recommendations
        recommendations = []
        if quality_metrics['sharpness'] < 70:
            recommendations.append("Image is not sharp enough. Ensure proper focus.")
        if quality_metrics['brightness'] < 40:
            recommendations.append("Image is too dark. Increase lighting.")
        elif quality_metrics['brightness'] > 80:
            recommendations.append("Image is too bright. Reduce lighting or adjust camera.")
        if quality_metrics['contrast'] < 60:
            recommendations.append("Image contrast is low. Improve lighting conditions.")
        if quality_metrics['blur'] < 50:
            recommendations.append("Image appears blurry. Avoid motion during capture.")

        if not recommendations:
            recommendations.append("Quality is acceptable. Capture successful.")

        response = {
            'quality_score': overall_quality,
            'passed': passed,
            'threshold': threshold,
            'biometric_type': biometric_type,
            'bio_attribute': bio_attribute,
            'field_id': field_id,
            'mdm_quality_score': mdm_quality_score,
            'retry_count': retry_count,
            'details': details,
            'metrics': {
                'sharpness': quality_metrics['sharpness'],
                'brightness': quality_metrics['brightness'],
                'contrast': quality_metrics['contrast'],
                'blur': quality_metrics['blur']
            },
            'recommendations': ' | '.join(recommendations),
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(
            f"Quality check result: {biometric_type} {bio_attribute} - "
            f"Score: {overall_quality}, Passed: {passed}"
        )

        return jsonify(response), 200

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'error': str(e),
            'passed': False,
            'quality_score': 0
        }), 400

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'passed': False,
            'quality_score': 0
        }), 500

@app.route('/quality/check/info', methods=['GET'])
def quality_info():
    """Get API information"""
    return jsonify({
        'name': 'MOSIP Biometric Quality Check API',
        'version': '1.0.0',
        'description': 'Analyzes biometric image quality for MOSIP registration client',
        'supported_biometric_types': list(QUALITY_THRESHOLDS.keys()),
        'quality_thresholds': QUALITY_THRESHOLDS,
        'quality_metrics': [
            'sharpness',
            'brightness',
            'contrast',
            'blur'
        ],
        'endpoints': {
            'health': '/health (GET)',
            'quality_check': '/quality/check (POST)',
            'info': '/quality/check/info (GET)'
        }
    }), 200

if __name__ == '__main__':
    # For local testing
    app.run(debug=True, host='0.0.0.0', port=8080)
