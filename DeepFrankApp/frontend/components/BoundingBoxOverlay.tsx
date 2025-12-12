'use client';

import { useEffect, useState, useRef } from 'react';
import { BodyPartDetection } from '@/types/api';

interface BoundingBoxOverlayProps {
  imageSrc: string;
  detections: BodyPartDetection[];
  className?: string;
}

// Color mapping for different body parts
const CLASS_COLORS: Record<string, string> = {
  eye: '#3b82f6', // blue
  tail: '#10b981', // green
  mouth: '#f59e0b', // amber
};

export function BoundingBoxOverlay({ imageSrc, detections, className = '' }: BoundingBoxOverlayProps) {
  const [imageDimensions, setImageDimensions] = useState<{ width: number; height: number } | null>(null);
  const [displayDimensions, setDisplayDimensions] = useState<{ width: number; height: number } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      setImageDimensions({ width: img.width, height: img.height });
    };
    img.src = imageSrc;
  }, [imageSrc]);

  useEffect(() => {
    const updateDisplayDimensions = () => {
      if (imageRef.current && imageDimensions) {
        const displayWidth = imageRef.current.clientWidth;
        const displayHeight = imageRef.current.clientHeight;
        setDisplayDimensions({ width: displayWidth, height: displayHeight });
      }
    };

    updateDisplayDimensions();

    const resizeObserver = new ResizeObserver(updateDisplayDimensions);
    if (imageRef.current) {
      resizeObserver.observe(imageRef.current);
    }

    window.addEventListener('resize', updateDisplayDimensions);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener('resize', updateDisplayDimensions);
    };
  }, [imageDimensions]);

  if (!imageDimensions || !displayDimensions || detections.length === 0) {
    return (
      <div className={`relative inline-block ${className}`}>
        <img
          ref={imageRef}
          src={imageSrc}
          alt="Preview"
          className="max-w-full h-auto max-h-96 rounded-lg shadow-lg"
        />
      </div>
    );
  }

  // Calculate scale factors
  const scaleX = displayDimensions.width / imageDimensions.width;
  const scaleY = displayDimensions.height / imageDimensions.height;

  return (
    <div ref={containerRef} className={`relative inline-block ${className}`}>
      <img
        ref={imageRef}
        src={imageSrc}
        alt="Preview"
        className="max-w-full h-auto max-h-96 rounded-lg shadow-lg"
      />
      <svg
        className="absolute top-0 left-0 pointer-events-none"
        style={{
          width: displayDimensions.width,
          height: displayDimensions.height,
        }}
      >
        {detections.map((detection, index) => {
          const [x1, y1, x2, y2] = detection.bbox;
          const scaledX1 = x1 * scaleX;
          const scaledY1 = y1 * scaleY;
          const scaledX2 = x2 * scaleX;
          const scaledY2 = y2 * scaleY;
          const width = scaledX2 - scaledX1;
          const height = scaledY2 - scaledY1;

          const color = CLASS_COLORS[detection.class_name] || '#6b7280';
          const confidencePercent = (detection.confidence * 100).toFixed(1);

          return (
            <g key={index}>
              {/* Bounding box rectangle */}
              <rect
                x={scaledX1}
                y={scaledY1}
                width={width}
                height={height}
                fill="none"
                stroke={color}
                strokeWidth="2"
                strokeDasharray="4 4"
              />
              {/* Label background */}
              <rect
                x={scaledX1}
                y={scaledY1 - 20}
                width={Math.max(80, detection.class_name.length * 8 + 50)}
                height={20}
                fill={color}
                opacity={0.9}
              />
              {/* Label text */}
              <text
                x={scaledX1 + 4}
                y={scaledY1 - 6}
                fill="white"
                fontSize="12"
                fontWeight="bold"
              >
                {detection.class_name} {confidencePercent}%
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

