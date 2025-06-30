/**
 * Advanced OCR Parser Service
 * Handles image preprocessing, Tesseract JSON parsing, word clustering, and Google Vision fallback
 */
import { Jimp } from 'jimp';
import Tesseract from 'tesseract.js';
import { ImageAnnotatorClient } from '@google-cloud/vision';
import { getEnv } from '../utils/env';
import { TesseractData } from '../types';

export interface Word {
  text: string;
  confidence: number;
  bbox: {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
  };
}

export interface ClusteredLine {
  text: string;
  confidence: number;
  words: Word[];
}

export interface OCRParserResult {
  lines: ClusteredLine[];
  averageConfidence: number;
  imageDimensions: { width: number; height: number };
  usedFallback: boolean;
}

/**
 * Preprocess image for better OCR accuracy
 * @param buffer - Raw image buffer
 * @returns Promise<Buffer> - Preprocessed image buffer
 */
export async function preprocess(buffer: Buffer): Promise<Buffer> {
  console.log('🔄 Starting image preprocessing...');
  
  try {
    const image = await Jimp.read(buffer);
    const originalWidth = image.width;
    const originalHeight = image.height;
    
    console.log(`📏 Original dimensions: ${originalWidth}x${originalHeight}`);
    
    // Resize to ~1000px height while maintaining aspect ratio
    const targetHeight = 1000;
    const scale = targetHeight / originalHeight;
    const newWidth = Math.round(originalWidth * scale);
    
    image.resize({ w: newWidth, h: targetHeight });
    console.log(`📏 Resized to: ${newWidth}x${targetHeight}`);
    
    // Convert to grayscale
    image.greyscale();
    
    // Boost contrast
    image.contrast(0.3);
    
    // Normalize brightness
    image.normalize();
    
    // Apply slight gaussian blur to reduce noise (only if image is large enough)
    if (image.width > 1 && image.height > 1) {
      image.gaussian(1);
    }
    
    // Apply threshold to create binary image
    image.threshold({ max: 128 });
    
    const processedBuffer = await image.getBuffer('image/png');
    console.log('✅ Image preprocessing completed');
    
    return processedBuffer;
  } catch (error) {
    console.error('❌ Image preprocessing failed:', error);
    throw new Error(`Image preprocessing failed: ${error}`);
  }
}

/**
 * Cluster words into lines based on Y-coordinate proximity
 * @param words - Array of Tesseract word objects
 * @param thresholdPx - Y-coordinate threshold for clustering (default: 10px)
 * @returns ClusteredLine[] - Array of clustered text lines
 */
export function clusterByY(words: Word[], thresholdPx: number = 10): ClusteredLine[] {
  console.log(`🔍 Clustering ${words.length} words with ${thresholdPx}px threshold...`);
  
  if (words.length === 0) {
    return [];
  }
  
  // Sort words by Y-coordinate
  const sortedWords = [...words].sort((a, b) => a.bbox.y0 - b.bbox.y0);
  
  const clusters: ClusteredLine[] = [];
  let currentCluster: Word[] = [sortedWords[0]!];
  let currentY = sortedWords[0]!.bbox.y0;
  
  for (let i = 1; i < sortedWords.length; i++) {
    const word = sortedWords[i]!;
    const yDiff = Math.abs(word.bbox.y0 - currentY);
    
    if (yDiff <= thresholdPx) {
      // Add to current cluster
      currentCluster.push(word);
    } else {
      // Start new cluster
      if (currentCluster.length > 0) {
        clusters.push(createClusteredLine(currentCluster));
      }
      currentCluster = [word];
      currentY = word.bbox.y0;
    }
  }
  
  // Add final cluster
  if (currentCluster.length > 0) {
    clusters.push(createClusteredLine(currentCluster));
  }
  
  console.log(`✅ Created ${clusters.length} text clusters`);
  return clusters;
}

/**
 * Create a clustered line from an array of words
 * @param words - Array of words in the same line
 * @returns ClusteredLine - Structured line with text and confidence
 */
function createClusteredLine(words: Word[]): ClusteredLine {
  // Sort words by X-coordinate for proper text order
  const sortedWords = [...words].sort((a, b) => a.bbox.x0 - b.bbox.x0);
  
  const text = sortedWords.map(w => w.text).join(' ');
  const totalConfidence = sortedWords.reduce((sum, w) => sum + w.confidence, 0);
  const averageConfidence = totalConfidence / sortedWords.length;
  
  return {
    text,
    confidence: averageConfidence,
    words: sortedWords
  };
}

/**
 * Parse Tesseract JSON output and filter low-confidence words
 * @param data - Tesseract recognition result
 * @param minConfidence - Minimum confidence threshold (default: 60)
 * @returns Word[] - Filtered array of word objects
 */
export function parseTesseractWords(data: TesseractData, minConfidence: number = 60): Word[] {
  console.log('🔍 Parsing Tesseract JSON output...');
  
  if (!data.words || !Array.isArray(data.words)) {
    console.log('⚠️ No words array found in Tesseract output');
    return [];
  }
  
  const filteredWords: Word[] = [];
  
  for (const word of data.words) {
    if (word.confidence >= minConfidence) {
      filteredWords.push({
        text: word.text,
        confidence: word.confidence,
        bbox: {
          x0: word.bbox.x0,
          y0: word.bbox.y0,
          x1: word.bbox.x1,
          y1: word.bbox.y1
        }
      });
    } else {
      console.log(`⚠️ Filtered low-confidence word: "${word.text}" (${word.confidence}%)`);
    }
  }
  
  console.log(`✅ Parsed ${filteredWords.length} words (filtered from ${data.words.length})`);
  return filteredWords;
}

