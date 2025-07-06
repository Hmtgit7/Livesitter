import axios from 'axios';

// API base configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Types
export interface Overlay {
  _id?: string;
  user_id?: string;
  name: string;
  type: 'text' | 'image' | 'logo';
  content: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  style: {
    fontSize?: number;
    color?: string;
    fontFamily?: string;
    opacity?: number;
    backgroundColor?: string;
    borderColor?: string;
    borderWidth?: number;
  };
  created_at?: string;
  updated_at?: string;
}

export interface Stream {
  _id?: string;
  user_id?: string;
  name: string;
  rtsp_url: string;
  hls_url?: string;
  status: 'stopped' | 'running' | 'error';
  is_active?: boolean;
  overlay_ids?: string[];
  settings: {
    quality: 'low' | 'medium' | 'high';
    fps: number;
    resolution: '480p' | '720p' | '1080p';
    bitrate?: string;
  };
  created_at?: string;
  updated_at?: string;
  last_started?: string;
  last_stopped?: string;
  current_status?: {
    exists: boolean;
    status: string;
    rtsp_url: string;
    hls_url: string;
    started_at: string;
    process_alive: boolean;
  };
}

export interface StreamStatus {
  exists: boolean;
  status: string;
  rtsp_url: string;
  hls_url: string;
  started_at: string;
  process_alive: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  details?: string[];
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

// Health API
export const healthApi = {
  check: () => api.get<ApiResponse<any>>('/api/health'),
  database: () => api.get<ApiResponse<any>>('/api/health/database'),
  streams: () => api.get<ApiResponse<any>>('/api/health/streams'),
};

// Overlays API
export const overlaysApi = {
  getAll: (params?: { page?: number; limit?: number; user_id?: string }) =>
    api.get<PaginatedResponse<Overlay>>('/api/overlays', { params }),
  
  getById: (id: string) =>
    api.get<ApiResponse<Overlay>>(`/api/overlays/${id}`),
  
  create: (overlay: Omit<Overlay, '_id' | 'created_at' | 'updated_at'>) =>
    api.post<ApiResponse<Overlay>>('/api/overlays', overlay),
  
  update: (id: string, overlay: Partial<Overlay>) =>
    api.put<ApiResponse<Overlay>>(`/api/overlays/${id}`, overlay),
  
  delete: (id: string) =>
    api.delete<ApiResponse<void>>(`/api/overlays/${id}`),
  
  createBatch: (overlays: Omit<Overlay, '_id' | 'created_at' | 'updated_at'>[], user_id?: string) =>
    api.post<ApiResponse<Overlay[]>>('/api/overlays/batch', { overlays, user_id }),
};

// Streams API
export const streamsApi = {
  getAll: (params?: { user_id?: string }) =>
    api.get<ApiResponse<Stream[]>>('/api/streams', { params }),
  
  getById: (id: string) =>
    api.get<ApiResponse<Stream>>(`/api/streams/${id}`),
  
  create: (stream: Omit<Stream, '_id' | 'created_at' | 'updated_at' | 'last_started' | 'last_stopped'>) =>
    api.post<ApiResponse<Stream>>('/api/streams', stream),
  
  update: (id: string, stream: Partial<Stream>) =>
    api.put<ApiResponse<Stream>>(`/api/streams/${id}`, stream),
  
  delete: (id: string) =>
    api.delete<ApiResponse<void>>(`/api/streams/${id}`),
  
  start: (id: string) =>
    api.post<ApiResponse<{ stream_id: string; hls_url: string; status: string }>>(`/api/streams/${id}/start`),
  
  stop: (id: string) =>
    api.post<ApiResponse<void>>(`/api/streams/${id}/stop`),
  
  getStatus: (id: string) =>
    api.get<ApiResponse<StreamStatus>>(`/api/streams/${id}/status`),
  
  getActive: () =>
    api.get<ApiResponse<Stream[]>>('/api/streams/active'),
};

// Utility functions
export const apiUtils = {
  // Convert frontend overlay format to API format
  convertOverlayToApi: (overlay: any): Omit<Overlay, '_id' | 'created_at' | 'updated_at'> => ({
    name: overlay.name || 'Untitled Overlay',
    type: overlay.type,
    content: overlay.content,
    position: overlay.position,
    size: overlay.size,
    style: {
      fontSize: overlay.style?.fontSize || 16,
      color: overlay.style?.color || '#ffffff',
      fontFamily: overlay.style?.fontFamily || 'Arial',
      opacity: overlay.style?.opacity || 1.0,
      backgroundColor: overlay.style?.backgroundColor || 'transparent',
      borderColor: overlay.style?.borderColor || 'transparent',
      borderWidth: overlay.style?.borderWidth || 0,
    },
  }),

  // Convert API overlay format to frontend format
  convertOverlayFromApi: (overlay: Overlay): any => ({
    id: overlay._id,
    name: overlay.name,
    type: overlay.type,
    content: overlay.content,
    position: overlay.position,
    size: overlay.size,
    style: overlay.style,
    visible: true, // Frontend specific
  }),

  // Convert frontend stream format to API format
  convertStreamToApi: (stream: any): Omit<Stream, '_id' | 'created_at' | 'updated_at' | 'last_started' | 'last_stopped'> => ({
    name: stream.name,
    rtsp_url: stream.rtsp_url,
    settings: {
      quality: stream.settings?.quality || 'medium',
      fps: stream.settings?.fps || 30,
      resolution: stream.settings?.resolution || '720p',
      bitrate: stream.settings?.bitrate || '1000k',
    },
  }),

  // Convert API stream format to frontend format
  convertStreamFromApi: (stream: Stream): any => ({
    id: stream._id,
    name: stream.name,
    rtsp_url: stream.rtsp_url,
    hls_url: stream.hls_url,
    status: stream.status,
    settings: stream.settings,
    is_active: stream.is_active,
  }),
};

export default api; 