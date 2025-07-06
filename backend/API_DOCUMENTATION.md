# Livesitter API Documentation

## Overview

The Livesitter API provides endpoints for managing RTSP livestreams with custom overlay functionality. The API is RESTful and returns JSON responses.

**Base URL:** `http://localhost:5000`

## Authentication

Currently, the API uses a simple user_id system. Include `user_id` in requests or use `default`.

## Response Format

All API responses follow this format:

```json
{
  "success": true|false,
  "data": {...},
  "message": "Success message",
  "error": "Error message",
  "details": ["validation errors"]
}
```

## Endpoints

### Health Checks

#### GET /api/health

Overall health check for the application.

**Response:**
```json
{
  "status": "healthy|unhealthy",
  "database": "connected|disconnected",
  "active_streams": 2,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### GET /api/health/database

Database connection health check.

**Response:**
```json
{
  "status": "healthy|unhealthy",
  "database": "connected|disconnected"
}
```

#### GET /api/health/streams

Active streams health check.

**Response:**
```json
{
  "status": "healthy",
  "active_streams": 2,
  "streams": [
    {
      "stream_id": "507f1f77bcf86cd799439011",
      "status": "running",
      "rtsp_url": "rtsp://rtsp.stream/pattern",
      "hls_url": "/streams/507f1f77bcf86cd799439011/playlist.m3u8",
      "started_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Overlays API

#### GET /api/overlays

Get all overlays with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10, max: 100)
- `user_id` (optional): User ID (default: "default")

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "user_id": "default",
      "name": "My Logo",
      "type": "logo",
      "content": "https://example.com/logo.png",
      "position": {"x": 10, "y": 10},
      "size": {"width": 100, "height": 50},
      "style": {
        "fontSize": 16,
        "color": "#ffffff",
        "fontFamily": "Arial",
        "opacity": 1.0,
        "backgroundColor": "transparent",
        "borderColor": "transparent",
        "borderWidth": 0
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "pages": 3
  }
}
```

#### GET /api/overlays/{id}

Get a specific overlay by ID.

**Path Parameters:**
- `id`: Overlay ID (MongoDB ObjectId)

**Response:**
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "user_id": "default",
    "name": "My Logo",
    "type": "logo",
    "content": "https://example.com/logo.png",
    "position": {"x": 10, "y": 10},
    "size": {"width": 100, "height": 50},
    "style": {
      "fontSize": 16,
      "color": "#ffffff",
      "fontFamily": "Arial",
      "opacity": 1.0,
      "backgroundColor": "transparent",
      "borderColor": "transparent",
      "borderWidth": 0
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### POST /api/overlays

Create a new overlay.

**Request Body:**
```json
{
  "name": "My Logo",
  "type": "logo",
  "content": "https://example.com/logo.png",
  "position": {"x": 10, "y": 10},
  "size": {"width": 100, "height": 50},
  "style": {
    "fontSize": 16,
    "color": "#ffffff",
    "fontFamily": "Arial",
    "opacity": 1.0,
    "backgroundColor": "transparent",
    "borderColor": "transparent",
    "borderWidth": 0
  },
  "user_id": "default"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "user_id": "default",
    "name": "My Logo",
    "type": "logo",
    "content": "https://example.com/logo.png",
    "position": {"x": 10, "y": 10},
    "size": {"width": 100, "height": 50},
    "style": {
      "fontSize": 16,
      "color": "#ffffff",
      "fontFamily": "Arial",
      "opacity": 1.0,
      "backgroundColor": "transparent",
      "borderColor": "transparent",
      "borderWidth": 0
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "message": "Overlay created successfully"
}
```

#### PUT /api/overlays/{id}

Update an existing overlay.

**Path Parameters:**
- `id`: Overlay ID (MongoDB ObjectId)

**Request Body:** (same as POST)

**Response:**
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "user_id": "default",
    "name": "Updated Logo",
    "type": "logo",
    "content": "https://example.com/updated-logo.png",
    "position": {"x": 20, "y": 20},
    "size": {"width": 150, "height": 75},
    "style": {
      "fontSize": 18,
      "color": "#ffffff",
      "fontFamily": "Arial",
      "opacity": 0.9,
      "backgroundColor": "transparent",
      "borderColor": "transparent",
      "borderWidth": 0
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T01:00:00Z"
  },
  "message": "Overlay updated successfully"
}
```

#### DELETE /api/overlays/{id}

Delete an overlay.

**Path Parameters:**
- `id`: Overlay ID (MongoDB ObjectId)

**Response:**
```json
{
  "success": true,
  "message": "Overlay deleted successfully"
}
```

#### POST /api/overlays/batch

Create multiple overlays at once.

**Request Body:**
```json
{
  "overlays": [
    {
      "name": "Logo 1",
      "type": "logo",
      "content": "https://example.com/logo1.png",
      "position": {"x": 10, "y": 10},
      "size": {"width": 100, "height": 50},
      "style": {
        "fontSize": 16,
        "color": "#ffffff",
        "opacity": 1.0
      }
    },
    {
      "name": "Text 1",
      "type": "text",
      "content": "Live Stream",
      "position": {"x": 50, "y": 50},
      "size": {"width": 200, "height": 30},
      "style": {
        "fontSize": 24,
        "color": "#ffffff",
        "fontFamily": "Arial",
        "opacity": 1.0
      }
    }
  ],
  "user_id": "default"
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "name": "Logo 1",
      "type": "logo",
      // ... other fields
    },
    {
      "_id": "507f1f77bcf86cd799439012",
      "name": "Text 1",
      "type": "text",
      // ... other fields
    }
  ],
  "message": "Created 2 overlays successfully"
}
```

### Streams API

#### GET /api/streams

Get all streams.

**Query Parameters:**
- `user_id` (optional): User ID (default: "default")

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "user_id": "default",
      "name": "Test Stream",
      "rtsp_url": "rtsp://rtsp.stream/pattern",
      "hls_url": "/streams/507f1f77bcf86cd799439011/playlist.m3u8",
      "status": "running",
      "is_active": true,
      "overlay_ids": ["507f1f77bcf86cd799439012"],
      "settings": {
        "quality": "medium",
        "fps": 30,
        "resolution": "720p",
        "bitrate": "1000k"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "last_started": "2024-01-01T00:00:00Z",
      "last_stopped": null
    }
  ]
}
```

#### GET /api/streams/{id}

Get a specific stream with current status.

**Path Parameters:**
- `id`: Stream ID (MongoDB ObjectId)

**Response:**
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "user_id": "default",
    "name": "Test Stream",
    "rtsp_url": "rtsp://rtsp.stream/pattern",
    "hls_url": "/streams/507f1f77bcf86cd799439011/playlist.m3u8",
    "status": "running",
    "is_active": true,
    "overlay_ids": ["507f1f77bcf86cd799439012"],
    "settings": {
      "quality": "medium",
      "fps": 30,
      "resolution": "720p",
      "bitrate": "1000k"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "last_started": "2024-01-01T00:00:00Z",
    "last_stopped": null,
    "current_status": {
      "exists": true,
      "status": "running",
      "rtsp_url": "rtsp://rtsp.stream/pattern",
      "hls_url": "/streams/507f1f77bcf86cd799439011/playlist.m3u8",
      "started_at": "2024-01-01T00:00:00Z",
      "process_alive": true
    }
  }
}
```

