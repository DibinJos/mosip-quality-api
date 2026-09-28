# Quick Start - Deploy in 5 Minutes

## Fastest Option: Render (Recommended)

### Step 1: Prepare Code
```bash
# Create a folder
mkdir mosip-quality-api
cd mosip-quality-api

# Copy these files into it:
# - quality_check_api.py
# - requirements.txt
# - Procfile
# - runtime.txt
```

### Step 2: Create GitHub Repo
```bash
git init
git add .
git commit -m "MOSIP quality check API"
git branch -M main

# Go to https://github.com/new and create "mosip-quality-api"
git remote add origin https://github.com/[YOUR-USERNAME]/mosip-quality-api.git
git push -u origin main
```

### Step 3: Deploy on Render
1. Go to https://render.com → Sign up (free)
2. Connect GitHub account
3. Click "New +" → "Web Service"
4. Select `mosip-quality-api` repo
5. Fill in:
   - Name: `mosip-quality-api`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn quality_check_api:app --bind 0.0.0.0:8080`
6. Click "Create Web Service"
7. Wait ~3 minutes for deployment
8. Get your URL from the dashboard

### Step 4: Test
```bash
curl https://[YOUR-DEPLOY-URL]/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "service": "MOSIP Biometric Quality Check API"
}
```

## Using the API

**Endpoint:** `POST https://[YOUR-URL]/quality/check`

**Request Example:**
```bash
curl -X POST https://[YOUR-URL]/quality/check \
  -H "Content-Type: application/json" \
  -d '{
    "image": "iVBORw0KGgoAAAANS...",
    "biometric_type": "FINGERPRINT",
    "bio_attribute": "Right Index",
    "field_id": "biometrics"
  }'
```

**Response:**
```json
{
  "quality_score": 75.5,
  "passed": true,
  "threshold": 60.0,
  "biometric_type": "FINGERPRINT",
  "bio_attribute": "Right Index",
  "metrics": {
    "sharpness": 80.5,
    "brightness": 65.0,
    "contrast": 72.3,
    "blur": 78.9
  },
  "details": "Sharpness: 80.5% (Good) | Brightness: 65.0% (Optimal) | Contrast: 72.3% (Good) | Blur: 78.9% (Sharp)",
  "recommendations": "Quality is acceptable. Capture successful.",
  "timestamp": "2026-09-28T10:30:45.123456"
}
```

## Other Options

- **Replit:** https://replit.com (easiest, no setup, may sleep)
- **Railway:** https://railway.app (good free tier)
- **Local:** `python quality_check_api.py` (for testing)

See `DEPLOYMENT_GUIDE.md` for detailed instructions.
