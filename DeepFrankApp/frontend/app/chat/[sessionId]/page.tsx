'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { getChatMessages, sendChatMessage } from '@/lib/api';
import { DetectionResponse, ChatMessage, ChatMessageRequest } from '@/types/api';

export default function ChatPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const sessionId = params.sessionId as string;
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<DetectionResponse | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasSentInitialMessage = useRef(false);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
      return;
    }

    // Load analysis data from sessionStorage if available
    const storedAnalysis = sessionStorage.getItem('analysisForChat');
    if (storedAnalysis) {
      try {
        const parsed = JSON.parse(storedAnalysis);
        setAnalysisData(parsed);
        sessionStorage.removeItem('analysisForChat'); // Clear after reading
      } catch (e) {
        console.error('Failed to parse analysis data:', e);
      }
    }

    // Load messages if authenticated
    if (isAuthenticated && sessionId) {
      loadMessages();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, authLoading, sessionId]);

  // Separate effect to send initial message after analysisData is set and messages are loaded
  useEffect(() => {
    if (analysisData && !hasSentInitialMessage.current && messages.length === 0 && !loading && isAuthenticated) {
      hasSentInitialMessage.current = true;
      sendInitialAnalysisMessage();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [analysisData, messages.length, loading, isAuthenticated]);

  const loadMessages = async () => {
    try {
      setLoading(true);
      setError(null);
      const loadedMessages = await getChatMessages(sessionId);
      setMessages(loadedMessages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load messages');
      console.error('Error loading messages:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatAnalysisForMessage = (analysis: DetectionResponse): string => {
    const parts: string[] = [];

    // Detections
    if (analysis.detections.length > 0) {
      parts.push('=== Detected Body Parts ===');
      analysis.detections.forEach((det, idx) => {
        parts.push(
          `${idx + 1}. ${det.class_name.toUpperCase()} (confidence: ${(det.confidence * 100).toFixed(1)}%)`
        );
        parts.push(`   Bounding box: [${det.bbox.join(', ')}]`);
      });
    } else {
      parts.push('=== No body parts detected ===');
    }

    // Analysis
    if (analysis.analysis) {
      parts.push('\n=== Body Part Analysis ===');
      const analysisResult = analysis.analysis;
      
      if (analysisResult.eye_state) {
        parts.push(`Eyes: ${analysisResult.eye_state}`);
      }
      if (analysisResult.mouth_state) {
        parts.push(`Mouth: ${analysisResult.mouth_state}`);
      }
      if (analysisResult.tail_position) {
        parts.push(`Tail Position: ${analysisResult.tail_position}`);
        if (analysisResult.tail_angle !== null) {
          parts.push(`Tail Angle: ${analysisResult.tail_angle.toFixed(1)}°`);
        }
      }
    }

    // Emotion
    if (analysis.emotion) {
      parts.push(`\n=== Emotional State ===`);
      parts.push(`Emotion: ${analysis.emotion.toUpperCase()}`);
    }

    return parts.join('\n');
  };

  const sendInitialAnalysisMessage = async () => {
    if (!analysisData) return;

    const analysisText = formatAnalysisForMessage(analysisData);
    const messageContent = `Here are my image analysis results:\n\n${analysisText}`;

    // Optimistically add user message to UI immediately
    const optimisticUserMessage: ChatMessage = {
      id: `temp-initial-${Date.now()}`,
      session_id: sessionId,
      sender: 'user',
      content: messageContent,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUserMessage]);

    try {
      setSending(true);
      const messageRequest: ChatMessageRequest = {
        session_id: sessionId,
        content: messageContent,
      };
      
      // Send message - this will save user message and return AI response
      const aiResponse = await sendChatMessage(messageRequest);
      
      // Reload messages to get the actual user message (with real ID) and AI response
      // This replaces the optimistic message with the real one
      await loadMessages();
    } catch (err) {
      // Remove optimistic message on error
      setMessages((prev) => prev.filter(msg => msg.id !== optimisticUserMessage.id));
      setError(err instanceof Error ? err.message : 'Failed to send initial message');
      console.error('Error sending initial message:', err);
    } finally {
      setSending(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || sending) return;

    const messageContent = inputMessage.trim();
    setInputMessage('');
    setError(null);

    // Optimistically add user message to UI immediately
    const optimisticUserMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      session_id: sessionId,
      sender: 'user',
      content: messageContent,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUserMessage]);

    try {
      setSending(true);
      const messageRequest: ChatMessageRequest = {
        session_id: sessionId,
        content: messageContent,
      };
      
      // Send message - this will save user message and return AI response
      const aiResponse = await sendChatMessage(messageRequest);
      
      // Reload messages to get the actual user message (with real ID) and AI response
      // This replaces the optimistic message with the real one
      await loadMessages();
    } catch (err) {
      // Remove optimistic message on error
      setMessages((prev) => prev.filter(msg => msg.id !== optimisticUserMessage.id));
      setError(err instanceof Error ? err.message : 'Failed to send message');
      console.error('Error sending message:', err);
    } finally {
      setSending(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl font-semibold text-gray-700">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="text-indigo-600 hover:text-indigo-700 font-semibold"
              >
                ← Back to Home
              </Link>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-lg">F</span>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Chat with Frankie</h1>
                  <p className="text-sm text-gray-500">Your AI cat health assistant</p>
                </div>
              </div>
            </div>
            {user && (
              <div className="text-sm text-gray-600">
                <span className="font-medium">{user.email}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto max-w-4xl w-full mx-auto px-4 py-6">
        <div className="space-y-4">
          {messages.length === 0 && !sending && !error && (
            <div className="text-center text-gray-500 py-8">
              {analysisData ? 'Sending analysis results...' : 'Start a conversation with Frankie!'}
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.sender === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'bg-white text-gray-900 rounded-tl-none shadow-sm border border-gray-200'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                <p className={`text-xs mt-1 ${
                  message.sender === 'user' ? 'text-indigo-200' : 'text-gray-400'
                }`}>
                  {new Date(message.created_at).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}

          {sending && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-900 rounded-lg px-4 py-2 rounded-tl-none shadow-sm border border-gray-200">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 font-medium">Error:</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form */}
      <div className="bg-white border-t border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              disabled={sending}
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || sending}
              className="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg
                hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500
                focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed
                transition-colors duration-200"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

