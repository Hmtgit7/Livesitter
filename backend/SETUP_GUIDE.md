# Livesitter Backend Setup Guide

This guide will help you set up the Livesitter backend API step by step.

## Prerequisites

Before starting, ensure you have the following installed:

1. **Python 3.8 or higher**
2. **MongoDB** (local or Atlas)
3. **FFmpeg** (for RTSP to HLS conversion)
4. **Git**

## Step 1: Environment Setup

### 1.1 Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 1.2 Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

### 1.3 Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your settings
# Use your preferred text editor
```

Edit the `.env` file with your configuration:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/livesitter
DATABASE_NAME=livesitter

# RTSP Stream Configuration
FFMPEG_PATH=ffmpeg
HLS_SEGMENT_DURATION=2
HLS_PLAYLIST_LENGTH=10
STREAM_TIMEOUT=30
MAX_STREAMS=5

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Rate Limiting
RATELIMIT_DEFAULT=100 per minute
```

## Step 2: Database Setup

### 2.1 Local MongoDB

**Install MongoDB:**

**Windows:**
1. Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Install and add to PATH
3. Start MongoDB service

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mongodb
sudo systemctl start mongod
sudo systemctl enable mongod
```

**Verify MongoDB is running:**
```bash
mongosh
# or
mongo
```

### 2.2 MongoDB Atlas (Cloud)

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a free cluster
3. Get your connection string
4. Update `MONGODB_URI` in `.env`:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/livesitter
```

## Step 3: FFmpeg Installation

### 3.1 Windows

1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add to PATH environment variable
4. Verify installation:
```bash
ffmpeg -version
```

### 3.2 macOS

```bash
brew install ffmpeg
ffmpeg -version
```

### 3.3 Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version
```

## Step 4: Start the Application

### 4.1 Quick Start

```bash
# Make sure virtual environment is activated
python run.py
```

### 4.2 Alternative Start Methods

```bash
# Method 1: Direct app.py
python app.py

# Method 2: Flask CLI
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

## Step 5: Verify Installation

### 5.1 Health Check

Open your browser or use curl:

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "active_streams": 0,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 5.2 API Documentation

Visit: http://localhost:5000/api/docs

### 5.3 Run Test Script

```bash
# Install requests if not already installed
pip install requests

# Run test script
python test_api.py
```

## Step 6: Testing RTSP Streams

### 6.1 Test RTSP Sources

For testing, use these RTSP sources:

- `rtsp://rtsp.stream/pattern` - Test pattern
- `rtsp://rtsp.stream/movie` - Sample movie
- `rtsp://rtsp.stream/beach` - Beach scene

### 6.2 Create Test Stream

```bash
curl -X POST http://localhost:5000/api/streams \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Stream",
    "rtsp_url": "rtsp://rtsp.stream/pattern",
    "settings": {
      "quality": "medium",
      "fps": 30,
      "resolution": "720p"
    }
  }'
```

### 6.3 Start Stream

```bash
# Replace {stream_id} with the actual ID from the previous response
curl -X POST http://localhost:5000/api/streams/{stream_id}/start
```

## Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed

**Symptoms:**
- Health check shows "database": "disconnected"
- Error: "Failed to connect to MongoDB"

**Solutions:**
- Check if MongoDB is running: `mongosh` or `mongo`
- Verify connection string in `.env`
- For Atlas: Check network access and credentials

#### 2. FFmpeg Not Found

**Symptoms:**
- Stream start fails
- Error: "FFmpeg not found"

**Solutions:**
- Install FFmpeg and add to PATH
- Verify with: `ffmpeg -version`
- Update `FFMPEG_PATH` in `.env` if needed

#### 3. Port Already in Use

**Symptoms:**
- Error: "Address already in use"

**Solutions:**
- Change port in `.env`: `FLASK_PORT=5001`
- Kill existing process: `lsof -ti:5000 | xargs kill -9`

#### 4. CORS Errors (Frontend Integration)

**Symptoms:**
- Browser console shows CORS errors

**Solutions:**
- Update `CORS_ORIGINS` in `.env` with your frontend URL
- Restart the Flask application

#### 5. Stream Not Starting

**Symptoms:**
- Stream status remains "stopped" or "error"

**Solutions:**
- Check RTSP URL is accessible
- Verify FFmpeg can access the stream
- Check firewall settings
- Review application logs

### Debug Mode

Enable debug mode for detailed error messages:

```env
FLASK_DEBUG=True
```

### Logs

The application logs to stdout. Check for:
- Database connection errors
- Stream manager errors
- FFmpeg process errors

## Production Deployment

### 1. Environment Variables

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-strong-secret-key
```

### 2. MongoDB Atlas

Use MongoDB Atlas for production:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/livesitter
```

### 3. Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Process Manager (PM2)

```bash
npm install -g pm2
pm2 start run.py --name livesitter-backend
pm2 save
pm2 startup
```

## API Testing

### Using cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Create overlay
curl -X POST http://localhost:5000/api/overlays \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Overlay",
    "type": "text",
    "content": "Live Stream",
    "position": {"x": 10, "y": 10},
    "size": {"width": 200, "height": 50},
    "style": {
      "fontSize": 24,
      "color": "#ffffff",
      "fontFamily": "Arial"
    }
  }'

# Create stream
curl -X POST http://localhost:5000/api/streams \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Stream",
    "rtsp_url": "rtsp://rtsp.stream/pattern",
    "settings": {
      "quality": "medium",
      "fps": 30,
      "resolution": "720p"
    }
  }'
```

### Using Postman

1. Import the API collection
2. Set base URL: `http://localhost:5000`
3. Test endpoints

## Next Steps

1. **Frontend Integration**: Connect your React frontend to the API
2. **Authentication**: Implement user authentication
3. **File Upload**: Add overlay image upload functionality
4. **WebSocket**: Add real-time stream status updates
5. **Monitoring**: Add application monitoring and logging

## Support

If you encounter issues:

1. Check the logs for error messages
2. Verify all prerequisites are installed
3. Test individual components (MongoDB, FFmpeg)
4. Review the API documentation
5. Run the test script to verify functionality

## Files Overview

```
backend/
├── app.py                 # Main Flask application
├── run.py                 # Run script
├── test_api.py           # API test script
├── requirements.txt       # Python dependencies
├── env.example           # Environment template
├── README.md             # Main documentation
├── API_DOCUMENTATION.md  # Detailed API docs
├── SETUP_GUIDE.md        # This file
├── config/               # Configuration
├── models/               # Data models
├── routes/               # API routes
└── utils/                # Utilities
``` 