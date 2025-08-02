import Tesseract from 'tesseract.js';
import sharp from 'sharp';

/**
 * Extracts text from a bet slip image buffer using OCR.
 * @param {Buffer} imageBuffer - The image buffer to process
 * @returns {Promise<string>} OCR text
 */
export async function extractTextFromImage(imageBuffer) {
  // Preprocess image (resize, grayscale, etc.)
  const processed = await sharp(imageBuffer)
    .grayscale()
    .toBuffer();

  const { data: { text } } = await Tesseract.recognize(processed, 'eng');
  return text;
} 