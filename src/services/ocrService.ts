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
  try {
    // Try OCR.space API first if API key is available
    const { OCR_SPACE_API_KEY } = getEnv();
    if (OCR_SPACE_API_KEY) {
      return await analyzeWithOCRSpace(image, OCR_SPACE_API_KEY);
    }
  } catch (error) {
    console.log('OCR.space API not available, falling back to Tesseract.js');
  }

  // Fallback to Tesseract.js
  return await analyzeWithTesseract(image);
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
    return parsedText.split('\r\n').filter((line: string) => line.trim().length > 0);
  }

  throw new Error('OCR.space API returned no results');
}

/**
 * Use Tesseract.js as fallback
 */
async function analyzeWithTesseract(image: Buffer): Promise<string[]> {
  const result = await Tesseract.recognize(image, 'eng', {
    logger: m => console.log(m)
  });

  return result.data.text.split('\n').filter((line: string) => line.trim().length > 0);
} 