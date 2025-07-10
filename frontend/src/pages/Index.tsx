import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { VideoPlayer } from "@/components/VideoPlayer";
import { OverlayManager } from "@/components/OverlayManager";
import { StreamControls } from "@/components/StreamControls";
import { OverlayPanel } from "@/components/OverlayPanel";
import { Play, Settings, Monitor, Layers } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  useCreateStream,
  useStartStream,
  useStopStream,
  useStreamStatus,
  useStreams,
  useOverlays,
  useCreateOverlay,
  useUpdateOverlay,
  useDeleteOverlay,
  useCreateOverlaysBatch,
} from '@/hooks/useApi';

const Index = () => {
  const [rtspUrl, setRtspUrl] = useState(''); // Remove default test URL
  const [streamId, setStreamId] = useState<string | null>(null);
  const [hlsUrl, setHlsUrl] = useState<string | undefined>(undefined);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamStatus, setStreamStatus] = useState<'idle' | 'connecting' | 'playing' | 'error'>('idle');
  const { toast } = useToast();

  // Overlays
  const {
    data: overlaysData,
    isLoading: overlaysLoading,
    refetch: refetchOverlays
  } = useOverlays({ page: 1, limit: 100 });
  const overlays = overlaysData?.data || [];
  const createOverlay = useCreateOverlay();
  const updateOverlay = useUpdateOverlay();
  const deleteOverlay = useDeleteOverlay();
  const createOverlaysBatch = useCreateOverlaysBatch();

  // Streams
  const createStream = useCreateStream();
  const startStream = useStartStream();
  const stopStream = useStopStream();
  const streamStatusQuery = useStreamStatus(streamId || '');

  // Handle start stream
  const handleStartStream = () => {
    if (!rtspUrl.trim()) {
      toast({
        title: "RTSP URL Required",
        description: "Please enter a valid RTSP URL to start streaming.",
        variant: "destructive"
      });
      return;
    }
    setStreamStatus('connecting');
    // Create stream in backend
    createStream.mutate(
      {
        name: 'My Stream',
        rtsp_url: rtspUrl,
        settings: { quality: 'medium', fps: 30, resolution: '720p' }
      },
      {
        onSuccess: (res) => {
          const id = res.data.data._id;
          setStreamId(id);
          // Start the stream
          startStream.mutate(id, {
            onSuccess: (startRes) => {
              // Construct full HLS URL with API base URL
              const hlsUrl = `https://livesitter-yeop.onrender.com${startRes.data.data.hls_url}`;
              setHlsUrl(hlsUrl);
              setIsStreaming(true);
              setStreamStatus('playing');
              toast({
                title: "Stream Started",
                description: "Successfully connected to RTSP stream.",
              });
              
              // Create test HLS files if needed
              fetch(`https://livesitter-yeop.onrender.com/api/streams/test-hls/${id}`)
                .then(response => {
                  if (response.ok) {
                    console.log('Test HLS files created');
                  }
                })
                .catch(error => {
                  console.error('Failed to create test HLS files:', error);
                });
            },
            onError: () => {
              setStreamStatus('error');
              setIsStreaming(false);
            }
          });
        },
        onError: () => {
          setStreamStatus('error');
          setIsStreaming(false);
        }
      }
    );
  };

  // Handle stop stream
  const handleStopStream = () => {
    if (!streamId) return;
    setStreamStatus('connecting');
    stopStream.mutate(streamId, {
      onSuccess: () => {
        setIsStreaming(false);
        setStreamStatus('idle');
        setHlsUrl(undefined);
        setStreamId(null);
        toast({
          title: "Stream Stopped",
          description: "RTSP stream has been disconnected.",
        });
      },
      onError: () => {
        setStreamStatus('error');
      }
    });
  };

  // Poll stream status
  useEffect(() => {
    if (streamId && streamStatusQuery.data?.data) {
      const status = streamStatusQuery.data.data.status;
      if (status === 'running') {
        setStreamStatus('playing');
      } else if (status === 'stopped') {
        setStreamStatus('idle');
        setIsStreaming(false);
      } else if (status === 'error') {
        setStreamStatus('error');
        setIsStreaming(false);
      }
    }
  }, [streamStatusQuery.data, streamId]);

  // Overlay CRUD handlers
  const handleAddOverlay = (overlay: any) => {
    createOverlay.mutate(overlay, {
      onSuccess: () => refetchOverlays(),
    });
  };
  const handleUpdateOverlay = (id: string, overlay: any) => {
    updateOverlay.mutate({ id, overlay }, {
      onSuccess: () => refetchOverlays(),
    });
  };
  const handleDeleteOverlay = (id: string) => {
    deleteOverlay.mutate(id, {
      onSuccess: () => refetchOverlays(),
    });
  };
  const handleBatchAddOverlays = (batch: any[]) => {
    createOverlaysBatch.mutate({ overlays: batch }, {
      onSuccess: () => refetchOverlays(),
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Modern Header with Floating Design */}
      <header className="border-b border-border/50 bg-card/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-glow">
                <Monitor className="w-7 h-7 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-foreground">LiveCast Pro</h1>
                <p className="text-muted-foreground">Professional RTSP Streaming</p>
              </div>
            </div>
            <Badge variant="secondary" className="px-4 py-2 text-sm font-medium shadow-warm">
              v2.0 Professional
            </Badge>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-12">
        {/* Hero Section with Side Panel Layout */}
        <div className="flex flex-col lg:flex-row gap-8 mb-12">
          {/* Main Stream Section */}
          <div className="flex-1 space-y-8">
            {/* Stream Configuration Card */}
            <Card className="bg-gradient-subtle border-border/50 shadow-glow">
              <CardHeader className="pb-4">
                <CardTitle className="text-foreground flex items-center space-x-3 text-xl">
                  <Play className="w-6 h-6 text-primary" />
                  <span>Stream Configuration</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col sm:flex-row gap-4">
                  <Input
                    type="url"
                    placeholder="Enter RTSP URL (e.g., rtsp://rtsp.stream/pattern)"
                    value={rtspUrl}
                    onChange={(e) => setRtspUrl(e.target.value)}
                    className="flex-1 bg-muted/50 border-border text-foreground placeholder:text-muted-foreground rounded-xl h-12"
                  />
                  <Button
                    onClick={isStreaming ? handleStopStream : handleStartStream}
                    disabled={streamStatus === 'connecting' || createStream.isPending || startStream.isPending || stopStream.isPending}
                    className={`px-8 h-12 rounded-xl font-medium transition-all duration-300 ${
                      isStreaming 
                        ? 'bg-destructive hover:bg-destructive/90 shadow-[0_0_20px_hsl(var(--destructive)/0.3)]' 
                        : 'bg-gradient-primary hover:shadow-glow shadow-warm'
                    }`}
                  >
                    {streamStatus === 'connecting' ? 'Connecting...' : (isStreaming ? 'Stop Stream' : 'Start Stream')}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Video Player with Modern Design */}
            <Card className="bg-gradient-subtle border-border/50 shadow-glow overflow-hidden">
              <CardContent className="p-0">
                <div className="relative aspect-video bg-background/50 rounded-xl overflow-hidden border border-border/20">
                  <VideoPlayer 
                    isStreaming={isStreaming}
                    streamStatus={streamStatus}
                    rtspUrl={rtspUrl}
                    hlsUrl={hlsUrl}
                  />
                  <OverlayManager 
                    overlays={overlays} 
                    onUpdateOverlay={handleUpdateOverlay}
                  />
                </div>
                <div className="p-6 bg-gradient-to-r from-card/50 to-muted/30">
                  <StreamControls 
                    isStreaming={isStreaming}
                    streamStatus={streamStatus}
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Side Panel for Overlay Management */}
          <div className="lg:w-96">
            <OverlayPanel 
              overlays={overlays} 
              setOverlays={() => {}} // overlays are now backend-driven
              onAddOverlay={handleAddOverlay}
              onUpdateOverlay={handleUpdateOverlay}
              onDeleteOverlay={handleDeleteOverlay}
              onBatchAddOverlays={handleBatchAddOverlays}
              loading={overlaysLoading}
            />
            
          </div>
        </div>

        {/* Stream Stats with Modern Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-subtle border-border/50 text-center hover:shadow-glow transition-all duration-300">
            <CardContent className="p-6">
              <div className="text-3xl font-bold text-primary mb-2">{isStreaming ? '1080p' : '--'}</div>
              <div className="text-sm text-muted-foreground font-medium">Resolution</div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-subtle border-border/50 text-center hover:shadow-warm transition-all duration-300">
            <CardContent className="p-6">
              <div className="text-3xl font-bold text-secondary mb-2">{isStreaming ? '30fps' : '--'}</div>
              <div className="text-sm text-muted-foreground font-medium">Frame Rate</div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-subtle border-border/50 text-center hover:shadow-glow transition-all duration-300">
            <CardContent className="p-6">
              <div className="text-3xl font-bold text-primary mb-2">{isStreaming ? '2.5Mbps' : '--'}</div>
              <div className="text-sm text-muted-foreground font-medium">Bitrate</div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-subtle border-border/50 text-center hover:shadow-warm transition-all duration-300">
            <CardContent className="p-6">
              <div className={`text-3xl font-bold mb-2 ${streamStatus === 'playing' ? 'text-primary' : 'text-muted-foreground'}`}>
                {streamStatus === 'playing' ? 'LIVE' : 'OFFLINE'}
              </div>
              <div className="text-sm text-muted-foreground font-medium">Status</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Index;
