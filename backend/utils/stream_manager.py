import subprocess
import os
import threading
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from config.settings import Config

logger = logging.getLogger(__name__)

class StreamManager:
    """Manages RTSP to HLS stream conversion"""
    
    def __init__(self, config: Config):
        self.config = config
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.stream_lock = threading.Lock()
        
        # Log config attributes for debugging
        logger.info(f"StreamManager initialized with config: MAX_STREAMS={getattr(config, 'MAX_STREAMS', 'NOT_FOUND')}, FFMPEG_PATH={getattr(config, 'FFMPEG_PATH', 'NOT_FOUND')}")
        
        # Create streams directory if it doesn't exist
        self.streams_dir = os.path.join(os.getcwd(), 'streams')
        os.makedirs(self.streams_dir, exist_ok=True)
    
    def start_stream(self, stream_id: str, rtsp_url: str, settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start RTSP to HLS conversion"""
        with self.stream_lock:
            if stream_id in self.active_streams:
                return {'success': False, 'error': 'Stream already running'}
            
            # Check if MAX_STREAMS attribute exists, default to 5 if not
            max_streams = getattr(self.config, 'MAX_STREAMS', 5)
            logger.info(f"Starting stream {stream_id}, current streams: {len(self.active_streams)}, max: {max_streams}")
            if len(self.active_streams) >= max_streams:
                return {'success': False, 'error': 'Maximum streams reached'}
            
            # Default settings
            default_settings = {
                'quality': 'medium',
                'fps': 30,
                'resolution': '720p',
                'bitrate': '1000k'
            }
            if settings:
                default_settings.update(settings)
            
            # Create stream directory
            stream_dir = os.path.join(self.streams_dir, stream_id)
            os.makedirs(stream_dir, exist_ok=True)
            
            # Generate HLS URL - include full API path
            hls_url = f"/api/streams/streams/{stream_id}/playlist.m3u8"
            
            try:
                # Build FFmpeg command
                ffmpeg_cmd = self._build_ffmpeg_command(
                    rtsp_url, stream_dir, default_settings
                )
                
                # Start FFmpeg process
                process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
                
                # Store stream info
                self.active_streams[stream_id] = {
                    'process': process,
                    'rtsp_url': rtsp_url,
                    'hls_url': hls_url,
                    'stream_dir': stream_dir,
                    'settings': default_settings,
                    'started_at': datetime.utcnow(),
                    'status': 'starting'
                }
                
                # Start monitoring thread
                monitor_thread = threading.Thread(
                    target=self._monitor_stream,
                    args=(stream_id,),
                    daemon=True
                )
                monitor_thread.start()
                
                logger.info(f"Started stream {stream_id} with RTSP URL: {rtsp_url}")
                return {
                    'success': True,
                    'stream_id': stream_id,
                    'hls_url': hls_url,
                    'status': 'starting'
                }
                
            except Exception as e:
                logger.error(f"Failed to start stream {stream_id}: {e}")
                return {'success': False, 'error': str(e)}
    
    def stop_stream(self, stream_id: str) -> Dict[str, Any]:
        """Stop RTSP to HLS conversion"""
        with self.stream_lock:
            if stream_id not in self.active_streams:
                return {'success': False, 'error': 'Stream not found'}
            
            stream_info = self.active_streams[stream_id]
            process = stream_info['process']
            
            try:
                # Terminate FFmpeg process
                process.terminate()
                
                # Wait for process to terminate
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                # Clean up
                del self.active_streams[stream_id]
                
                logger.info(f"Stopped stream {stream_id}")
                return {'success': True, 'stream_id': stream_id}
                
            except Exception as e:
                logger.error(f"Failed to stop stream {stream_id}: {e}")
                return {'success': False, 'error': str(e)}
    
    def get_stream_status(self, stream_id: str) -> Dict[str, Any]:
        """Get stream status"""
        with self.stream_lock:
            if stream_id not in self.active_streams:
                return {'exists': False}
            
            stream_info = self.active_streams[stream_id]
            process = stream_info['process']
            
            return {
                'exists': True,
                'status': stream_info['status'],
                'rtsp_url': stream_info['rtsp_url'],
                'hls_url': stream_info['hls_url'],
                'started_at': stream_info['started_at'].isoformat(),
                'process_alive': process.poll() is None
            }
    
    def get_all_streams(self) -> List[Dict[str, Any]]:
        """Get all active streams"""
        with self.stream_lock:
            streams = []
            for stream_id, stream_info in self.active_streams.items():
                streams.append({
                    'stream_id': stream_id,
                    'status': stream_info['status'],
                    'rtsp_url': stream_info['rtsp_url'],
                    'hls_url': stream_info['hls_url'],
                    'started_at': stream_info['started_at'].isoformat()
                })
            return streams
    
    def _build_ffmpeg_command(self, rtsp_url: str, stream_dir: str, settings: Dict[str, Any]) -> str:
        """Build FFmpeg command for RTSP to HLS conversion"""
        
        # Resolution mapping
        resolution_map = {
            '480p': '854:480',
            '720p': '1280:720',
            '1080p': '1920:1080'
        }
        
        # Quality settings
        quality_settings = {
            'low': {'bitrate': '500k', 'crf': 28},
            'medium': {'bitrate': '1000k', 'crf': 23},
            'high': {'bitrate': '2000k', 'crf': 18}
        }
        
        quality = settings.get('quality', 'medium')
        fps = settings.get('fps', 30)
        resolution = settings.get('resolution', '720p')
        bitrate = settings.get('bitrate', quality_settings[quality]['bitrate'])
        crf = quality_settings[quality]['crf']
        
        # Build command with fallback values for config attributes
        ffmpeg_path = getattr(self.config, 'FFMPEG_PATH', 'ffmpeg')
        hls_segment_duration = getattr(self.config, 'HLS_SEGMENT_DURATION', 2)
        hls_playlist_length = getattr(self.config, 'HLS_PLAYLIST_LENGTH', 10)
        
        cmd = [
            ffmpeg_path,
            '-i', rtsp_url,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', str(crf),
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'hls',
            '-hls_time', str(hls_segment_duration),
            '-hls_list_size', str(hls_playlist_length),
            '-hls_flags', 'delete_segments',
            '-hls_segment_filename', os.path.join(stream_dir, 'segment_%03d.ts'),
            '-vf', f'scale={resolution_map[resolution]},fps={fps}',
            os.path.join(stream_dir, 'playlist.m3u8')
        ]
        
        return ' '.join(cmd)
    
    def _monitor_stream(self, stream_id: str) -> None:
        """Monitor stream process and update status"""
        stream_info = self.active_streams.get(stream_id)
        if not stream_info:
            return
        
        process = stream_info['process']
        
        # Wait a bit for process to start
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            stream_info['status'] = 'running'
        else:
            stream_info['status'] = 'error'
            logger.error(f"Stream {stream_id} process terminated unexpectedly")
        
        # Monitor process
        while stream_id in self.active_streams:
            if process.poll() is not None:
                stream_info['status'] = 'stopped'
                logger.info(f"Stream {stream_id} process ended")
                break
            time.sleep(5)
    
    def cleanup_streams(self) -> None:
        """Clean up stopped streams"""
        with self.stream_lock:
            stopped_streams = []
            for stream_id, stream_info in self.active_streams.items():
                if stream_info['process'].poll() is not None:
                    stopped_streams.append(stream_id)
            
            for stream_id in stopped_streams:
                del self.active_streams[stream_id]
                logger.info(f"Cleaned up stopped stream {stream_id}")

# Global stream manager instance
stream_manager: Optional[StreamManager] = None

def init_stream_manager(config: Config) -> StreamManager:
    """Initialize stream manager"""
    global stream_manager
    try:
        stream_manager = StreamManager(config)
        logger.info("Stream manager initialized successfully")
        return stream_manager
    except Exception as e:
        logger.error(f"Failed to initialize stream manager: {e}")
        raise

def get_stream_manager() -> StreamManager:
    """Get stream manager instance"""
    if stream_manager is None:
        raise Exception("Stream manager not initialized")
    return stream_manager 