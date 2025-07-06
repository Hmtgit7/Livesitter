import React, { useState, useRef } from 'react';

interface Overlay {
  id?: string;
  _id?: string;
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
  visible?: boolean;
}

interface OverlayManagerProps {
  overlays: Overlay[];
  onUpdateOverlay?: (id: string, overlay: Overlay) => void;
}

export const OverlayManager: React.FC<OverlayManagerProps> = ({ overlays, onUpdateOverlay }) => {
  const [draggedOverlay, setDraggedOverlay] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = (e: React.MouseEvent, overlayId: string) => {
    const overlay = overlays.find(o => (o._id || o.id) === overlayId);
    if (!overlay || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const offsetX = e.clientX - rect.left - overlay.position.x;
    const offsetY = e.clientY - rect.top - overlay.position.y;
    
    setDraggedOverlay(overlayId);
    setDragOffset({ x: offsetX, y: offsetY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!draggedOverlay || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const newX = e.clientX - rect.left - dragOffset.x;
    const newY = e.clientY - rect.top - dragOffset.y;

    // Clamp to container bounds
    const clampedX = Math.max(0, Math.min(100 - 10, newX));
    const clampedY = Math.max(0, Math.min(100 - 10, newY));

    const overlay = overlays.find(o => (o._id || o.id) === draggedOverlay);
    if (overlay && onUpdateOverlay) {
      onUpdateOverlay(draggedOverlay, {
        ...overlay,
        position: { x: clampedX, y: clampedY }
      });
    }
  };

  const handleMouseUp = () => {
    setDraggedOverlay(null);
  };

  return (
    <div 
      ref={containerRef}
      className="absolute inset-0 pointer-events-none"
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {overlays.map((overlay) => {
        const overlayId = overlay._id || overlay.id;
        if (!overlayId) return null;

        return (
          <div
            key={overlayId}
            className={`absolute pointer-events-auto ${draggedOverlay === overlayId ? 'cursor-grabbing' : 'cursor-grab'}`}
            style={{
              left: `${overlay.position.x}%`,
              top: `${overlay.position.y}%`,
              width: `${overlay.size.width}px`,
              height: `${overlay.size.height}px`,
              opacity: overlay.style.opacity || 1,
              zIndex: draggedOverlay === overlayId ? 1000 : 1,
            }}
            onMouseDown={(e) => handleMouseDown(e, overlayId)}
          >
            {overlay.type === 'text' && (
              <div
                className="text-white font-semibold shadow-lg select-none"
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
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-2 text-white text-center select-none">
                <div className="text-sm font-bold">{overlay.content}</div>
              </div>
            )}
            {overlay.type === 'image' && (
              <div className="select-none">
                <img 
                  src={overlay.content} 
                  alt="Overlay"
                  className="max-w-full max-h-full object-contain"
                  style={{
                    width: overlay.size.width,
                    height: overlay.size.height,
                  }}
                  onError={(e) => {
                    // Fallback if image fails to load
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    target.nextElementSibling?.classList.remove('hidden');
                  }}
                />
                <div className="bg-slate-700/50 rounded border-2 border-dashed border-slate-500 flex items-center justify-center text-white text-xs hidden">
                  Failed to load image
                </div>
              </div>
            )}
            
            {/* Resize handles */}
            <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-blue-500 rounded-full cursor-se-resize opacity-75 hover:opacity-100"></div>
          </div>
        );
      })}
    </div>
  );
};
