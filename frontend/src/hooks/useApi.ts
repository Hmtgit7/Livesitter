import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  overlaysApi, 
  streamsApi, 
  healthApi, 
  apiUtils,
  type Overlay,
  type Stream,
  type ApiResponse,
  type PaginatedResponse
} from '@/services/api';
import { useToast } from '@/hooks/use-toast';

// Query keys
export const queryKeys = {
  health: ['health'],
  overlays: ['overlays'],
  overlay: (id: string) => ['overlay', id],
  streams: ['streams'],
  stream: (id: string) => ['stream', id],
  streamStatus: (id: string) => ['streamStatus', id],
  activeStreams: ['activeStreams'],
} as const;

// Health hooks
export const useHealthCheck = () => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => healthApi.check(),
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
  });
};

export const useDatabaseHealth = () => {
  return useQuery({
    queryKey: [...queryKeys.health, 'database'],
    queryFn: () => healthApi.database(),
    refetchInterval: 30000,
  });
};

export const useStreamsHealth = () => {
  return useQuery({
    queryKey: [...queryKeys.health, 'streams'],
    queryFn: () => healthApi.streams(),
    refetchInterval: 10000, // More frequent for streams
  });
};

// Overlay hooks
export const useOverlays = (params?: { page?: number; limit?: number; user_id?: string }) => {
  return useQuery({
    queryKey: [...queryKeys.overlays, params],
    queryFn: () => overlaysApi.getAll(params),
    select: (data) => ({
      ...data.data,
      data: data.data.data.map(apiUtils.convertOverlayFromApi),
    }),
  });
};

export const useOverlay = (id: string) => {
  return useQuery({
    queryKey: queryKeys.overlay(id),
    queryFn: () => overlaysApi.getById(id),
    enabled: !!id,
    select: (data) => ({
      ...data.data,
      data: data.data.data ? apiUtils.convertOverlayFromApi(data.data.data) : null,
    }),
  });
};

export const useCreateOverlay = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (overlay: any) => {
      const apiOverlay = apiUtils.convertOverlayToApi(overlay);
      return overlaysApi.create(apiOverlay);
    },
    onSuccess: (response) => {
      if (response.data.success) {
        toast({
          title: "Overlay Created",
          description: "Overlay has been created successfully.",
        });
        queryClient.invalidateQueries({ queryKey: queryKeys.overlays });
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Failed to create overlay';
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    },
  });
};

export const useUpdateOverlay = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, overlay }: { id: string; overlay: any }) => {
      const apiOverlay = apiUtils.convertOverlayToApi(overlay);
      return overlaysApi.update(id, apiOverlay);
    },
    onSuccess: (response, { id }) => {
      if (response.data.success) {
        toast({
          title: "Overlay Updated",
          description: "Overlay has been updated successfully.",
        });
        queryClient.invalidateQueries({ queryKey: queryKeys.overlays });
        queryClient.invalidateQueries({ queryKey: queryKeys.overlay(id) });
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Failed to update overlay';
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    },
  });
};

export const useDeleteOverlay = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => overlaysApi.delete(id),
    onSuccess: (response) => {
      if (response.data.success) {
        toast({
          title: "Overlay Deleted",
          description: "Overlay has been deleted successfully.",
        });
        queryClient.invalidateQueries({ queryKey: queryKeys.overlays });
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Failed to delete overlay';
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    },
  });
};

export const useCreateOverlaysBatch = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ overlays, user_id }: { overlays: any[]; user_id?: string }) => {
      const apiOverlays = overlays.map(apiUtils.convertOverlayToApi);
      return overlaysApi.createBatch(apiOverlays, user_id);
    },
    onSuccess: (response) => {
      if (response.data.success) {
        toast({
          title: "Overlays Created",
          description: `${response.data.data?.length || 0} overlays have been created successfully.`,
        });
        queryClient.invalidateQueries({ queryKey: queryKeys.overlays });
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Failed to create overlays';
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    },
  });
};

