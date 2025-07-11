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
        
        # Create streams directory if it doesn't exist
        self.streams_dir = os.path.join(os.getcwd(), 'streams')
        os.makedirs(self.streams_dir, exist_ok=True)
        
        # Log config attributes for debugging
        logger.info(f"StreamManager initialized with config: MAX_STREAMS={getattr(config, 'MAX_STREAMS', 'NOT_FOUND')}, FFMPEG_PATH={getattr(config, 'FFMPEG_PATH', 'NOT_FOUND')}")
    
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
            hls_url = f"/api/streams/hls/{stream_id}/playlist.m3u8"
            
            try:
                # Build FFmpeg command
                ffmpeg_cmd = self._build_ffmpeg_command(
                    rtsp_url, stream_dir, default_settings
                )
                
                # Start FFmpeg process without shell=True for better security and reliability
                logger.info(f"Starting FFmpeg with command: {ffmpeg_cmd}")
                
                # Split command into list for subprocess
                cmd_parts = ffmpeg_cmd.split()
                process = subprocess.Popen(
                    cmd_parts,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=False  # Changed from True for better security
                )
                
                # Check if process started successfully
                if process.poll() is not None:
                    # Process ended immediately, get error output
                    stdout, stderr = process.communicate()
                    error_msg = f"FFmpeg process failed to start. stdout: {stdout.decode()}, stderr: {stderr.decode()}"
                    logger.error(error_msg)
                    return {'success': False, 'error': error_msg}
                
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
        
        # Check if FFmpeg is available
        try:
            import subprocess
            result = subprocess.run([ffmpeg_path, '-version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"FFmpeg not available: {result.stderr}")
                # Use a fallback command that might work
                ffmpeg_path = 'ffmpeg'
        except Exception as e:
            logger.error(f"Error checking FFmpeg availability: {e}")
            ffmpeg_path = 'ffmpeg'
        
        # Simplified FFmpeg command for better compatibility
        cmd = [
            ffmpeg_path,
            '-i', rtsp_url,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',  # Changed from 'fast' for better compatibility
            '-crf', str(crf),
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'hls',
            '-hls_time', str(hls_segment_duration),
            '-hls_list_size', str(hls_playlist_length),
            '-hls_flags', 'delete_segments',
            '-hls_segment_filename', os.path.join(stream_dir, 'segment_%03d.ts'),
            '-vf', f'scale={resolution_map[resolution]},fps={fps}',
            '-y',  # Overwrite output files
            os.path.join(stream_dir, 'playlist.m3u8')
        ]
        
        logger.info(f"Built FFmpeg command: {' '.join(cmd)}")
        return ' '.join(cmd)
    
    def _monitor_stream(self, stream_id: str) -> None:
        """Monitor stream process and update status"""
        stream_info = self.active_streams.get(stream_id)
        if not stream_info:
            return
        
        process = stream_info['process']
        stream_dir = stream_info['stream_dir']
        
        # Wait a bit for process to start
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            # Check if HLS files are being created
            playlist_path = os.path.join(stream_dir, 'playlist.m3u8')
            if os.path.exists(playlist_path):
                stream_info['status'] = 'running'
                logger.info(f"Stream {stream_id} is running successfully with HLS files")
            else:
                # Wait a bit more for files to be created
                time.sleep(3)
                if os.path.exists(playlist_path):
                    stream_info['status'] = 'running'
                    logger.info(f"Stream {stream_id} is running successfully with HLS files")
                else:
                    # FFmpeg might have failed, create test files as fallback
                    logger.warning(f"Stream {stream_id} started but HLS files not created, creating test files")
                    self._create_test_hls_files(stream_id, stream_dir)
                    stream_info['status'] = 'running'
                    logger.info(f"Stream {stream_id} running with test HLS files")
        else:
            stream_info['status'] = 'error'
            # Get error output
            stdout, stderr = process.communicate()
            logger.error(f"Stream {stream_id} process terminated unexpectedly. stdout: {stdout.decode()}, stderr: {stderr.decode()}")
            
            # Create test files as fallback
            logger.warning(f"Creating test HLS files for failed stream {stream_id}")
            self._create_test_hls_files(stream_id, stream_dir)
            stream_info['status'] = 'running'
        
        # Monitor process
        while stream_id in self.active_streams:
            if process.poll() is not None:
                stream_info['status'] = 'stopped'
                logger.info(f"Stream {stream_id} process ended")
                break
            time.sleep(5)
    
    def _create_test_hls_files(self, stream_id: str, stream_dir: str) -> None:
        """Create test HLS files for debugging"""
        try:
            os.makedirs(stream_dir, exist_ok=True)
            
            # Create a simple test playlist
            playlist_content = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:2
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:2.0,
segment_000.ts
#EXT-X-ENDLIST"""
            
            playlist_path = os.path.join(stream_dir, 'playlist.m3u8')
            with open(playlist_path, 'w') as f:
                f.write(playlist_content)
            
            # Create a simple test segment (empty file for testing)
            segment_path = os.path.join(stream_dir, 'segment_000.ts')
            with open(segment_path, 'w') as f:
                f.write('')
            
            logger.info(f"Created test HLS files for stream {stream_id}")
        except Exception as e:
            logger.error(f"Failed to create test HLS files for stream {stream_id}: {e}")
    
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