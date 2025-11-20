'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { ImageAnalysisHistoryItem } from '@/types/api';
import { getUserAnalyses } from '@/lib/api';

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
      parts.push(`Detections: ${item.detections.length} body parts`);
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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <div className="text-center">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={fetchAnalyses}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

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
              <p className="text-3xl font-bold text-indigo-900">{total}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-green-600 font-medium">Analyses</p>
              <p className="text-3xl font-bold text-green-900">{total}</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-purple-600 font-medium">Emotions Detected</p>
              <p className="text-3xl font-bold text-purple-900">
                {new Set(analyses.map(item => item.emotion).filter(Boolean)).size}
              </p>
            </div>
          </div>

          {/* Image Grid */}
          {analyses.length === 0 ? (
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
              {analyses.map((item) => (
                <div
                  key={item.id}
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
                      {item.filename}
                    </h3>
                    <p className="text-xs text-gray-500 mb-3">
                      {formatDate(item.created_at)}
                    </p>

                    {/* Analysis Summary */}
                    <div className="space-y-2">
                      <div className="flex flex-wrap gap-1">
                        {item.detections.map((det, idx) => (
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
                        {formatAnalysis(item)}
                      </p>

                      {item.emotion && (
                        <div className="pt-2 border-t border-gray-200">
                          <span className="text-xs font-semibold text-gray-600">Emotion: </span>
                          <span className="text-sm font-bold text-indigo-600 uppercase">
                            {item.emotion}
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

