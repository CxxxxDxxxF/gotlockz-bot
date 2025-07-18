/**
 * OCR Service - Image analysis for betting slips
 */
import axios from 'axios';
import Tesseract from 'tesseract.js';
import { getEnv } from '../utils/env';
import { parseImage, OCRParserResult } from './ocrParser';

export interface OCRResult {
  text: string;
  confidence: number;
  lines: Array<{
    text: string;
    confidence: number;
    bbox: { x0: number; y0: number; x1: number; y1: number };
  }>;
}

/**
 * Analyze an image to extract text using advanced OCR with preprocessing and fallback
 * @param image - Buffer containing the image data
 * @param debug - Whether to enable debug mode (saves debug images and data)
 * @returns Promise<string[]> - Array of text lines extracted from the image
 */
export async function analyzeImage(image: Buffer, debug = false): Promise<string[]> {
  console.log('🔍 Starting advanced OCR analysis...');
  console.log('📏 Image buffer size:', image.length, 'bytes');
  if (debug) {
    console.log('🐛 Debug mode enabled - will save debug images and data');
  }
  
  try {
    // Use the new advanced OCR parser
    const result: OCRParserResult = await parseImage(image, debug);
    
    console.log(`📊 OCR Analysis Results:`);
    console.log(`  - Lines extracted: ${result.lines.length}`);
    console.log(`  - Average confidence: ${result.averageConfidence.toFixed(1)}%`);
    console.log(`  - Image dimensions: ${result.imageDimensions.width}x${result.imageDimensions.height}`);
    console.log(`  - Used fallback: ${result.usedFallback ? 'Yes (Google Vision)' : 'No (Tesseract)'}`);
    
    if (debug && result.debug) {
      console.log('🐛 Debug info:');
      console.log(`  - Raw image: ${result.debug.rawImagePath}`);
      console.log(`  - Preprocessed: ${result.debug.preprocessedImagePath}`);
      console.log(`  - Tesseract output: ${result.debug.tesseractOutputPath}`);
    }
    
    // Extract text lines from clustered results
    const textLines = result.lines.map(line => line.text).filter(text => text.trim().length > 0);
    
    console.log('✅ Advanced OCR successful, extracted lines:', textLines.length);
    return textLines;
    
  } catch (error) {
    console.error('❌ Advanced OCR failed:', error);
    
    // Fallback to legacy OCR methods
    console.log('🔄 Falling back to legacy OCR methods...');
    return await fallbackToLegacyOCR(image);
  }
}

/**
 * Legacy OCR fallback methods
 */
async function fallbackToLegacyOCR(image: Buffer): Promise<string[]> {
  try {
    // Try OCR.space API first if API key is available (no retries)
    const { OCR_SPACE_API_KEY } = getEnv();
    if (OCR_SPACE_API_KEY) {
      console.log('🔑 Using OCR.space API fallback...');
      try {
        const result = await analyzeWithOCRSpace(image, OCR_SPACE_API_KEY);
        console.log('✅ OCR.space API successful, extracted lines:', result.length);
        return result;
      } catch (error) {
        console.log('❌ OCR.space API failed, skipping retry:', error instanceof Error ? error.message : 'Unknown error');
        // Continue to Tesseract.js fallback - no retry
      }
    } else {
      console.log('⚠️ No OCR_SPACE_API_KEY found, using Tesseract.js fallback');
    }
  } catch (error) {
    console.log('❌ Error checking OCR.space API:', error);
  }

  // Fallback to basic Tesseract.js
  console.log('🔄 Falling back to basic Tesseract.js...');
  try {
    const result = await analyzeWithTesseract(image);
    console.log('✅ Tesseract.js successful, extracted lines:', result.length);
    return result;
  } catch (error) {
    console.error('❌ Tesseract.js failed:', error);
    console.log('📝 Returning empty array due to OCR failure');
    return [];
  }
}

/**
 * Use OCR.space API for higher accuracy with configurable timeout
 */
async function analyzeWithOCRSpace(image: Buffer, apiKey: string): Promise<string[]> {
  const base64Image = image.toString('base64');
  
  const formData = new FormData();
  formData.append('apikey', apiKey);
  formData.append('base64Image', `data:image/png;base64,${base64Image}`);
  formData.append('language', 'eng');
  formData.append('isOverlayRequired', 'false');
  formData.append('filetype', 'png');

  try {
    const response = await axios.post('https://api.ocr.space/parse/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 10000, // 10 second timeout
    });

    if (response.data.ParsedResults && response.data.ParsedResults.length > 0) {
      const parsedText = response.data.ParsedResults[0].ParsedText;
      const lines = parsedText.split('\r\n').filter((line: string) => line.trim().length > 0);
      console.log('📄 OCR.space extracted text:', parsedText.substring(0, 200) + '...');
      return lines;
    }

    throw new Error('OCR.space API returned no results');
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        console.log('⏰ OCR.space API timeout - falling back to Tesseract.js');
        throw new Error('OCR.space API timeout');
      }
      if (error.code === 'ETIMEDOUT' || error.code === 'ECONNREFUSED') {
        console.log('🌐 OCR.space API connection error - falling back to Tesseract.js');
        throw new Error('OCR.space API connection error');
      }
    }
    console.log('❌ OCR.space API error - falling back to Tesseract.js:', error instanceof Error ? error.message : 'Unknown error');
    throw error;
  }
}

/**
 * Use Tesseract.js as fallback
 */
async function analyzeWithTesseract(image: Buffer): Promise<string[]> {
  console.log('🔄 Starting basic Tesseract.js processing...');
  
  const result = await Tesseract.recognize(image, 'eng', {
    logger: m => {
      if (m.status === 'recognizing text') {
        console.log(`🔄 Tesseract progress: ${Math.round(m.progress * 100)}%`);
      } else {
        console.log(`🔄 Tesseract: ${m.status}`);
      }
    }
  });

  const lines = result.data.text.split('\n').filter((line: string) => line.trim().length > 0);
  console.log('📄 Tesseract extracted text:', result.data.text.substring(0, 200) + '...');
  console.log('📊 Tesseract confidence:', result.data.confidence);
  
  return lines;
} 