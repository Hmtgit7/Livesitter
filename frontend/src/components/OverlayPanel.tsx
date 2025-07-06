import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { Plus, Type, Image, Layers, Trash2, Eye, EyeOff } from 'lucide-react';
import { useToast } from "@/hooks/use-toast";

interface Overlay {
  id?: string;
  _id?: string;
  name?: string;
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

interface OverlayPanelProps {
  overlays: Overlay[];
  setOverlays?: React.Dispatch<React.SetStateAction<Overlay[]>>;
  onAddOverlay?: (overlay: Overlay) => void;
  onUpdateOverlay?: (id: string, overlay: Overlay) => void;
  onDeleteOverlay?: (id: string) => void;
  onBatchAddOverlays?: (overlays: Overlay[]) => void;
  loading?: boolean;
}

export const OverlayPanel: React.FC<OverlayPanelProps> = ({
  overlays,
  onAddOverlay,
  onUpdateOverlay,
  onDeleteOverlay,
  onBatchAddOverlays,
  loading
}) => {
  const [newOverlay, setNewOverlay] = useState({
    type: 'text' as 'text' | 'logo' | 'image',
    content: '',
    fontSize: 24,
    color: '#ffffff',
    opacity: 100,
    positionX: 50,
    positionY: 50,
  });
  const { toast } = useToast();

  const addOverlay = () => {
    if (!newOverlay.content.trim()) {
      toast({
        title: "Content Required",
        description: "Please enter content for the overlay.",
        variant: "destructive"
      });
      return;
    }
    const overlay: Overlay = {
      type: newOverlay.type,
      content: newOverlay.content,
      position: { x: newOverlay.positionX, y: newOverlay.positionY },
      size: { width: 200, height: 50 },
      style: {
        fontSize: newOverlay.fontSize,
        color: newOverlay.color,
        opacity: newOverlay.opacity / 100,
      },
      visible: true,
    };
    if (onAddOverlay) onAddOverlay(overlay);
    setNewOverlay({ ...newOverlay, content: '' });
    toast({
      title: "Overlay Added",
      description: `${newOverlay.type} overlay has been added to the stream.`,
    });
  };

  const removeOverlay = (id: string) => {
    if (onDeleteOverlay) onDeleteOverlay(id);
    toast({
      title: "Overlay Removed",
      description: "Overlay has been removed from the stream.",
    });
  };

  const toggleOverlayVisibility = (id: string) => {
    // Optionally implement visibility toggle with backend if needed
  };

  return (
    <Card className="bg-gradient-subtle border-border/50 shadow-glow sticky top-4">
      <CardHeader>
        <CardTitle className="text-foreground flex items-center space-x-2">
          <Layers className="w-5 h-5 text-primary" />
          <span>Overlay Manager</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Tabs defaultValue="add" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-muted/50">
            <TabsTrigger value="add" className="text-foreground data-[state=active]:bg-card data-[state=active]:shadow-sm">
              Add Overlay
            </TabsTrigger>
            <TabsTrigger value="manage" className="text-foreground data-[state=active]:bg-card data-[state=active]:shadow-sm">
              Manage ({overlays.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="add" className="space-y-4">
            <div className="space-y-3">
              <div>
                <Label className="text-foreground font-medium">Overlay Type</Label>
                <Select
                  value={newOverlay.type}
                  onValueChange={(value: string) => 
                    setNewOverlay({ ...newOverlay, type: value as 'text' | 'logo' | 'image' })
                  }
                >
                  <SelectTrigger className="bg-muted/30 border-border text-foreground rounded-xl">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border rounded-xl">
                    <SelectItem value="text">
                      <div className="flex items-center space-x-2">
                        <Type className="w-4 h-4 text-primary" />
                        <span>Text</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="logo">
                      <div className="flex items-center space-x-2">
                        <Image className="w-4 h-4 text-secondary" />
                        <span>Logo</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="image">
                      <div className="flex items-center space-x-2">
                        <Image className="w-4 h-4 text-accent" />
                        <span>Image</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label className="text-foreground font-medium">Content</Label>
                <Input
                  value={newOverlay.content}
                  onChange={(e) => setNewOverlay({ ...newOverlay, content: e.target.value })}
                  placeholder={
                    newOverlay.type === 'text' 
                      ? 'Enter text content...' 
                      : 'Enter URL or identifier...'
                  }
                  className="bg-muted/30 border-border text-foreground placeholder:text-muted-foreground rounded-xl"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label className="text-foreground font-medium">Position X: {newOverlay.positionX}%</Label>
                  <Slider
                    value={[newOverlay.positionX]}
                    onValueChange={(value) => setNewOverlay({ ...newOverlay, positionX: value[0] })}
                    min={0}
                    max={90}
                    step={1}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label className="text-foreground font-medium">Position Y: {newOverlay.positionY}%</Label>
                  <Slider
                    value={[newOverlay.positionY]}
                    onValueChange={(value) => setNewOverlay({ ...newOverlay, positionY: value[0] })}
                    min={0}
                    max={90}
                    step={1}
                    className="mt-2"
                  />
                </div>
              </div>

              {newOverlay.type === 'text' && (
                <>
                  <div>
                    <Label className="text-foreground font-medium">Font Size: {newOverlay.fontSize}px</Label>
                    <Slider
                      value={[newOverlay.fontSize]}
                      onValueChange={(value) => setNewOverlay({ ...newOverlay, fontSize: value[0] })}
                      min={12}
                      max={72}
                      step={1}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label className="text-foreground font-medium">Text Color</Label>
                    <div className="flex items-center space-x-2 mt-1">
                      <input
                        type="color"
                        value={newOverlay.color}
                        onChange={(e) => setNewOverlay({ ...newOverlay, color: e.target.value })}
                        className="w-8 h-8 rounded-lg border border-border bg-muted/30"
                      />
                      <Input
                        value={newOverlay.color}
                        onChange={(e) => setNewOverlay({ ...newOverlay, color: e.target.value })}
                        className="bg-muted/30 border-border text-foreground text-xs rounded-lg"
                      />
                    </div>
                  </div>
                </>
              )}

              <div>
                <Label className="text-foreground font-medium">Opacity: {newOverlay.opacity}%</Label>
                <Slider
                  value={[newOverlay.opacity]}
                  onValueChange={(value) => setNewOverlay({ ...newOverlay, opacity: value[0] })}
                  min={0}
                  max={100}
                  step={1}
                  className="mt-2"
                />
              </div>
            </div>
            <Button onClick={addOverlay} className="w-full mt-2" disabled={loading}>
              <Plus className="w-4 h-4 mr-2" /> Add Overlay
            </Button>
          </TabsContent>

          <TabsContent value="manage" className="space-y-4">
            {loading ? (
              <div className="text-center text-muted-foreground py-8">Loading overlays...</div>
            ) : overlays.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">No overlays added yet.</div>
            ) : (
              <div className="space-y-2">
                {overlays.map((overlay) => (
                  <Card key={overlay._id || overlay.id} className="bg-card border-border/30 p-3 flex items-center justify-between">
                    <div className="flex flex-col">
                      <span className="font-semibold text-foreground">{overlay.type.toUpperCase()}</span>
                      <span className="text-muted-foreground text-xs break-all">{overlay.content}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="icon" onClick={() => removeOverlay(overlay._id || overlay.id!)}>
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
