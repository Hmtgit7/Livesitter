
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Play, Pause, Volume2, VolumeX, Maximize, Settings } from 'lucide-react';

interface StreamControlsProps {
  isStreaming: boolean;
  streamStatus: 'idle' | 'connecting' | 'playing' | 'error';
}

export const StreamControls: React.FC<StreamControlsProps> = ({ 
  isStreaming, 
  streamStatus 
}) => {
  const [isPlaying, setIsPlaying] = useState(true);
  const [volume, setVolume] = useState([75]);
  const [isMuted, setIsMuted] = useState(false);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleVolumeChange = (value: number[]) => {
    setVolume(value);
    if (value[0] === 0) {
      setIsMuted(true);
    } else {
      setIsMuted(false);
    }
  };

  const handleMute = () => {
    setIsMuted(!isMuted);
  };

  if (!isStreaming || streamStatus !== 'playing') {
    return null;
  }

  return (
    <div className="flex items-center justify-between bg-slate-800/80 backdrop-blur-sm">
      <div className="flex items-center space-x-4">
        {/* Play/Pause Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={handlePlayPause}
          className="text-white hover:bg-slate-700"
        >
          {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </Button>

        {/* Volume Controls */}
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleMute}
            className="text-white hover:bg-slate-700"
          >
            {isMuted || volume[0] === 0 ? (
              <VolumeX className="w-4 h-4" />
            ) : (
              <Volume2 className="w-4 h-4" />
            )}
          </Button>
          <div className="w-24">
            <Slider
              value={isMuted ? [0] : volume}
              onValueChange={handleVolumeChange}
              max={100}
              step={1}
              className="cursor-pointer"
            />
          </div>
          <span className="text-xs text-slate-400 w-8">
            {isMuted ? 0 : volume[0]}%
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        {/* Settings Button */}
        <Button
          variant="ghost"
          size="sm"
          className="text-white hover:bg-slate-700"
        >
          <Settings className="w-4 h-4" />
        </Button>

        {/* Fullscreen Button */}
        <Button
          variant="ghost"
          size="sm"
          className="text-white hover:bg-slate-700"
        >
          <Maximize className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};
