/**
 * API types for DeepFrank backend
 */

export interface BodyPartDetection {
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number]; // [x1, y1, x2, y2]
}

export interface AnalysisResult {
  eye_state: string | null;
  mouth_state: string | null;
  tail_position: string | null;
  tail_angle: number | null;
}

export interface DetectionResponse {
  detections: BodyPartDetection[];
  analysis: AnalysisResult | null;
  emotion: string | null;
  chat_session_id: string | null;
}

export interface ImageAnalysisResponse {
  analysis_text: string;
  chat_session_id: string | null;
}

// Authentication types
export interface User {
  id: string;
  email: string;
  stytch_user_id: string;
  created_at: string | null;
}

export interface AuthResponse {
  session_token: string;
  user: User;
}

export interface SessionResponse {
  user: User;
  session_id: string | null;
  expires_at: string | null;
}

export interface MagicLinkSendResponse {
  status: string;
  message: string;
  email_id: string | null;
}

// Profile types
export interface ImageAnalysisHistoryItem {
  id: string;
  filename: string;
  detections: BodyPartDetection[];
  analysis: AnalysisResult | null;
  emotion: string | null;
  chat_session_id: string | null;
  created_at: string;
}

export interface UserAnalysesResponse {
  analyses: ImageAnalysisHistoryItem[];
  total: number;
}

// Chat types
export interface ChatSession {
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  sender: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessageRequest {
  session_id: string;
  content: string;
}

