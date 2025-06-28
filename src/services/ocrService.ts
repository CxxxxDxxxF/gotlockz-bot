/**
 * OCR Service - Image analysis for betting slips
 */
import axios from 'axios';
import Tesseract from 'tesseract.js';
import { getEnv } from '../utils/env';

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
 * Analyze an image to extract text using OCR
 * @param image - Buffer containing the image data
 * @returns Promise<string[]> - Array of text lines extracted from the image
 */
export async function analyzeImage(image: Buffer): Promise<string[]> {
  console.log('🔍 Starting OCR analysis...');
  console.log('📏 Image buffer size:', image.length, 'bytes');
  
  try {
    // Try OCR.space API first if API key is available
    const { OCR_SPACE_API_KEY } = getEnv();
    if (OCR_SPACE_API_KEY) {
      console.log('🔑 Using OCR.space API...');
      try {
        const result = await analyzeWithOCRSpace(image, OCR_SPACE_API_KEY);
        console.log('✅ OCR.space API successful, extracted lines:', result.length);
        return result;
      } catch (error) {
        console.log('❌ OCR.space API failed:', error);
      }
    } else {
      console.log('⚠️ No OCR_SPACE_API_KEY found, using Tesseract.js fallback');
    }
  } catch (error) {
    console.log('❌ Error checking OCR.space API:', error);
  }

  // Fallback to Tesseract.js
  console.log('🔄 Falling back to Tesseract.js...');
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
 * Use OCR.space API for higher accuracy
 */
async function analyzeWithOCRSpace(image: Buffer, apiKey: string): Promise<string[]> {
  const base64Image = image.toString('base64');
  
  const formData = new FormData();
  formData.append('apikey', apiKey);
  formData.append('base64Image', `data:image/png;base64,${base64Image}`);
  formData.append('language', 'eng');
  formData.append('isOverlayRequired', 'false');
  formData.append('filetype', 'png');

  const response = await axios.post('https://api.ocr.space/parse/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  if (response.data.ParsedResults && response.data.ParsedResults.length > 0) {
    const parsedText = response.data.ParsedResults[0].ParsedText;
    const lines = parsedText.split('\r\n').filter((line: string) => line.trim().length > 0);
    console.log('📄 OCR.space extracted text:', parsedText.substring(0, 200) + '...');
    return lines;
  }

  throw new Error('OCR.space API returned no results');
}

/**
 * Use Tesseract.js as fallback
 */
async function analyzeWithTesseract(image: Buffer): Promise<string[]> {
  console.log('🔄 Starting Tesseract.js processing...');
  
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