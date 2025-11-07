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
}

