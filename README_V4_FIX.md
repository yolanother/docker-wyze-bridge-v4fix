# 🎯 Wyze Cam v4 Fix - Quick Start Guide

## Problem
Wyze Cam v4 cameras stopped working after the February 2025 firmware update.

## Solution
This repository contains a **tested fix** that restores v4 camera functionality while maintaining full backwards compatibility.

## Quick Deployment

### 1. Clone and Setup
```bash
git clone <your-repo>
cd docker-wyze-bridge

# Create your .env file with Wyze credentials
cp .env.example .env
# Edit .env with your WYZE_EMAIL, WYZE_PASSWORD, API_ID, API_KEY
```

### 2. Deploy with Fix
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Or for testing/debugging  
docker-compose up -d
```

### 3. Verify Fix Working
```bash
# Check logs for v4 fix messages
docker-compose logs | grep "V4 FIX"

# Check camera status
curl http://localhost:5000/api/sse_status
```

## Expected Results

### ✅ Success Indicators
- Logs show: `🔧 [V4 FIX] Camera_Name - Using forced parallel connection for v4 camera`
- v4 cameras show "connecting" or "connected" status (not "stopped")
- Older cameras continue working normally

### ❌ If Still Not Working
1. Check `.env` file has valid Wyze credentials
2. Ensure cameras are online and accessible on your network
3. Check Docker logs for specific error messages

## What This Fix Does

- **Targets**: Only Wyze Cam v4 (HL_CAM4) cameras
- **Change**: Forces v4 cameras to use parallel connection instead of DTLS auth
- **Impact**: Zero impact on other camera models
- **Safety**: 100% backwards compatible

## Files Changed
- `wyze_v4_fix.py` - The fix implementation
- `Dockerfile.v4fix` - Docker build with fix
- `docker-compose.prod.yml` - Production deployment

## Need Help?

See `WYZE_V4_FIX_CHANGELOG.md` for detailed technical information.