// Stream hooks
export const useStreams = (params?: { user_id?: string }) => {
  return useQuery({
    queryKey: [...queryKeys.streams, params],
    queryFn: () => streamsApi.getAll(params),
    select: (data) => ({
      ...data.data,
      data: data.data.data?.map(apiUtils.convertStreamFromApi) || [],
    }),
  });
};

export const useStream = (id: string) => {
  return useQuery({
    queryKey: queryKeys.stream(id),
    queryFn: () => streamsApi.getById(id),
    enabled: !!id,
    select: (data) => ({
      ...data.data,
      data: data.data.data ? apiUtils.convertStreamFromApi(data.data.data) : null,
    }),
  });
};

export const useStreamStatus = (id: string) => {
  return useQuery({
    queryKey: queryKeys.streamStatus(id),
    queryFn: () => streamsApi.getStatus(id),
    enabled: !!id,
    refetchInterval: 5000, // Poll every 5 seconds
  });
};

export const useActiveStreams = () => {
  return useQuery({
    queryKey: queryKeys.activeStreams,
    queryFn: () => streamsApi.getActive(),
    refetchInterval: 5000, // Poll every 5 seconds
    select: (data) => ({
      ...data.data,
      data: data.data.data?.map(apiUtils.convertStreamFromApi) || [],
    }),
  });
};

export const useCreateStream = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (stream: any) => {
      const apiStream = apiUtils.convertStreamToApi(stream);
      return streamsApi.create(apiStream);
    },
    onSuccess: (response) => {
      if (response.data.success) {
        toast({
          title: "Stream Created",
          description: "Stream has been created successfully.",
        });
        queryClient.invalidateQueries({ queryKey: queryKeys.streams });
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Failed to create stream';
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    },
  });
};

export const useUpdateStream = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, stream }: { id: string; stream: any }) => {
      const apiStream = apiUtils.convertStreamToApi(stream);
      return streamsApi.update(id, apiStream);
    },
    onSuccess: (response, { id }) => {
      if (response.data.success) {
        toast({
          title: "Stream Updated",
          description: "Stream has been updated successfully.",
        });
        queryClient.invalidateQueries({ queryKey: queryKeys.streams });
        queryClient.invalidateQueries({ queryKey: queryKeys.stream(id) });
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Failed to update stream';
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    },
  });
};

export const useDeleteStream = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => streamsApi.delete(id),
    onSuccess: (response) => {
      if (response.data.success) {
        toast({
          title: "Stream Deleted",
          description: "Stream has been deleted successfully.",
        });
        queryClient.invalidateQueries({ queryKey: queryKeys.streams });
        queryClient.invalidateQueries({ queryKey: queryKeys.activeStreams });
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Failed to delete stream';
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    },
  });
};

export const useStartStream = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => streamsApi.start(id),
    onSuccess: (response, id) => {
      if (response.data.success) {
        toast({
          title: "Stream Started",
          description: "Stream has been started successfully.",
        });
        queryClient.invalidateQueries({ queryKey: queryKeys.streams });
        queryClient.invalidateQueries({ queryKey: queryKeys.stream(id) });
        queryClient.invalidateQueries({ queryKey: queryKeys.streamStatus(id) });
        queryClient.invalidateQueries({ queryKey: queryKeys.activeStreams });
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Failed to start stream';
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    },
  });
};

export const useStopStream = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => streamsApi.stop(id),
    onSuccess: (response, id) => {
      if (response.data.success) {
        toast({
          title: "Stream Stopped",
          description: "Stream has been stopped successfully.",
        });
        queryClient.invalidateQueries({ queryKey: queryKeys.streams });
        queryClient.invalidateQueries({ queryKey: queryKeys.stream(id) });
        queryClient.invalidateQueries({ queryKey: queryKeys.streamStatus(id) });
        queryClient.invalidateQueries({ queryKey: queryKeys.activeStreams });
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.error || 'Failed to stop stream';
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    },
  });
}; 