# Deployment Guide

Quick deployment options for the QR Code Transformation Tool.

## 🚀 Fastest Deployment Options

### Option 1: Docker (Recommended - ~2 minutes)

```bash
# Build and run
docker-compose up -d

# Or with Docker directly
docker build -t qr-transformer .
docker run -p 8000:8000 qr-transformer
```

**Time: ~2 minutes** (first time includes image build)

### Option 2: Railway.app (~3 minutes)

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Deploy: `railway up`
4. Done! Get your URL from Railway dashboard

**Time: ~3 minutes** (includes account setup)

### Option 3: Render.com (~5 minutes)

1. Go to https://render.com
2. New → Web Service
3. Connect your GitHub repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn web.app:app --host 0.0.0.0 --port $PORT`
5. Deploy!

**Time: ~5 minutes**

### Option 4: Heroku (~5 minutes)

```bash
# Install Heroku CLI
heroku create qr-transformer
git push heroku main
```

**Time: ~5 minutes**

### Option 5: Fly.io (~5 minutes)

```bash
# Install flyctl
fly launch
# Follow prompts
fly deploy
```

**Time: ~5 minutes**

## 📦 Production Configuration

For production, use a production ASGI server:

```bash
# Using gunicorn with uvicorn workers
pip install gunicorn
gunicorn web.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or uvicorn with production settings
uvicorn web.app:app --host 0.0.0.0 --port 8000 --workers 4 --no-access-log
```

## 🔧 Environment Variables

Optional environment variables:

- `PORT`: Server port (default: 8000)
- `WORKERS`: Number of worker processes (default: 1)
- `LOG_LEVEL`: Logging level (default: info)

## 📊 Performance Notes

- **First request**: May take 2-5 seconds (algorithm initialization)
- **Subsequent requests**: 200-500ms typical
- **Memory**: ~200-300MB per worker
- **CPU**: Moderate (ILP solver can be CPU-intensive)

## 🐳 Docker Production

```bash
# Build production image
docker build -t qr-transformer:prod .

# Run with multiple workers
docker run -p 8000:8000 -e WORKERS=4 qr-transformer:prod
```

## ☁️ Cloud Platform Comparison

| Platform | Setup Time | Free Tier | Ease |
|----------|-----------|-----------|------|
| Railway | 3 min | ✅ Yes | ⭐⭐⭐⭐⭐ |
| Render | 5 min | ✅ Yes | ⭐⭐⭐⭐ |
| Fly.io | 5 min | ✅ Yes | ⭐⭐⭐⭐ |
| Heroku | 5 min | ❌ No | ⭐⭐⭐ |
| Docker | 2 min | N/A | ⭐⭐⭐⭐⭐ |

## 🚨 Quick Start (Local Production)

```bash
# Install dependencies
pip install -r requirements.txt

# Run production server
cd web
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

**Time: ~30 seconds**

