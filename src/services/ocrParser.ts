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
// clusterByY function will be defined in this file

// Constants for ROI detection
const MIN_CROP_HEIGHT = 30;
const TEXT_DENSITY_THRESHOLD = 0.1; // 10% of row width

// Tunable constants
const HEADER_REGEX = /Fanatics/i;
const DISCLAIMER_REGEX = /MUST BE\s+\d+\+/i;
const Y_MARGIN = 5;
const CONFIDENCE_THRESHOLD = 60;

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
    const JimpModule = await import('jimp');
    const Jimp = (JimpModule.default ?? JimpModule) as any;
    let image = await Jimp.read(buffer);
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

    // 2. Smart ROI Detection using horizontal projection analysis
    const smartCropRegion = await detectTextRegion(image);
    let cropRegion: { x: number; y: number; w: number; h: number } | undefined;
    
    if (smartCropRegion && smartCropRegion.h > 100) {
      // Apply smart crop
      image = image.crop(smartCropRegion.x, smartCropRegion.y, smartCropRegion.w, smartCropRegion.h);
      cropRegion = smartCropRegion;
      console.log(`🎯 Smart crop applied: ${cropRegion.x},${cropRegion.y} ${cropRegion.w}x${cropRegion.h}`);
      
      // Save debug visualization
      if (debugMode) {
        await saveCropDebugVisualization(buffer, cropRegion);
        
        // Save the cropped region itself
        const croppedBuffer = await image.getBufferAsync('image/png');
        writeFileSync(path.resolve(__dirname, '../../debug/crop.png'), croppedBuffer);
        console.log('📸 Saved cropped region to debug/crop.png');
      }
    } else {
      // Fallback to basic crop if smart detection fails
      let basicCropRegion: { x: number; y: number; w: number; h: number } | undefined = { 
        x: 50, 
        y: 200, 
        w: originalWidth - 100, 
        h: originalHeight - 400 
      };
      
      // Ensure crop region is valid
      basicCropRegion.x = Math.max(0, basicCropRegion.x);
      basicCropRegion.y = Math.max(0, basicCropRegion.y);
      basicCropRegion.w = Math.min(originalWidth - basicCropRegion.x, basicCropRegion.w);
      basicCropRegion.h = Math.min(originalHeight - basicCropRegion.y, basicCropRegion.h);
      
      // Apply basic crop if region is reasonable
      if (basicCropRegion.w > 100 && basicCropRegion.h > 100) {
        image = image.crop(basicCropRegion.x, basicCropRegion.y, basicCropRegion.w, basicCropRegion.h);
        cropRegion = basicCropRegion;
        console.log(`✂️ Basic crop applied: ${cropRegion.x},${cropRegion.y} ${cropRegion.w}x${cropRegion.h}`);
      } else {
        cropRegion = undefined;
        console.log('⚠️ Skipping crop - region too small');
      }
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
 * Detect text region using horizontal projection analysis
 * @param image - Jimp image object
 * @returns Promise<{ x: number; y: number; w: number; h: number } | null> - Detected text region or null
 */
async function detectTextRegion(image: any): Promise<{ x: number; y: number; w: number; h: number } | null> {
  try {
    // Create a binary version for analysis
    const bin = image.clone().greyscale().threshold({ max: 200 });
    const rows = bin.bitmap.height;
    const width = bin.bitmap.width;
    
    // Compute horizontal projection (sum of black pixels per row)
    const rowSums = new Array(rows).fill(0);
    
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < width; x++) {
        const idx = (y * width + x) * 4;
        if (bin.bitmap.data[idx] === 0) { // Black pixel
          rowSums[y]++;
        }
      }
    }
    
    // Find text density threshold (10% of row width)
    const threshold = width * TEXT_DENSITY_THRESHOLD;
    
    // Find first row with significant text density
    let top = -1;
    for (let y = 0; y < rows; y++) {
      if (rowSums[y] > threshold) {
        top = y;
        break;
      }
    }
    
    // Find last row with significant text density
    let bottom = -1;
    for (let y = rows - 1; y >= 0; y--) {
      if (rowSums[y] > threshold) {
        bottom = y;
        break;
      }
    }
    
    // Validate detected region
    if (top === -1 || bottom === -1 || top >= bottom) {
      console.log('⚠️ Could not detect valid text region');
      return null;
    }
    
    const regionHeight = bottom - top + 1;
    
    if (regionHeight < MIN_CROP_HEIGHT) {
      console.log(`⚠️ Skipping crop: detected region too small (${regionHeight}px < ${MIN_CROP_HEIGHT}px)`);
      return null;
    }
    
    // Crop bounds: [0, top - 5] to [width, bottom - top + 10]
    const x = 0;
    const y = Math.max(0, top - 5);
    const w = width;
    const h = Math.min(rows - y, bottom - top + 10);
    
    console.log(`🔍 Text region detected: ${x},${y} ${w}x${h} (density: ${(rowSums[top] / width * 100).toFixed(1)}% - ${(rowSums[bottom] / width * 100).toFixed(1)}%)`);
    
    return { x, y, w, h };
    
  } catch (error) {
    console.error('❌ Text region detection failed:', error);
    return null;
  }
}

