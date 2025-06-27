/**
 * OCR Service - Image analysis for betting slips
 */

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
 * @returns Promise<OCRResult> - Extracted text and confidence scores
 */
export async function analyzeImage(image: Buffer): Promise<OCRResult> {
  throw new Error("Not implemented");
} 