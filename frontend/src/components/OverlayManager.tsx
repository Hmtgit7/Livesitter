
import React from 'react';

interface Overlay {
  id: string;
  type: 'text' | 'logo' | 'image';
  content: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  style: {
    fontSize?: number;
    color?: string;
    fontFamily?: string;
    opacity?: number;
  };
}

interface OverlayManagerProps {
  overlays: Overlay[];
}

export const OverlayManager: React.FC<OverlayManagerProps> = ({ overlays }) => {
  return (
    <div className="absolute inset-0 pointer-events-none">
      {overlays.map((overlay) => (
        <div
          key={overlay.id}
          className="absolute pointer-events-auto cursor-move"
          style={{
            left: `${overlay.position.x}%`,
            top: `${overlay.position.y}%`,
            width: `${overlay.size.width}px`,
            height: `${overlay.size.height}px`,
            opacity: overlay.style.opacity || 1,
          }}
        >
          {overlay.type === 'text' && (
            <div
              className="text-white font-semibold shadow-lg"
              style={{
                fontSize: `${overlay.style.fontSize || 16}px`,
                color: overlay.style.color || '#ffffff',
                fontFamily: overlay.style.fontFamily || 'sans-serif',
                textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
              }}
            >
              {overlay.content}
            </div>
          )}
          {overlay.type === 'logo' && (
            <div className="bg-white/20 backdrop-blur-sm rounded-lg p-2 text-white text-center">
              <div className="text-sm font-bold">{overlay.content}</div>
            </div>
          )}
          {overlay.type === 'image' && (
            <div className="bg-slate-700/50 rounded border-2 border-dashed border-slate-500 flex items-center justify-center text-white text-xs">
              IMG
            </div>
          )}
          
          {/* Resize handles */}
          <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-blue-500 rounded-full cursor-se-resize opacity-75 hover:opacity-100"></div>
        </div>
      ))}
    </div>
  );
};
