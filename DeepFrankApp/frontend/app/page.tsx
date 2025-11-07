'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import { analyzeImage } from '@/lib/api';
import { DetectionResponse } from '@/types/api';

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [imageSize, setImageSize] = useState<{ width: number; height: number } | null>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setResult(null);
      setImageSize(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleImageLoad = () => {
    if (imageRef.current) {
      setImageSize({
        width: imageRef.current.naturalWidth,
        height: imageRef.current.naturalHeight,
      });
    }
  };

  const getBoundingBoxStyle = (bbox: [number, number, number, number]) => {
    if (!imageRef.current || !imageSize) return {};
    
    const displayedWidth = imageRef.current.clientWidth;
    const displayedHeight = imageRef.current.clientHeight;
    
    const scaleX = displayedWidth / imageSize.width;
    const scaleY = displayedHeight / imageSize.height;
    
    const [x1, y1, x2, y2] = bbox;
    
    return {
      position: 'absolute' as const,
      left: `${x1 * scaleX}px`,
      top: `${y1 * scaleY}px`,
      width: `${(x2 - x1) * scaleX}px`,
      height: `${(y2 - y1) * scaleY}px`,
    };
  };

  const getBoxColor = (className: string): string => {
    const colors: Record<string, string> = {
      eye: 'rgba(255, 0, 0, 0.3)',      // Red with transparency
      mouth: 'rgba(0, 255, 0, 0.3)',    // Green with transparency
      tail: 'rgba(0, 0, 255, 0.3)',     // Blue with transparency
    };
    return colors[className] || 'rgba(255, 255, 0, 0.3)';
  };

  const getBoxBorderColor = (className: string): string => {
    const colors: Record<string, string> = {
      eye: '#ef4444',      // Red
      mouth: '#22c55e',   // Green
      tail: '#3b82f6',    // Blue
    };
    return colors[className] || '#eab308';
  };

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

  const formatAnalysis = (result: DetectionResponse): string => {
    const parts: string[] = [];

    // Detections
    if (result.detections.length > 0) {
      parts.push('=== Detected Body Parts ===');
      result.detections.forEach((det, idx) => {
        parts.push(
          `${idx + 1}. ${det.class_name.toUpperCase()} (confidence: ${(det.confidence * 100).toFixed(1)}%)`
        );
        parts.push(`   Bounding box: [${det.bbox.join(', ')}]`);
      });
    } else {
      parts.push('=== No body parts detected ===');
    }

    // Analysis
    if (result.analysis) {
      parts.push('\n=== Body Part Analysis ===');
      const analysis = result.analysis;
      
      if (analysis.eye_state) {
        parts.push(`Eyes: ${analysis.eye_state}, your cat's eyes are closed, it's probably sleeping or relaxed.`);
      }
      if (analysis.mouth_state) {
        parts.push(`Mouth: ${analysis.mouth_state}, hmmm, the mouth looks a little strange, please upload a clearer photo.`);
      }
      if (analysis.tail_position) {
        parts.push(`Tail Position: ${analysis.tail_position}`);
        if (analysis.tail_angle !== null) {
          parts.push(`Tail Angle: ${analysis.tail_angle.toFixed(1)}°`);
        }
      }
    }

    // Emotion
    if (result.emotion) {
      parts.push(`\n=== Emotional State ===`);
      parts.push(`Emotion: ${result.emotion.toUpperCase()}`);
    }

    return parts.join('\n');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Navigation */}
          <div className="flex justify-end gap-4 mb-6">
            <Link
              href="/profile"
              className="px-4 py-2 text-indigo-600 font-semibold rounded-lg
                hover:bg-indigo-50 transition-colors duration-200"
            >
              My Profile
            </Link>
            <Link
              href="/vets"
              className="px-4 py-2 text-indigo-600 font-semibold rounded-lg
                hover:bg-indigo-50 transition-colors duration-200"
            >
              Vets & Products
            </Link>
          </div>

          <h1 className="text-4xl font-bold text-center text-gray-900 mb-2">
            DeepFrank Cat Analysis
          </h1>
          <p className="text-center text-gray-600 mb-8">
            Upload a cat image to analyze emotional state
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File Input */}
            <div>
              <label
                htmlFor="image-upload"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Select Cat Image
              </label>
              <input
                id="image-upload"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-lg file:border-0
                  file:text-sm file:font-semibold
                  file:bg-indigo-50 file:text-indigo-700
                  hover:file:bg-indigo-100
                  cursor-pointer"
                disabled={loading}
              />
            </div>

            {/* Preview with Bounding Boxes */}
            {preview && (
              <div className="flex justify-center">
                <div className="relative inline-block">
                  <img
                    ref={imageRef}
                    src={preview}
                    alt="Preview"
                    className="max-w-full h-auto max-h-96 rounded-lg shadow-md"
                    onLoad={handleImageLoad}
                  />
                  {/* Bounding Box Overlay */}
                  {result && result.detections.length > 0 && imageSize && (
                    <div className="absolute inset-0 pointer-events-none">
                      {result.detections.map((detection, idx) => (
                        <div
                          key={idx}
                          style={{
                            ...getBoundingBoxStyle(detection.bbox),
                            border: `3px solid ${getBoxBorderColor(detection.class_name)}`,
                            backgroundColor: getBoxColor(detection.class_name),
                            borderRadius: '4px',
                          }}
                        >
                          <div
                            className="absolute -top-7 left-0 px-2 py-1 text-xs font-bold text-white rounded"
                            style={{
                              backgroundColor: getBoxBorderColor(detection.class_name),
                            }}
                          >
                            {detection.class_name.toUpperCase()} {(detection.confidence * 100).toFixed(0)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={!selectedFile || loading}
              className="w-full py-3 px-4 bg-indigo-600 text-white font-semibold rounded-lg
                hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500
                focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed
                transition-colors duration-200"
            >
              {loading ? 'Analyzing...' : 'Analyze Image'}
            </button>
          </form>

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 font-medium">Error:</p>
              <p className="text-red-600">{error}</p>
            </div>
          )}

          {/* Results Display */}
          {result && (
            <div className="mt-6 p-6 bg-gray-50 border border-gray-200 rounded-lg">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Analysis Results</h2>
              <pre className="whitespace-pre-wrap font-mono text-sm text-gray-800 bg-white p-4 rounded border border-gray-300 overflow-x-auto">
                {formatAnalysis(result)}
              </pre>
            </div>
          )}

          {/* Chat with Frankie */}
          {result && (
            <div className="mt-6 p-6 bg-white border border-gray-200 rounded-lg shadow-md">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center mr-3">
                  <span className="text-white font-bold text-lg">F</span>
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Chat with Frankie</h2>
                  <p className="text-sm text-gray-500">Your AI cat health assistant</p>
                </div>
              </div>

              <div className="space-y-4 mt-4">
                {/* User Message */}
                <div className="flex justify-end">
                  <div className="max-w-[80%] bg-indigo-600 text-white rounded-lg px-4 py-2 rounded-tr-none">
                    <p className="text-sm">Does my cat look healthy?</p>
                  </div>
                </div>

                {/* AI Message */}
                <div className="flex justify-start">
                  <div className="max-w-[80%] bg-gray-100 text-gray-900 rounded-lg px-4 py-2 rounded-tl-none">
                    <p className="text-sm">Your cat seems to be in a relaxed position.</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

