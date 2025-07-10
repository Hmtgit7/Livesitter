import React, { useEffect, useRef, useState } from 'react';
import { Play, Loader2, AlertCircle, Volume2, VolumeX } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';

interface VideoPlayerProps {
  isStreaming: boolean;
  streamStatus: 'idle' | 'connecting' | 'playing' | 'error';
  rtspUrl: string;
  hlsUrl?: string;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ 
  isStreaming, 
  streamStatus, 
  rtspUrl,
  hlsUrl 
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(50);
  const [isHlsSupported, setIsHlsSupported] = useState(false);
  const [hlsInstance, setHlsInstance] = useState<any>(null);

  // Check HLS support
  useEffect(() => {
    const checkHlsSupport = async () => {
      try {
        // Try to import HLS.js dynamically
        const Hls = (await import('hls.js')).default;
        if (Hls.isSupported()) {
          setIsHlsSupported(true);
        }
      } catch (error) {
        console.warn('HLS.js not available, falling back to native HLS support');
        setIsHlsSupported(false);
      }
    };

    checkHlsSupport();
  }, []);

  // Initialize HLS stream
  useEffect(() => {
    if (!hlsUrl || !isStreaming || streamStatus !== 'playing') {
      return;
    }

    const initHlsStream = async () => {
      try {
        if (isHlsSupported) {
          const Hls = (await import('hls.js')).default;
          
          if (hlsInstance) {
            hlsInstance.destroy();
          }

          const hls = new Hls({
            debug: false,
            enableWorker: true,
            lowLatencyMode: true,
            backBufferLength: 90,
          });

          hls.loadSource(hlsUrl);
          hls.attachMedia(videoRef.current!);
          
          hls.on(Hls.Events.MANIFEST_PARSED, () => {
            if (videoRef.current) {
              videoRef.current.play();
            }
          });

          hls.on(Hls.Events.ERROR, (event, data) => {
            console.error('HLS Error:', data);
          });

          setHlsInstance(hls);
        } else if (videoRef.current?.canPlayType('application/vnd.apple.mpegurl')) {
          // Native HLS support (Safari)
          videoRef.current.src = hlsUrl;
          videoRef.current.play();
        }
      } catch (error) {
        console.error('Failed to initialize HLS stream:', error);
      }
    };

    initHlsStream();

    return () => {
      if (hlsInstance) {
        hlsInstance.destroy();
        setHlsInstance(null);
      }
    };
  }, [hlsUrl, isStreaming, streamStatus, isHlsSupported]);

  // Handle volume changes
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.volume = volume / 100;
      videoRef.current.muted = isMuted;
    }
  }, [volume, isMuted]);

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const handleVolumeChange = (value: number[]) => {
    setVolume(value[0]);
    if (value[0] === 0) {
      setIsMuted(true);
    } else if (isMuted) {
      setIsMuted(false);
    }
  };

  const renderContent = () => {
    switch (streamStatus) {
      case 'idle':
        return (
          <div className="flex flex-col items-center justify-center h-full text-foreground">
            <div className="w-20 h-20 bg-muted rounded-full flex items-center justify-center mb-4 shadow-glow">
              <Play className="w-10 h-10 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Ready to Stream</h3>
            <p className="text-muted-foreground text-center max-w-sm">
              Enter an RTSP URL and click "Start Stream" to begin watching your livestream
            </p>
          </div>
        );
      
      case 'connecting':
        return (
          <div className="flex flex-col items-center justify-center h-full text-foreground">
            <Loader2 className="w-12 h-12 animate-spin mb-4 text-primary" />
            <h3 className="text-xl font-semibold mb-2">Connecting...</h3>
            <p className="text-muted-foreground">Establishing connection to RTSP stream</p>
          </div>
        );
      
      case 'playing':
        return (
          <div className="relative w-full h-full">
            {hlsUrl ? (
              <>
                <video
                  ref={videoRef}
                  className="w-full h-full object-cover"
                  controls={false}
                  autoPlay
                  muted={isMuted}
                  playsInline
                />
                
                {/* Video Controls Overlay */}
                <div className="absolute bottom-4 left-4 right-4 bg-black/50 backdrop-blur-sm rounded-lg p-3">
                  <div className="flex items-center space-x-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={toggleMute}
                      className="text-white hover:bg-white/20"
                    >
                      {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                    </Button>
                    
                    <div className="flex-1 flex items-center space-x-2">
                      <Slider
                        value={[volume]}
                        onValueChange={handleVolumeChange}
                        max={100}
                        min={0}
                        step={1}
                        className="flex-1"
                      />
                      <span className="text-white text-xs w-8">{volume}%</span>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              // Fallback for when HLS URL is not available
              <div className="w-full h-full bg-gradient-subtle flex items-center justify-center">
                <div className="text-center text-foreground">
                  <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mb-4 mx-auto animate-pulse shadow-glow">
                    <div className="w-3 h-3 bg-primary-foreground rounded-full"></div>
                  </div>
                  <p className="text-sm text-muted-foreground break-all px-4">{rtspUrl}</p>
                </div>
              </div>
            )}
            
            {/* Live indicator */}
            <div className="absolute top-4 left-4 bg-primary text-primary-foreground px-3 py-1 rounded-full text-sm font-semibold flex items-center space-x-2 shadow-glow">
              <div className="w-2 h-2 bg-primary-foreground rounded-full animate-pulse"></div>
              <span>LIVE</span>
            </div>
          </div>
        );
      
      case 'error':
        return (
          <div className="flex flex-col items-center justify-center h-full text-foreground">
            <AlertCircle className="w-12 h-12 text-destructive mb-4" />
            <h3 className="text-xl font-semibold mb-2">Connection Failed</h3>
            <p className="text-muted-foreground text-center max-w-sm">
              Unable to connect to the RTSP stream. Please check the URL and try again.
            </p>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="w-full h-full min-h-[400px] bg-black rounded-lg relative overflow-hidden">
      {renderContent()}
    </div>
  );
};
