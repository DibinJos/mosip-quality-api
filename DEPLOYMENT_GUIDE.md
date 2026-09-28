# MOSIP Biometric Quality Check API - Free Hosting Deployment Guide

This guide shows how to deploy the Flask biometric quality check API to free hosting platforms.

## Files Included

- `quality_check_api.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `Procfile` - Deployment configuration for Render/Heroku
- `Dockerfile` - Docker container configuration
- `DEPLOYMENT_GUIDE.md` - This file

---

## Option 1: Deploy on Replit (Easiest)

Replit is the easiest option - no credit card needed, can run directly from browser.

### Steps:

1. **Create Replit Account**
   - Go to https://replit.com
   - Sign up for free
   - Click "Create Repl"

2. **Set Up Project**
   - Choose "Python" as language
   - Name it "mosip-quality-api"
   - Click "Create Repl"

3. **Upload Files**
   - Click on "Upload file" or drag-and-drop:
     - `quality_check_api.py`
     - `requirements.txt`

4. **Install Dependencies**
   - Replit auto-detects `requirements.txt`
   - It will install automatically
   - Or manually run in terminal: `pip install -r requirements.txt`

5. **Run the Application**
   - Click "Run" button (or `python quality_check_api.py`)
   - Server will start on `https://[your-replit-name].replit.dev`

6. **Test the API**
   ```bash
   curl https://[your-replit-name].replit.dev/health
   ```

**Pros:**
- Absolutely no setup required
- Free forever (within usage limits)
- Live link immediately

**Cons:**
- Replit may put project to sleep after inactivity
- Limited resources (less powerful)

---

## Option 2: Deploy on Render (Recommended)

Render offers good free tier with persistent URLs and automatic deployments.

### Prerequisites:
- GitHub account (free)
- Render account (free)

### Steps:

1. **Push Code to GitHub**
   ```bash
   # Initialize git repo locally
   cd /path/to/api/folder
   git init
   git add quality_check_api.py requirements.txt Procfile
   git commit -m "Initial commit: MOSIP quality check API"
   git branch -M main
   
   # Create new repo on GitHub (https://github.com/new)
   git remote add origin https://github.com/[username]/mosip-quality-api.git
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to https://render.com
   - Sign up for free (link GitHub account)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select `mosip-quality-api` repository

3. **Configure Render**
   - **Name:** `mosip-quality-api`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn quality_check_api:app --bind 0.0.0.0:8080`
   - **Region:** Choose closest to you
   - **Plan:** Free tier

4. **Deploy**
   - Click "Create Web Service"
   - Render will auto-deploy
   - Your API URL: `https://mosip-quality-api-[random].onrender.com`

5. **Test**
   ```bash
   curl https://mosip-quality-api-[random].onrender.com/health
   ```

