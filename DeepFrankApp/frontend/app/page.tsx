'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { analyzeImage } from '@/lib/api';
import { ImageAnalysisResponse } from '@/types/api';
import { useAuth } from '@/contexts/AuthContext';
import { MarkdownRenderer } from '@/components/MarkdownRenderer';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload, Image as ImageIcon, Loader2, MessageSquare, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function Home() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImageAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (file: File) => {
    setSelectedFile(file);
    setError(null);
    setResult(null);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileChange(file);
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      handleFileChange(file);
    } else {
      setError('Please drop a valid image file');
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setError('Please select an image file');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await analyzeImage(selectedFile);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze image');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold text-foreground">Cat Analysis</h1>
          <p className="text-muted-foreground">
            Upload a cat image to analyze emotional state and get insights
          </p>
        </div>

        {/* Upload Form */}
        <Card className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Drag and Drop Zone */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => {
                if (!preview && !loading) {
                  document.getElementById('image-upload')?.click();
                }
              }}
              className={`
                relative border-2 border-dashed rounded-lg p-12 text-center transition-colors
                ${isDragging 
                  ? 'border-primary bg-primary/5' 
                  : 'border-border hover:border-primary/50'
                }
                ${preview ? 'p-4 cursor-default' : 'cursor-pointer'}
                ${loading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <input
                id="image-upload"
                type="file"
                accept="image/*"
                onChange={handleFileInputChange}
                className="hidden"
                disabled={loading}
              />
              {preview ? (
                <div className="space-y-4" onClick={(e) => e.stopPropagation()}>
                  <div className="relative inline-block">
                    <img
                      src={preview}
                      alt="Preview"
                      className="max-w-full h-auto max-h-96 rounded-lg shadow-lg"
                    />
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setPreview(null);
                        setSelectedFile(null);
                        setResult(null);
                      }}
                      className="absolute top-2 right-2 p-2 bg-background/80 backdrop-blur-sm rounded-full hover:bg-background transition-colors"
                    >
                      <span className="sr-only">Remove image</span>
                      ×
                    </button>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {selectedFile?.name}
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center space-y-4">
                  <div className="p-4 bg-primary/10 rounded-full">
                    <Upload className="h-8 w-8 text-primary" />
                  </div>
                  <div className="space-y-2">
                    <p className="text-lg font-medium text-foreground">
                      Drag and drop your image here
                    </p>
                    <p className="text-sm text-muted-foreground">
                      or click anywhere to browse
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    className="cursor-pointer"
                    disabled={loading}
                    onClick={(e) => {
                      e.stopPropagation();
                      document.getElementById('image-upload')?.click();
                    }}
                  >
                    <ImageIcon className="mr-2 h-4 w-4" />
                    Select Image
                  </Button>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={!selectedFile || loading}
              className="w-full"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <ImageIcon className="mr-2 h-4 w-4" />
                  Analyze Image
                </>
              )}
            </Button>
          </form>
        </Card>

        {/* Error Display */}
        {error && (
          <Card className="p-6 border-destructive bg-destructive/10">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-destructive mb-1">Error</h3>
                <p className="text-sm text-destructive/80">{error}</p>
              </div>
            </div>
          </Card>
        )}

        {/* Results Display */}
        {result && (
          <Card className="p-6 space-y-4">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">Analysis Results</h2>
            </div>
            <div className="p-4 bg-muted rounded-lg border">
              <MarkdownRenderer content={result.analysis_text} />
            </div>
          </Card>
        )}

        {/* Open Chat Button */}
        {result && result.chat_session_id && isAuthenticated && (
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                  <span className="text-primary-foreground font-bold text-lg">F</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-foreground">Chat with Frankie</h3>
                  <p className="text-sm text-muted-foreground">
                    Get insights about your cat's analysis
                  </p>
                </div>
              </div>
              <Button
                onClick={() => {
                  sessionStorage.setItem('analysisForChat', JSON.stringify(result));
                  router.push(`/chat/${result.chat_session_id}`);
                }}
                size="lg"
              >
                <MessageSquare className="mr-2 h-4 w-4" />
                Open Chat
              </Button>
            </div>
          </Card>
        )}

        {/* Sign in prompt */}
        {result && !isAuthenticated && (
          <Card className="p-6 bg-primary/5 border-primary/20">
            <div className="flex items-center justify-between gap-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-foreground mb-1">
                  Want to save your chat history?
                </h3>
                <p className="text-sm text-muted-foreground">
                  Sign in to continue conversations about your cat's analysis and access your analysis history.
                </p>
              </div>
              <Link href="/login">
                <Button size="lg">
                  Sign In
                </Button>
              </Link>
            </div>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
