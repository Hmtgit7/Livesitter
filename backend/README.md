# Livesitter Backend API

A Flask-based REST API for managing RTSP livestreams with custom overlay functionality.

## Features

- **RTSP to HLS Conversion**: Convert RTSP streams to HLS format for browser compatibility
- **Overlay Management**: Full CRUD operations for custom overlays (text, images, logos)
- **Stream Management**: Create, start, stop, and monitor RTSP streams
- **Real-time Monitoring**: Health checks and stream status monitoring
- **Rate Limiting**: Built-in rate limiting for API protection
- **CORS Support**: Cross-origin resource sharing for frontend integration

## Tech Stack

- **Python 3.8+**
- **Flask**: Web framework
- **MongoDB**: Database
- **FFmpeg**: RTSP to HLS conversion
- **Flask-CORS**: Cross-origin support
- **Flask-Limiter**: Rate limiting

## Prerequisites

1. **Python 3.8 or higher**
2. **MongoDB** (local or Atlas)
3. **FFmpeg** installed and accessible in PATH
4. **Git**

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Livesitter/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

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
```

### 5. Start MongoDB

**Local MongoDB:**
```bash
# Start MongoDB service
mongod
```

**MongoDB Atlas:**
- Create a cluster at [MongoDB Atlas](https://cloud.mongodb.com)
- Get your connection string and update `MONGODB_URI`

### 6. Install FFmpeg

**Windows:**
```bash
# Download from https://ffmpeg.org/download.html
# Add to PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 7. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Documentation

### Base URL
```
http://localhost:5000
```

### Authentication
Currently, the API uses a simple user_id system. Set `user_id` in requests or use `default`.

### Endpoints

#### Health Checks

**GET /api/health**
- Overall health check
- Returns database and stream status

**GET /api/health/database**
- Database connection health

**GET /api/health/streams**
- Active streams status

#### Overlays API

**GET /api/overlays**
- Get all overlays with pagination
- Query parameters: `page`, `limit`, `user_id`

**GET /api/overlays/{id}**
- Get specific overlay by ID

**POST /api/overlays**
- Create new overlay
- Body: Overlay data

**PUT /api/overlays/{id}**
- Update existing overlay
- Body: Overlay data

**DELETE /api/overlays/{id}**
- Delete overlay

**POST /api/overlays/batch**
- Create multiple overlays
- Body: `{"overlays": [...], "user_id": "default"}`

#### Streams API

**GET /api/streams**
- Get all streams
- Query parameters: `user_id`

**GET /api/streams/{id}**
- Get specific stream with current status

**POST /api/streams**
- Create new stream
- Body: Stream data

**PUT /api/streams/{id}**
- Update existing stream
- Body: Stream data

**DELETE /api/streams/{id}**
- Delete stream (stops if running)

**POST /api/streams/{id}/start**
- Start RTSP to HLS conversion

**POST /api/streams/{id}/stop**
- Stop stream conversion

**GET /api/streams/{id}/status**
- Get current stream status

**GET /api/streams/active**
- Get all active streams

## Data Models

### Overlay Model

```json
{
  "_id": "string",
  "user_id": "string",
  "name": "string",
  "type": "text|image|logo",
  "content": "string",
  "position": {
    "x": "number",
    "y": "number"
  },
  "size": {
    "width": "number",
    "height": "number"
  },
  "style": {
    "fontSize": "number",
    "color": "string",
    "fontFamily": "string",
    "opacity": "number",
    "backgroundColor": "string",
    "borderColor": "string",
    "borderWidth": "number"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Stream Model

```json
{
  "_id": "string",
  "user_id": "string",
  "name": "string",
  "rtsp_url": "string",
  "hls_url": "string",
  "status": "stopped|running|error",
  "is_active": "boolean",
  "overlay_ids": ["string"],
  "settings": {
    "quality": "low|medium|high",
    "fps": "number",
    "resolution": "480p|720p|1080p",
    "bitrate": "string"
  },
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_started": "datetime",
  "last_stopped": "datetime"
}
```

## Usage Examples

### Create an Overlay

```bash
curl -X POST http://localhost:5000/api/overlays \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Logo",
    "type": "logo",
    "content": "https://example.com/logo.png",
    "position": {"x": 10, "y": 10},
    "size": {"width": 100, "height": 50},
    "style": {
      "opacity": 0.8,
      "backgroundColor": "transparent"
    }
  }'
```

### Create a Stream

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

### Start a Stream

```bash
curl -X POST http://localhost:5000/api/streams/{stream_id}/start
```

### Get Stream Status

```bash
curl http://localhost:5000/api/streams/{stream_id}/status
```

## RTSP Stream Sources

For testing, you can use these RTSP sources:

- `rtsp://rtsp.stream/pattern` - Test pattern
- `rtsp://rtsp.stream/movie` - Sample movie
- `rtsp://rtsp.stream/beach` - Beach scene

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "error": "Error message",
  "details": ["validation errors"]
}
```

## Rate Limiting

- Default: 100 requests per minute per IP
- Configurable via environment variables

## CORS Configuration

- Default origins: `http://localhost:3000`, `http://localhost:5173`
- Configurable via `CORS_ORIGINS` environment variable

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Running Tests

```bash
# TODO: Add test suite
python -m pytest tests/
```

### Code Structure

```
backend/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── env.example           # Environment template
├── config/               # Configuration
│   ├── __init__.py
│   └── settings.py
├── models/               # Data models
│   ├── __init__.py
│   ├── overlay.py
│   └── stream.py
├── routes/               # API routes
│   ├── __init__.py
│   ├── overlays.py
│   ├── streams.py
│   └── health.py
└── utils/                # Utilities
    ├── __init__.py
    ├── database.py
    ├── stream_manager.py
    └── validators.py
```

## Deployment

### Production Configuration

1. Set `FLASK_ENV=production`
2. Use strong `SECRET_KEY`
3. Configure MongoDB Atlas or production MongoDB
4. Set up proper CORS origins
5. Use reverse proxy (nginx) for production

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check MongoDB is running
   - Verify connection string in `.env`

2. **FFmpeg Not Found**
   - Install FFmpeg and add to PATH
   - Verify with `ffmpeg -version`

3. **Stream Not Starting**
   - Check RTSP URL is accessible
   - Verify FFmpeg can access the stream
   - Check firewall settings

4. **CORS Errors**
   - Verify frontend URL in `CORS_ORIGINS`
   - Check browser console for errors

### Logs

The application logs to stdout. Check for:
- Database connection errors
- Stream manager errors
- FFmpeg process errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license here] 