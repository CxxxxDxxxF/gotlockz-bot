/**
 * Advanced OCR Parser Service
 * Handles image preprocessing, Tesseract JSON parsing, word clustering, and Google Vision fallback
 */
import { createWorker, PSM } from 'tesseract.js';
import { ImageAnnotatorClient } from '@google-cloud/vision';
import { getEnv } from '../utils/env';
import { TesseractData, TesseractWord } from '../types';
import { writeFileSync, mkdirSync } from 'fs';
import path from 'path';

export type Word = TesseractWord;
export { TesseractData };

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
  rawText: string;
  debug?: {
    rawImagePath?: string;
    preprocessedImagePath?: string;
    tesseractOutputPath?: string;
    cropRegion?: { x: number; y: number; w: number; h: number };
  };
}

/**
 * Preprocess image for better OCR accuracy
 * @param buffer - Raw image buffer
 * @param debugMode - Whether to save debug images and data
 * @returns Promise<{ buffer: Buffer; cropRegion?: { x: number; y: number; w: number; h: number } }> - Preprocessed image buffer and crop region
 */
export async function preprocess(buffer: Buffer, debugMode = false): Promise<{ buffer: Buffer; cropRegion?: { x: number; y: number; w: number; h: number } }> {
  console.log('🔄 Starting image preprocessing...');
  
  try {
    const Jimp = (await import('jimp')).default;
    let image = await (Jimp as any).read(buffer);
    const originalWidth = image.bitmap.width;
    const originalHeight = image.bitmap.height;
    
    console.log(`📏 Original dimensions: ${originalWidth}x${originalHeight}`);
    
    // Create debug directory if needed
    if (debugMode) {
      try {
        mkdirSync(path.resolve(__dirname, '../../debug'), { recursive: true });
      } catch (err) {
        // Directory might already exist
      }
    }

    // 1. Save the raw upload
    if (debugMode) {
      writeFileSync(path.resolve(__dirname, '../../debug/raw.png'), buffer);
      console.log('📸 Saved raw image to debug/raw.png');
    }

    // 2. Try to crop to the bet area (common bet slip layout)
    let cropRegion: { x: number; y: number; w: number; h: number } | undefined = { 
      x: 50, 
      y: 200, 
      w: originalWidth - 100, 
      h: originalHeight - 400 
    };
    
    // Ensure crop region is valid
    cropRegion.x = Math.max(0, cropRegion.x);
    cropRegion.y = Math.max(0, cropRegion.y);
    cropRegion.w = Math.min(originalWidth - cropRegion.x, cropRegion.w);
    cropRegion.h = Math.min(originalHeight - cropRegion.y, cropRegion.h);
    
    // Apply crop if region is reasonable
    if (cropRegion.w > 100 && cropRegion.h > 100) {
      image = image.crop(cropRegion.x, cropRegion.y, cropRegion.w, cropRegion.h);
      console.log(`✂️ Cropped image to region: ${cropRegion.x},${cropRegion.y} ${cropRegion.w}x${cropRegion.h}`);
    } else {
      cropRegion = undefined;
      console.log('⚠️ Skipping crop - region too small');
    }

    // 3. Apply preprocessing pipeline
    image = image
      .greyscale()
      .contrast(0.7)
      .normalize()
      .scaleToFit(1000, 1000);

    // Apply conditional gaussian blur
    if (image.bitmap.width > 1 && image.bitmap.height > 1) {
      image = image.gaussian(1);
    }

    // Apply threshold
    image = image.threshold({ max: 200 });

    // 4. Apply noise filtering (remove small isolated blobs)
    image = removeNoise(image);

    // 5. Save after preprocessing
    const processedBuffer: Buffer = await new Promise((resolve, reject) => {
      image.getBuffer('image/png', (err: any, buf: Buffer) => {
        if (err) reject(err); else resolve(buf);
      });
    });
    if (debugMode) {
      writeFileSync(path.resolve(__dirname, '../../debug/preprocessed.png'), processedBuffer);
      console.log('📸 Saved preprocessed image to debug/preprocessed.png');
    }

    if (cropRegion) {
      return { buffer: processedBuffer, cropRegion };
    } else {
      return { buffer: processedBuffer };
    }
  } catch (error) {
    console.error('❌ Image preprocessing failed:', error);
    throw new Error(`Image preprocessing failed: ${error}`);
  }
}

/**
 * Remove noise (small isolated blobs) from the image
 */