#### POST /api/streams

Create a new stream.

**Request Body:**
```json
{
  "name": "Test Stream",
  "rtsp_url": "rtsp://rtsp.stream/pattern",
  "settings": {
    "quality": "medium",
    "fps": 30,
    "resolution": "720p",
    "bitrate": "1000k"
  },
  "user_id": "default"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "user_id": "default",
    "name": "Test Stream",
    "rtsp_url": "rtsp://rtsp.stream/pattern",
    "hls_url": "",
    "status": "stopped",
    "is_active": false,
    "overlay_ids": [],
    "settings": {
      "quality": "medium",
      "fps": 30,
      "resolution": "720p",
      "bitrate": "1000k"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "last_started": null,
    "last_stopped": null
  },
  "message": "Stream created successfully"
}
```

#### PUT /api/streams/{id}

Update an existing stream.

**Path Parameters:**
- `id`: Stream ID (MongoDB ObjectId)

**Request Body:** (same as POST)

**Response:**
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "user_id": "default",
    "name": "Updated Stream",
    "rtsp_url": "rtsp://rtsp.stream/movie",
    "hls_url": "/streams/507f1f77bcf86cd799439011/playlist.m3u8",
    "status": "running",
    "is_active": true,
    "overlay_ids": ["507f1f77bcf86cd799439012"],
    "settings": {
      "quality": "high",
      "fps": 60,
      "resolution": "1080p",
      "bitrate": "2000k"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T01:00:00Z",
    "last_started": "2024-01-01T00:00:00Z",
    "last_stopped": null
  },
  "message": "Stream updated successfully"
}
```

#### DELETE /api/streams/{id}

Delete a stream (stops if running).

**Path Parameters:**
- `id`: Stream ID (MongoDB ObjectId)

**Response:**
```json
{
  "success": true,
  "message": "Stream deleted successfully"
}
```

#### POST /api/streams/{id}/start

Start RTSP to HLS conversion.

**Path Parameters:**
- `id`: Stream ID (MongoDB ObjectId)

**Response:**
```json
{
  "success": true,
  "data": {
    "stream_id": "507f1f77bcf86cd799439011",
    "hls_url": "/streams/507f1f77bcf86cd799439011/playlist.m3u8",
    "status": "starting"
  },
  "message": "Stream started successfully"
}
```

#### POST /api/streams/{id}/stop

Stop stream conversion.

**Path Parameters:**
- `id`: Stream ID (MongoDB ObjectId)

**Response:**
```json
{
  "success": true,
  "message": "Stream stopped successfully"
}
```

#### GET /api/streams/{id}/status

Get current stream status.

**Path Parameters:**
- `id`: Stream ID (MongoDB ObjectId)

**Response:**
```json
{
  "success": true,
  "data": {
    "exists": true,
    "status": "running",
    "rtsp_url": "rtsp://rtsp.stream/pattern",
    "hls_url": "/streams/507f1f77bcf86cd799439011/playlist.m3u8",
    "started_at": "2024-01-01T00:00:00Z",
    "process_alive": true
  }
}
```

#### GET /api/streams/active

Get all active streams.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "stream_id": "507f1f77bcf86cd799439011",
      "status": "running",
      "rtsp_url": "rtsp://rtsp.stream/pattern",
      "hls_url": "/streams/507f1f77bcf86cd799439011/playlist.m3u8",
      "started_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## Data Models

### Overlay Types

1. **text**: Text overlay with customizable fonts and colors
2. **image**: Image overlay (URL to image)
3. **logo**: Logo overlay (URL to logo image)

### Stream Settings

- **quality**: `low`, `medium`, `high`
- **fps**: Frame rate (integer)
- **resolution**: `480p`, `720p`, `1080p`
- **bitrate**: Video bitrate (string, e.g., "1000k")

### Stream Status

- **stopped**: Stream is not running
- **running**: Stream is active and converting
- **error**: Stream encountered an error

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid data |
| 404 | Not Found - Resource not found |
| 405 | Method Not Allowed |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "details": [
    "Validation error 1",
    "Validation error 2"
  ]
}
```

## Rate Limiting

- Default: 100 requests per minute per IP
- Configurable via environment variables
- Rate limit headers included in responses

## CORS Headers

The API includes CORS headers for cross-origin requests:
- `Access-Control-Allow-Origin`
- `Access-Control-Allow-Methods`
- `Access-Control-Allow-Headers`

## Testing

### Test RTSP Sources

For testing, use these RTSP sources:
- `rtsp://rtsp.stream/pattern` - Test pattern
- `rtsp://rtsp.stream/movie` - Sample movie
- `rtsp://rtsp.stream/beach` - Beach scene

### Example cURL Commands

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

# Start stream
curl -X POST http://localhost:5000/api/streams/{stream_id}/start

# Get stream status
curl http://localhost:5000/api/streams/{stream_id}/status
```

## HLS Streaming

Once a stream is started, the HLS playlist is available at:
```
http://localhost:5000/streams/{stream_id}/playlist.m3u8
```

This can be used with video players like:
- HLS.js
- Video.js
- Native HTML5 video (with HLS.js)

## WebSocket Support

Future versions may include WebSocket support for real-time stream status updates. 