/**
 * Save debug visualization of crop region
 * @param originalBuffer - Original image buffer
 * @param cropRegion - Detected crop region
 */
async function saveCropDebugVisualization(originalBuffer: Buffer, cropRegion: { x: number; y: number; w: number; h: number }): Promise<void> {
  try {
    const JimpModule = await import('jimp');
    const Jimp = (JimpModule.default ?? JimpModule) as any;
    const raw = await Jimp.read(originalBuffer);
    
    // Draw red rectangle around crop region
    const red = Jimp.rgbaToInt(255, 0, 0, 255);
    
    // Draw top and bottom borders
    for (let x = cropRegion.x; x < cropRegion.x + cropRegion.w; x++) {
      raw.setPixelColor(red, x, cropRegion.y);
      raw.setPixelColor(red, x, cropRegion.y + cropRegion.h - 1);
    }
    
    // Draw left and right borders
    for (let y = cropRegion.y; y < cropRegion.y + cropRegion.h; y++) {
      raw.setPixelColor(red, cropRegion.x, y);
      raw.setPixelColor(red, cropRegion.x + cropRegion.w - 1, y);
    }
    
    // Save debug visualization
    writeFileSync(
      path.resolve(__dirname, '../../debug/crop-overlay.png'),
      await raw.getBufferAsync('image/png')
    );
    console.log('📸 Saved crop overlay to debug/crop-overlay.png');
    
  } catch (error) {
    console.error('❌ Failed to save crop debug visualization:', error);
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
export async function parseImage(buffer: Buffer, debugMode = false): Promise<OCRParserResult> {
  console.log('🚀 Starting advanced OCR parsing...');
  
  try {
    // Step 1: Preprocess image
    const { buffer: processedBuffer, cropRegion } = await preprocess(buffer, debugMode);
    
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
    const lowConfidenceClusters = clusters.filter((c: ClusteredLine) => c.confidence < 50);
    if (lowConfidenceClusters.length > 0) {
      console.log('⚠️ Low-confidence clusters detected:');
      lowConfidenceClusters.forEach((cluster: ClusteredLine, index: number) => {
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

export async function parseImageLegacy(buffer: Buffer): Promise<string[]> {
  // 1) Preprocess as before (dynamic Jimp import inside to keep tests happy)
  const { preprocessedBuffer } = await (async () => {
    const JimpModule = await import('jimp');
    const Jimp = (JimpModule.default ?? JimpModule) as any;
    let image = await Jimp.read(buffer);
    image = image
      .greyscale()
      .contrast(0.7)
      .normalize()
      .scaleToFit(1000, 1000)
      .gaussian(image.bitmap.width > 1 && image.bitmap.height > 1 ? 1 : 0)
      .threshold({ max: 200 });
    const buf = await image.getBufferAsync('image/png');
    writeFileSync(path.resolve(__dirname, '../../debug/preprocessed.png'), buf);
    return { preprocessedBuffer: buf };
  })();

  // 2) OCR with Tesseract
  const worker = await createWorker();
  await worker.reinitialize('eng');
  await worker.setParameters({
    tessedit_char_whitelist: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-/',
    tessedit_pageseg_mode: PSM.SINGLE_BLOCK,
    tessedit_ocr_engine_mode: '3'
  });

  const {
    data: { words }
  } = await worker.recognize(preprocessedBuffer);
  await worker.terminate();

  // 3) Determine header + disclaimer Y-bounds
  const headerMaxY =
    words
      .filter((w: any) => HEADER_REGEX.test(w.text))
      .map((w: any) => w.bbox.y1)
      .reduce((max: number, y: number) => Math.max(max, y), -Infinity) || -Infinity;

  const disclaimerMinY =
    words
      .filter((w: any) => DISCLAIMER_REGEX.test(w.text))
      .map((w: any) => w.bbox.y0)
      .reduce((min: number, y: number) => Math.min(min, y), Infinity) || Infinity;

  // 4) Filter to bet-details region + confidence
  const betWords = words.filter(
    (w: any) =>
      w.bbox.y0 > headerMaxY + Y_MARGIN &&
      w.bbox.y1 < disclaimerMinY - Y_MARGIN &&
      w.confidence > CONFIDENCE_THRESHOLD
  );

  // 5) Debug dump of filtered words
  writeFileSync(
    path.resolve(__dirname, '../../debug/filtered-words.json'),
    JSON.stringify(
      betWords.map((w: any) => ({
        text: w.text,
        bbox: w.bbox,
        confidence: w.confidence
      })),
      null,
      2
    )
  );

  // 6) Cluster by Y and rebuild lines
  const clusters = clusterByY(betWords, 10);
  const filteredLines = clusters.map((cluster: ClusteredLine) =>
    cluster.words.map((w: Word) => w.text).join(' ')
  );

  writeFileSync(
    path.resolve(__dirname, '../../debug/filtered-lines.json'),
    JSON.stringify(filteredLines, null, 2)
  );

  // 7) Return lines for downstream parsing (or call your parser here)
  return filteredLines;
}

/**
 * Cluster words by Y-coordinate to group them into lines
 * @param words - Array of word objects with bounding boxes
 * @param thresholdPx - Y-coordinate threshold for clustering (default: 10)
 * @returns ClusteredLine[] - Array of clustered text lines
 */
export function clusterByY(words: Word[], thresholdPx: number = 10): ClusteredLine[] {
  if (words.length === 0) {
    return [];
  }

  // Sort words by Y-coordinate
  const sortedWords = [...words].sort((a, b) => a.bbox.y0 - b.bbox.y0);
  if (!sortedWords[0]) return [];

  const clusters: Word[][] = [];
  let currentCluster: Word[] = [sortedWords[0]];
  
  for (let i = 1; i < sortedWords.length; i++) {
    const word = sortedWords[i];
    if (!word) continue;
    
    const lastWord = currentCluster[currentCluster.length - 1];
    if (!lastWord) continue;
    
    // Check if this word is close enough to the last word in the cluster
    const yDistance = Math.abs(word.bbox.y0 - lastWord.bbox.y0);
    
    if (yDistance <= thresholdPx) {
      // Add to current cluster
      currentCluster.push(word);
    } else {
      // Start a new cluster
      clusters.push(currentCluster);
      currentCluster = [word];
    }
  }
  
  // Add the last cluster
  clusters.push(currentCluster);
  
  // Convert clusters to ClusteredLine objects
  return clusters.map(cluster => {
    // Sort words within cluster by X-coordinate
    const sortedCluster = cluster.sort((a, b) => a.bbox.x0 - b.bbox.x0);
    
    // Calculate average confidence
    const totalConfidence = cluster.reduce((sum, w) => sum + w.confidence, 0);
    const averageConfidence = totalConfidence / cluster.length;
    
    // Join words to form text
    const text = sortedCluster.map(w => w.text).join(' ');
    
    return {
      text,
      confidence: averageConfidence,
      words: sortedCluster
    };
  });
} 