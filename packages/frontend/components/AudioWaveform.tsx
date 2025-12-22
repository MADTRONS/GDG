'use client';

import { useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

interface AudioWaveformProps {
  className?: string;
}

export default function AudioWaveform({ className }: AudioWaveformProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const width = canvas.offsetWidth || 256;
    const height = canvas.offsetHeight || 128;
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    // Waveform animation
    const bars = 32;
    const barWidth = width / bars;
    const barGap = 2;
    const heights = Array(bars).fill(0).map(() => Math.random());

    const animate = () => {
      ctx.clearRect(0, 0, width, height);
      
      heights.forEach((_, i) => {
        // Animate heights
        heights[i] += (Math.random() - 0.5) * 0.1;
        heights[i] = Math.max(0.1, Math.min(1, heights[i]));
        
        const barHeight = heights[i] * height * 0.8;
        const x = i * barWidth;
        const y = (height - barHeight) / 2;
        
        // Gradient from blue to purple
        const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
        gradient.addColorStop(0, '#3b82f6'); // blue-500
        gradient.addColorStop(1, '#8b5cf6'); // violet-500
        
        ctx.fillStyle = gradient;
        ctx.fillRect(x + barGap, y, barWidth - barGap * 2, barHeight);
      });
      
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={cn('rounded-lg bg-gray-800', className)}
    />
  );
}
