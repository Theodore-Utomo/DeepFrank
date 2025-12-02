'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { ImageAnalysisHistoryItem } from '@/types/api';
import { getUserAnalyses } from '@/lib/api';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ImageIcon, Upload, Calendar, Heart, AlertCircle, Loader2, MessageSquare } from 'lucide-react';

export default function ProfilePage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [analyses, setAnalyses] = useState<ImageAnalysisHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
      return;
    }

    // Fetch user analyses if authenticated
    if (isAuthenticated && user) {
      fetchAnalyses();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, authLoading, user]);

  const fetchAnalyses = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getUserAnalyses();
      setAnalyses(response.analyses);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analyses');
      console.error('Error fetching analyses:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatAnalysis = (item: ImageAnalysisHistoryItem): string => {
    const parts: string[] = [];

    if (item.detections.length > 0) {
      parts.push(`${item.detections.length} body parts`);
    }

    if (item.analysis) {
      const a = item.analysis;
      if (a.eye_state) parts.push(`Eyes: ${a.eye_state}`);
      if (a.mouth_state) parts.push(`Mouth: ${a.mouth_state}`);
      if (a.tail_position) parts.push(`Tail: ${a.tail_position}`);
    }

    if (item.emotion) {
      parts.push(`Emotion: ${item.emotion}`);
    }

    return parts.join(' • ');
  };

  if (authLoading || loading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <Skeleton className="h-12 w-64" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Skeleton key={i} className="h-64" />
            ))}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <Card className="p-8">
          <div className="text-center space-y-4">
            <AlertCircle className="h-12 w-12 text-destructive mx-auto" />
            <div>
              <p className="text-destructive font-medium mb-2">{error}</p>
              <Button onClick={fetchAnalyses} variant="outline">
                <Loader2 className="mr-2 h-4 w-4" />
                Retry
              </Button>
            </div>
          </div>
        </Card>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold text-foreground">My Profile</h1>
            <p className="text-muted-foreground">
              View your uploaded cat images and analysis history
            </p>
          </div>
          <Link href="/">
            <Button size="lg">
              <Upload className="mr-2 h-4 w-4" />
              Upload New
            </Button>
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">Total Images</p>
                <p className="text-3xl font-bold text-foreground">{total}</p>
              </div>
              <div className="p-3 bg-primary/10 rounded-lg">
                <ImageIcon className="h-6 w-6 text-primary" />
              </div>
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">Analyses</p>
                <p className="text-3xl font-bold text-foreground">{total}</p>
              </div>
              <div className="p-3 bg-primary/10 rounded-lg">
                <Calendar className="h-6 w-6 text-primary" />
              </div>
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">Emotions Detected</p>
                <p className="text-3xl font-bold text-foreground">
                  {new Set(analyses.map(item => item.emotion).filter(Boolean)).size}
                </p>
              </div>
              <div className="p-3 bg-primary/10 rounded-lg">
                <Heart className="h-6 w-6 text-primary" />
              </div>
            </div>
          </Card>
        </div>

        {/* Image Grid */}
        {analyses.length === 0 ? (
          <Card className="p-12">
            <div className="text-center space-y-4">
              <div className="p-4 bg-muted rounded-full w-16 h-16 mx-auto flex items-center justify-center">
                <ImageIcon className="h-8 w-8 text-muted-foreground" />
              </div>
              <div>
                <p className="text-lg font-medium text-foreground mb-2">No images uploaded yet</p>
                <p className="text-sm text-muted-foreground mb-4">
                  Start analyzing your cat's emotional state
                </p>
              </div>
              <Link href="/">
                <Button size="lg">
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Your First Image
                </Button>
              </Link>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {analyses.map((item) => {
              const hasChat = !!item.chat_session_id;
              
              return (
                <Card
                  key={item.id}
                  className={`overflow-hidden transition-all ${
                    hasChat 
                      ? 'hover:shadow-lg cursor-pointer hover:border-primary/50' 
                      : 'hover:shadow-lg'
                  }`}
                  onClick={() => {
                    if (hasChat && item.chat_session_id) {
                      router.push(`/chat/${item.chat_session_id}`);
                    }
                  }}
                >
                  {/* Image Placeholder */}
                  <div className="relative w-full h-48 bg-gradient-to-br from-muted to-muted/50 flex items-center justify-center">
                    <ImageIcon className="w-16 h-16 text-muted-foreground" />
                    {hasChat && (
                      <div className="absolute top-2 right-2 p-2 bg-primary rounded-full shadow-md">
                        <MessageSquare className="w-4 h-4 text-primary-foreground" />
                      </div>
                    )}
                  </div>

                  {/* Image Info */}
                  <div className="p-4 space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-foreground mb-1 truncate">
                          {item.filename}
                        </h3>
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(item.created_at)}
                        </p>
                      </div>
                      {hasChat && (
                        <Badge variant="secondary" className="text-xs flex items-center gap-1 whitespace-nowrap">
                          <MessageSquare className="h-3 w-3" />
                          Chat
                        </Badge>
                      )}
                    </div>

                    {/* Analysis Summary */}
                    <div className="space-y-2">
                      {item.detections.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {item.detections.slice(0, 3).map((det, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {det.class_name}
                            </Badge>
                          ))}
                          {item.detections.length > 3 && (
                            <Badge variant="secondary" className="text-xs">
                              +{item.detections.length - 3}
                            </Badge>
                          )}
                        </div>
                      )}

                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {formatAnalysis(item)}
                      </p>

                      {item.emotion && (
                        <div className="pt-2 border-t border-border">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-medium text-muted-foreground">Emotion:</span>
                            <Badge variant="default" className="text-xs">
                              {item.emotion.toUpperCase()}
                            </Badge>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {hasChat && (
                      <div className="pt-2 border-t border-border">
                        <p className="text-xs text-muted-foreground italic">
                          Click to view and continue chat
                        </p>
                      </div>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
