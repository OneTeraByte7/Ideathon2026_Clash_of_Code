# 🔧 Render Deployment Troubleshooting

## Issue: pydantic-core Build Failure (Rust Compilation)

### Problem
```
error: failed to create directory `/usr/local/cargo/registry/cache/index.crates.io-1949cf8c6b5b557f`
Caused by: Read-only file system (os error 30)
💥 maturin failed
```

### Solutions

#### Solution 1: Use Compatible Requirements (Recommended)
The updated `requirements.txt` uses older, stable versions that don't require Rust compilation:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
motor==3.3.2
pydantic==2.5.2
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.25.2
python-multipart==0.0.6
apscheduler==3.10.4
requests==2.31.0
beanie==1.20.0
google-generativeai==0.3.2
```

#### Solution 2: Alternative Render Configuration
Update your `render.yaml`:

```yaml
services:
  - type: web
    name: asclepius-api
    env: python
    plan: free
    buildCommand: cd server && pip install --upgrade pip && pip install -r requirements.txt
    startCommand: cd server && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.7
      - key: PIP_NO_CACHE_DIR
        value: 1
      - key: PIP_DISABLE_PIP_VERSION_CHECK
        value: 1
```

#### Solution 3: Manual Render Setup (If yaml fails)

1. **Go to Render Dashboard**
2. **Create New Web Service**
3. **Configure manually**:
   ```
   Build Command: cd server && pip install --upgrade pip && pip install -r requirements.txt
   Start Command: cd server && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
4. **Environment Variables**:
   - `PYTHON_VERSION` = `3.11.7`
   - `PIP_NO_CACHE_DIR` = `1`
   - Add your other environment variables

#### Solution 4: Use Docker (Advanced)
If builds continue to fail, use Docker deployment:

Create `Dockerfile` in server directory:
```dockerfile
FROM python:3.11.7-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 10000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
```

## Alternative Platforms

### If Render continues to fail, try these alternatives:

#### 1. Railway.app (Recommended Alternative)
```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "cd server && python -m uvicorn main:app --host 0.0.0.0 --port $PORT"
```

#### 2. Fly.io
```dockerfile
# fly.toml
app = "asclepius-api"

[build]
  image = "python:3.11.7-slim"

[[services]]
  internal_port = 8000
  protocol = "tcp"
```

#### 3. Heroku (with Procfile)
```
# Procfile
web: cd server && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Quick Deployment Test

After fixing requirements, test locally first:

```bash
# Test locally
cd server
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Test endpoint
curl http://localhost:8000/health
```

## Common Build Issues & Fixes

### Issue: Python Version Mismatch
**Fix**: Set `PYTHON_VERSION=3.11.7` in environment variables

### Issue: Pip Cache Issues  
**Fix**: Set `PIP_NO_CACHE_DIR=1`

### Issue: Memory Limit Exceeded
**Fix**: Use free tier with smaller dependencies

### Issue: Build Timeout
**Fix**: Reduce dependencies, use pre-compiled wheels

## Successful Build Indicators

✅ **Success messages to look for**:
```
✅ MongoDB connected and Beanie initialized
==> Build successful 🎉
==> Deploying...
==> Deploy successful 🎉
```

## Final Fallback: Minimal API

If all else fails, here's a minimal working `requirements.txt`:

```txt
fastapi==0.104.1
uvicorn==0.24.0
motor==3.3.2
pydantic==2.5.2
python-dotenv==1.0.0
requests==2.31.0
```

This removes Beanie but you'll need to use raw MongoDB operations.

---

## Next Steps After Successful Deploy

1. ✅ Check deployment logs for "Deploy successful"
2. ✅ Test health endpoint: `https://your-app.onrender.com/health`
3. ✅ Update Vercel environment variable with your Render URL
4. ✅ Deploy frontend to Vercel

**Need more help?** Check the main deployment guide or create an issue on GitHub.