/**
 * Use Google Vision API as fallback for low-confidence Tesseract results
 * @param imageBuffer - Preprocessed image buffer
 * @returns Promise<ClusteredLine[]> - Array of text lines from Google Vision
 */
export async function analyzeWithGoogleVision(imageBuffer: Buffer): Promise<ClusteredLine[]> {
  console.log('🔍 Using Google Vision API fallback...');
  
  try {
    const { GOOGLE_APPLICATION_CREDENTIALS } = getEnv();
    
    if (!GOOGLE_APPLICATION_CREDENTIALS) {
      throw new Error('GOOGLE_APPLICATION_CREDENTIALS environment variable not set');
    }
    
    const client = new ImageAnnotatorClient({
      keyFilename: GOOGLE_APPLICATION_CREDENTIALS
    });
    
    const [result] = await client.textDetection(imageBuffer);
    const detections = result.textAnnotations;
    
    if (!detections || detections.length === 0) {
      console.log('⚠️ No text detected by Google Vision');
      return [];
    }
    
    // Skip the first annotation (it contains all text)
    const words = detections.slice(1).map(annotation => {
      const vertices = annotation.boundingPoly?.vertices || [];
      const x0 = Math.min(...vertices.map(v => v.x || 0));
      const y0 = Math.min(...vertices.map(v => v.y || 0));
      const x1 = Math.max(...vertices.map(v => v.x || 0));
      const y1 = Math.max(...vertices.map(v => v.y || 0));
      
      return {
        text: annotation.description || '',
        confidence: 90, // Google Vision doesn't provide confidence scores
        bbox: { x0, y0, x1, y1 }
      };
    });
    
    const clusters = clusterByY(words, 15); // Slightly higher threshold for Google Vision
    console.log(`✅ Google Vision extracted ${clusters.length} text lines`);
    
    return clusters;
  } catch (error) {
    console.error('❌ Google Vision API failed:', error);
    throw new Error(`Google Vision API failed: ${error}`);
  }
}

/**
 * Main OCR parsing function with preprocessing and fallback logic
 * @param imageBuffer - Raw image buffer
 * @returns Promise<OCRParserResult> - Structured OCR result with confidence metrics
 */
export async function parseImage(imageBuffer: Buffer): Promise<OCRParserResult> {
  console.log('🚀 Starting advanced OCR parsing...');
  
  try {
    // Step 1: Preprocess image
    const processedBuffer = await preprocess(imageBuffer);
    
    // Step 2: Analyze with Tesseract
    console.log('🔍 Running Tesseract analysis...');
    const tesseractResult = await Tesseract.recognize(processedBuffer, 'eng', {
      logger: m => {
        if (m.status === 'recognizing text') {
          console.log(`🔄 Tesseract progress: ${Math.round(m.progress * 100)}%`);
        }
      }
    });
    
    // Step 3: Parse Tesseract words and filter low confidence
    const words = parseTesseractWords(tesseractResult.data, 60);
    
    if (words.length === 0) {
      console.log('⚠️ No words found by Tesseract, using Google Vision fallback');
      const visionLines = await analyzeWithGoogleVision(processedBuffer);
      return {
        lines: visionLines,
        averageConfidence: 0,
        imageDimensions: { width: 0, height: 0 },
        usedFallback: true
      };
    }
    
    // Step 4: Cluster words into lines
    const clusters = clusterByY(words, 10);
    
    // Step 5: Calculate average confidence
    const totalConfidence = words.reduce((sum, w) => sum + w.confidence, 0);
    const averageConfidence = totalConfidence / words.length;
    
    console.log(`📊 Average confidence: ${averageConfidence.toFixed(1)}%`);
    
    // Step 6: Check if confidence is too low and use Google Vision fallback
    if (averageConfidence < 55) {
      console.log('⚠️ Low confidence detected, using Google Vision fallback');
      try {
        const visionLines = await analyzeWithGoogleVision(processedBuffer);
        return {
          lines: visionLines,
          averageConfidence,
          imageDimensions: { width: 0, height: 0 }, // Tesseract doesn't provide dimensions
          usedFallback: true
        };
      } catch (visionError) {
        console.log('⚠️ Google Vision fallback failed, using Tesseract results');
      }
    }
    
    // Step 7: Log low-confidence clusters for debugging
    const lowConfidenceClusters = clusters.filter(c => c.confidence < 50);
    if (lowConfidenceClusters.length > 0) {
      console.log('⚠️ Low-confidence clusters detected:');
      lowConfidenceClusters.forEach((cluster, index) => {
        console.log(`  ${index + 1}. "${cluster.text}" (${cluster.confidence.toFixed(1)}%)`);
      });
    }
    
    return {
      lines: clusters,
      averageConfidence,
      imageDimensions: { width: 0, height: 0 }, // Tesseract doesn't provide dimensions
      usedFallback: false
    };
    
  } catch (error) {
    console.error('❌ OCR parsing failed:', error);
    throw new Error(`OCR parsing failed: ${error}`);
  }
} 