**Pros:**
- Persistent URL (doesn't sleep)
- Good free tier
- Auto-deploys on code push
- Easy GitHub integration

**Cons:**
- Takes ~2-3 minutes to deploy
- Free tier has some resource limits

---

## Option 3: Deploy on Railway

Railway is modern and easy, with auto-deployment from GitHub.

### Steps:

1. **Push to GitHub** (same as Render above)

2. **Create Railway Account**
   - Go to https://railway.app
   - Sign up free (GitHub recommended)

3. **Connect GitHub Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select `mosip-quality-api` repo
   - Click "Deploy Now"

4. **Configure Environment**
   - Railway auto-detects Python
   - Sets up based on `Procfile` and `requirements.txt`
   - Takes ~5-10 minutes to build and deploy

5. **Get URL**
   - Once deployed, Railway generates URL
   - Find it in the project settings
   - Format: `https://mosip-quality-api-[id].railway.app`

6. **Test**
   ```bash
   curl https://mosip-quality-api-[id].railway.app/health
   ```

**Pros:**
- Very straightforward
- Good UI
- Free tier is generous

**Cons:**
- Free tier may have usage limits
- Needs GitHub account

---

## Option 4: Deploy Locally (Testing Only)

For local testing before deploying to cloud:

### Steps:

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Server**
   ```bash
   python quality_check_api.py
   ```

3. **Access API**
   - Server runs on `http://localhost:8080`
   - Health check: `curl http://localhost:8080/health`

**Use For:**
- Development and testing
- Integration with local MOSIP registration client
- Before deploying to cloud

---

## Testing the API

### 1. Health Check
```bash
curl http://your-api-url/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-09-28T10:30:45.123456",
  "service": "MOSIP Biometric Quality Check API"
}
```

### 2. API Info
```bash
curl http://your-api-url/quality/check/info
```

**Response:**
```json
{
  "name": "MOSIP Biometric Quality Check API",
  "version": "1.0.0",
  "supported_biometric_types": ["FINGERPRINT", "IRIS", "FACE"],
  "quality_thresholds": {
    "FINGERPRINT": 60.0,
    "IRIS": 65.0,
    "FACE": 70.0
  }
}
```

### 3. Quality Check (Full Test)

Create a test script `test_api.py`:

```python
import requests
import base64
import cv2
import numpy as np

# Create a test image (e.g., fingerprint simulation)
test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
_, buffer = cv2.imencode('.jpg', test_image)
image_base64 = base64.b64encode(buffer).decode('utf-8')

# Send to API
api_url = "http://localhost:8080/quality/check"  # or your deployed URL
payload = {
    "image": image_base64,
    "biometric_type": "FINGERPRINT",
    "bio_attribute": "Right Index",
    "field_id": "biometrics",
    "capture_timestamp": 1696945445000,
    "mdm_quality_score": 75.5,
    "retry_count": 1
}

response = requests.post(api_url, json=payload)
print(response.json())
```

Run it:
```bash
python test_api.py
```

---

## Integration with MOSIP Registration Client

Once deployed, integrate the API URL in your Java code:

```java
// In GenericBiometricsController.java
private static final String QUALITY_CHECK_API_URL = "https://your-api-url/quality/check";

private void checkBiometricQuality(BiometricsDto bioDto) throws Exception {
    HttpClient client = HttpClient.newHttpClient();
    String imageBase64 = Base64.getEncoder().encodeToString(bioDto.getBioData());
    
    String jsonPayload = String.format(
        "{\"image\":\"%s\",\"biometric_type\":\"%s\",\"bio_attribute\":\"%s\"}",
        imageBase64, bioDto.getBioType(), bioDto.getBioAttribute()
    );
    
    HttpRequest request = HttpRequest.newBuilder()
        .uri(URI.create(QUALITY_CHECK_API_URL))
        .header("Content-Type", "application/json")
        .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
        .build();
    
    HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
    JsonObject result = Json.createReader(new StringReader(response.body())).readObject();
    
    boolean passed = result.getBoolean("passed");
    double score = result.getJsonNumber("quality_score").doubleValue();
    
    if (!passed) {
        logger.warning("Quality check failed: " + result.getString("recommendations"));
    } else {
        logger.info("Quality check passed with score: " + score);
    }
}
```

---

## Troubleshooting

### API Won't Start
- Check Python version: `python --version` (need 3.8+)
- Check dependencies: `pip list` (should have Flask, opencv-python, numpy)
- Check port: Make sure port 8080 is available

### Deployment Fails on Render
- Check Procfile format (must end with newline)
- Verify requirements.txt has all packages
- Check build logs in Render dashboard

### API Returns Errors
- Ensure image is valid Base64
- Check biometric_type is one of: FINGERPRINT, IRIS, FACE
- Look at server logs for detailed error messages

### CORS Issues
If calling from browser, update the Flask app to include CORS headers:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

Install CORS package:
```bash
pip install flask-cors
```

---

## Recommended Deployment Summary

| Platform | Setup Time | Free Tier | Best For |
|----------|-----------|----------|----------|
| **Replit** | 2 min | Forever (limited) | Quick testing |
| **Render** | 5 min | ~750 hrs/month | Production |
| **Railway** | 5 min | ~10 GB/month | Production |
| **Local** | 1 min | N/A | Development |

**Recommendation:** Use **Render** for a stable, always-on free API with persistent URL.

---

## Next Steps

1. Choose a deployment platform (Render recommended)
2. Push your code to GitHub
3. Create account on platform and connect repo
4. Get your API URL
5. Integrate URL into MOSIP registration client
6. Test with real biometric data from Mock MDS

Good luck! 🚀