function removeNoise(img: any): any {
  const width = img.bitmap.width;
  const height = img.bitmap.height;
  
  // Create a copy for processing
  const processed = img.clone();
  
  // Simple noise removal: if a pixel is isolated (surrounded by white), make it white
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      const idx = (y * width + x) * 4;
      const current = processed.bitmap.data[idx];
      
      if (current === 0) { // Black pixel
        // Check surrounding pixels
        const neighbors = [
          processed.bitmap.data[((y-1) * width + x) * 4],     // top
          processed.bitmap.data[((y+1) * width + x) * 4],     // bottom
          processed.bitmap.data[(y * width + (x-1)) * 4],     // left
          processed.bitmap.data[(y * width + (x+1)) * 4],     // right
        ];
        
        // If all neighbors are white, this is likely noise
        if (neighbors.every(n => n === 255)) {
          processed.bitmap.data[idx] = 255;
          processed.bitmap.data[idx + 1] = 255;
          processed.bitmap.data[idx + 2] = 255;
        }
      }
    }
  }
  
  return processed;
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
 * @param debugMode - Whether to save debug images and data
 * @returns Promise<OCRParserResult> - Structured OCR result with confidence metrics
 */
export async function parseImage(imageBuffer: Buffer, debugMode = false): Promise<OCRParserResult> {
  console.log('🚀 Starting advanced OCR parsing...');
  
  try {
    // Step 1: Preprocess image
    const { buffer: processedBuffer, cropRegion } = await preprocess(imageBuffer, debugMode);
    
    // Step 2: Analyze with Tesseract
    console.log('🔍 Running Tesseract analysis...');
    const worker = await createWorker();
    await worker.reinitialize('eng');
    
    // Set parameters for better text recognition
    await worker.setParameters({
      tessedit_pageseg_mode: PSM.SINGLE_BLOCK,
      tessedit_char_whitelist: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-/.()$%',
      preserve_interword_spaces: '1'
    });
    
    const tesseractResult = await worker.recognize(processedBuffer);
    await worker.terminate();
    
    // Step 3: Save full Tesseract output for debugging
    if (debugMode) {
      const debugData = {
        words: tesseractResult.data.words,
        text: tesseractResult.data.text,
        confidence: tesseractResult.data.confidence,
        timestamp: new Date().toISOString()
      };
      writeFileSync(
        path.resolve(__dirname, '../../debug/tesseract.json'),
        JSON.stringify(debugData, null, 2)
      );
      console.log('📄 Saved Tesseract output to debug/tesseract.json');
    }
    
    // Step 4: Parse Tesseract words and filter low confidence
    const words = parseTesseractWords(tesseractResult.data, 60);
    
    // Create debug object with proper typing
    const debugInfo = debugMode ? {
      rawImagePath: 'debug/raw.png',
      preprocessedImagePath: 'debug/preprocessed.png',
      tesseractOutputPath: 'debug/tesseract.json',
      ...(cropRegion ? { cropRegion } : {})
    } : undefined;
    
    if (words.length === 0) {
      console.log('⚠️ No words found by Tesseract, using Google Vision fallback');
      const visionLines = await analyzeWithGoogleVision(processedBuffer);
      const result: OCRParserResult = {
        lines: visionLines,
        averageConfidence: 0,
        imageDimensions: { width: 0, height: 0 },
        usedFallback: true,
        rawText: tesseractResult.data.text
      };
      if (debugInfo) {
        result.debug = debugInfo;
      }
      return result;
    }
    
    // Step 5: Cluster words into lines
    const clusters = clusterByY(words, 10);
    
    // Step 6: Calculate average confidence
    const totalConfidence = words.reduce((sum, w) => sum + w.confidence, 0);
    const averageConfidence = totalConfidence / words.length;
    
    console.log(`📊 Average confidence: ${averageConfidence.toFixed(1)}%`);
    
    // Step 7: Check if confidence is too low and use Google Vision fallback
    if (averageConfidence < 55) {
      console.log('⚠️ Low confidence detected, using Google Vision fallback');
      try {
        const visionLines = await analyzeWithGoogleVision(processedBuffer);
        const result: OCRParserResult = {
          lines: visionLines,
          averageConfidence,
          imageDimensions: { width: 0, height: 0 }, // Tesseract doesn't provide dimensions
          usedFallback: true,
          rawText: tesseractResult.data.text
        };
        if (debugInfo) {
          result.debug = debugInfo;
        }
        return result;
      } catch (visionError) {
        console.log('⚠️ Google Vision fallback failed, using Tesseract results');
      }
    }
    
    // Step 8: Log low-confidence clusters for debugging
    const lowConfidenceClusters = clusters.filter(c => c.confidence < 50);
    if (lowConfidenceClusters.length > 0) {
      console.log('⚠️ Low-confidence clusters detected:');
      lowConfidenceClusters.forEach((cluster, index) => {
        console.log(`  ${index + 1}. "${cluster.text}" (${cluster.confidence.toFixed(1)}%)`);
      });
    }
    
    const result: OCRParserResult = {
      lines: clusters,
      averageConfidence,
      imageDimensions: { width: 0, height: 0 }, // Tesseract doesn't provide dimensions
      usedFallback: false,
      rawText: tesseractResult.data.text
    };
    if (debugInfo) {
      result.debug = debugInfo;
    }
    return result;
    
  } catch (error) {
    console.error('❌ OCR parsing failed:', error);
    throw new Error(`OCR parsing failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
} 