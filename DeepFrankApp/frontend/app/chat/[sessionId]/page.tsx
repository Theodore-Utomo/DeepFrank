'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { getChatMessages, sendChatMessage } from '@/lib/api';
import { ImageAnalysisResponse, ChatMessage, ChatMessageRequest } from '@/types/api';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MarkdownRenderer } from '@/components/MarkdownRenderer';
import { Loader2, Send, MessageSquare } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

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
  const [analysisData, setAnalysisData] = useState<ImageAnalysisResponse | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasSentInitialMessage = useRef(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
      return;
    }

    const storedAnalysis = sessionStorage.getItem('analysisForChat');
    if (storedAnalysis) {
      try {
        const parsed = JSON.parse(storedAnalysis);
        setAnalysisData(parsed);
        sessionStorage.removeItem('analysisForChat');
      } catch (e) {
        // Failed to parse analysis data
      }
    }

    if (isAuthenticated && sessionId) {
      loadMessages();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, authLoading, sessionId]);

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
    } finally {
      setLoading(false);
    }
  };

  const sendInitialAnalysisMessage = async () => {
    if (!analysisData) return;

    const messageContent = `Here are my image analysis results:\n\n${analysisData.analysis_text}`;

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
      
      await sendChatMessage(messageRequest);
      await loadMessages();
    } catch (err) {
      setMessages((prev) => prev.filter(msg => msg.id !== optimisticUserMessage.id));
      setError(err instanceof Error ? err.message : 'Failed to send initial message');
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
      
      await sendChatMessage(messageRequest);
      await loadMessages();
    } catch (err) {
      setMessages((prev) => prev.filter(msg => msg.id !== optimisticUserMessage.id));
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  if (authLoading || loading) {
    return (
      <DashboardLayout>
        <div className="max-w-4xl mx-auto space-y-4">
          <Skeleton className="h-12 w-64" />
          <Skeleton className="h-96 w-full" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto flex flex-col" style={{ minHeight: 'calc(100vh - 12rem)' }}>
        {/* Header */}
        <div className="mb-6 space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-lg">F</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Chat with Frankie</h1>
              <p className="text-sm text-muted-foreground">Your AI cat health assistant</p>
            </div>
          </div>
        </div>

        {/* Messages Container */}
        <ScrollArea className="flex-1 mb-4">
          <div className="space-y-4 pr-4">
            {messages.length === 0 && !sending && !error && (
              <div className="text-center py-12 text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>{analysisData ? 'Sending analysis results...' : 'Start a conversation with Frankie!'}</p>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <Card
                  className={`max-w-[80%] ${
                    message.sender === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-card'
                  }`}
                >
                  <div className="px-4 py-3">
                    {message.sender === 'assistant' ? (
                      <MarkdownRenderer content={message.content} />
                    ) : (
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    )}
                    <p className={`text-xs mt-2 ${
                      message.sender === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'
                    }`}>
                      {new Date(message.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </Card>
              </div>
            ))}

            {sending && (
              <div className="flex justify-start">
                <Card>
                  <div className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Frankie is typing...</span>
                    </div>
                  </div>
                </Card>
              </div>
            )}

            {error && (
              <Card className="border-destructive bg-destructive/10">
                <div className="px-4 py-3">
                  <p className="text-destructive font-medium text-sm">Error:</p>
                  <p className="text-destructive/80 text-sm">{error}</p>
                </div>
              </Card>
            )}

            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input Form */}
        <Card className="p-4">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <Input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={sending}
              className="flex-1"
            />
            <Button
              type="submit"
              disabled={!inputMessage.trim() || sending}
              size="icon"
            >
              {sending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </Card>
      </div>
    </DashboardLayout>
  );
}
