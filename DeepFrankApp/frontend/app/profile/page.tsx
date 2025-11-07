'use client';

import Link from 'next/link';
import { DetectionResponse } from '@/types/api';

// Mock data for uploaded images and their analyses
const mockUploadedImages = [
  {
    id: '1',
    imageUrl: '/api/placeholder/400/300', // Using placeholder for now
    fileName: 'cat_analysis_1.jpg',
    uploadedAt: '2024-01-15T10:30:00Z',
    analysis: {
      detections: [
        {
          class_name: 'eye',
          confidence: 0.85,
          bbox: [100, 150, 200, 250] as [number, number, number, number],
        },
        {
          class_name: 'mouth',
          confidence: 0.78,
          bbox: [180, 280, 250, 320] as [number, number, number, number],
        },
      ],
      analysis: {
        eye_state: 'wide_open',
        mouth_state: 'closed',
        tail_position: null,
        tail_angle: null,
      },
      emotion: 'alert',
    } as DetectionResponse,
  },
  {
    id: '2',
    imageUrl: '/api/placeholder/400/300',
    fileName: 'cat_analysis_2.jpg',
    uploadedAt: '2024-01-14T14:20:00Z',
    analysis: {
      detections: [
        {
          class_name: 'eye',
          confidence: 0.92,
          bbox: [120, 140, 220, 240] as [number, number, number, number],
        },
        {
          class_name: 'tail',
          confidence: 0.88,
          bbox: [300, 400, 350, 600] as [number, number, number, number],
        },
      ],
      analysis: {
        eye_state: 'normal',
        mouth_state: null,
        tail_position: 'up',
        tail_angle: 45.0,
      },
      emotion: 'content',
    } as DetectionResponse,
  },
  {
    id: '3',
    imageUrl: '/api/placeholder/400/300',
    fileName: 'cat_analysis_3.jpg',
    uploadedAt: '2024-01-13T09:15:00Z',
    analysis: {
      detections: [
        {
          class_name: 'eye',
          confidence: 0.75,
          bbox: [150, 180, 240, 280] as [number, number, number, number],
        },
        {
          class_name: 'mouth',
          confidence: 0.82,
          bbox: [200, 300, 280, 350] as [number, number, number, number],
        },
        {
          class_name: 'tail',
          confidence: 0.79,
          bbox: [320, 450, 380, 620] as [number, number, number, number],
        },
      ],
      analysis: {
        eye_state: 'closed',
        mouth_state: 'closed',
        tail_position: 'down',
        tail_angle: 135.0,
      },
      emotion: 'sleepy',
    } as DetectionResponse,
  },
];

export default function ProfilePage() {
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

  const formatAnalysis = (analysis: DetectionResponse): string => {
    const parts: string[] = [];

    if (analysis.detections.length > 0) {
      parts.push(`Detections: ${analysis.detections.length} body parts`);
    }

    if (analysis.analysis) {
      const a = analysis.analysis;
      if (a.eye_state) parts.push(`Eyes: ${a.eye_state}`);
      if (a.mouth_state) parts.push(`Mouth: ${a.mouth_state}`);
      if (a.tail_position) parts.push(`Tail: ${a.tail_position}`);
    }

    if (analysis.emotion) {
      parts.push(`Emotion: ${analysis.emotion}`);
    }

    return parts.join(' • ');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Header */}
          <div className="mb-6">
            <Link
              href="/"
              className="inline-flex items-center text-indigo-600 hover:text-indigo-700 font-medium mb-4
                transition-colors duration-200"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              Back to Home
            </Link>
          </div>
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                My Profile
              </h1>
              <p className="text-gray-600">
                View your uploaded cat images and analysis history
              </p>
            </div>
            <div className="flex gap-4">
              <Link
                href="/vets"
                className="px-4 py-2 text-indigo-600 font-semibold rounded-lg
                  hover:bg-indigo-50 transition-colors duration-200"
              >
                Vets & Products
              </Link>
              <Link
                href="/"
                className="px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg
                  hover:bg-indigo-700 transition-colors duration-200"
              >
                Upload New
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-indigo-50 rounded-lg p-4">
              <p className="text-sm text-indigo-600 font-medium">Total Images</p>
              <p className="text-3xl font-bold text-indigo-900">{mockUploadedImages.length}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-green-600 font-medium">Analyses</p>
              <p className="text-3xl font-bold text-green-900">{mockUploadedImages.length}</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-purple-600 font-medium">Emotions Detected</p>
              <p className="text-3xl font-bold text-purple-900">
                {new Set(mockUploadedImages.map(img => img.analysis.emotion).filter(Boolean)).size}
              </p>
            </div>
          </div>

          {/* Image Grid */}
          {mockUploadedImages.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg mb-4">No images uploaded yet</p>
              <Link
                href="/"
                className="inline-block px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg
                  hover:bg-indigo-700 transition-colors duration-200"
              >
                Upload Your First Image
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mockUploadedImages.map((image) => (
                <div
                  key={image.id}
                  className="bg-gray-50 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
                >
                  {/* Image Placeholder */}
                  <div className="w-full h-48 bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center">
                    <svg
                      className="w-16 h-16 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                  </div>

                  {/* Image Info */}
                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900 mb-1 truncate">
                      {image.fileName}
                    </h3>
                    <p className="text-xs text-gray-500 mb-3">
                      {formatDate(image.uploadedAt)}
                    </p>

                    {/* Analysis Summary */}
                    <div className="space-y-2">
                      <div className="flex flex-wrap gap-1">
                        {image.analysis.detections.map((det, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 text-xs font-medium rounded
                              bg-indigo-100 text-indigo-800"
                          >
                            {det.class_name}
                          </span>
                        ))}
                      </div>

                      <p className="text-sm text-gray-700 line-clamp-2">
                        {formatAnalysis(image.analysis)}
                      </p>

                      {image.analysis.emotion && (
                        <div className="pt-2 border-t border-gray-200">
                          <span className="text-xs font-semibold text-gray-600">Emotion: </span>
                          <span className="text-sm font-bold text-indigo-600 uppercase">
                            {image.analysis.emotion}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

