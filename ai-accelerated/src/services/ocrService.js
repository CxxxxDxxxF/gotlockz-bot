import Tesseract from 'tesseract.js';
import sharp from 'sharp';
import axios from 'axios';
import { logger } from '../utils/logger.js';

class OCRService {
  constructor () {
    this.engines = ['tesseract', 'easyocr', 'paddleocr'];
    this.currentEngine = 0;
  }

  async analyzeImage (imageUrl, debug = false) {
    const startTime = Date.now();

    try {
      logger.info('Starting OCR analysis', { imageUrl, debug });

      // Download and preprocess image
      const imageBuffer = await this.downloadImage(imageUrl);
      const processedBuffer = await this.preprocessImage(imageBuffer, debug);

      // Try multiple OCR engines
      let ocrResult = null;
      let engineUsed = '';

      for (let i = 0; i < this.engines.length; i++) {
        const engine = this.engines[(this.currentEngine + i) % this.engines.length];

        try {
          logger.info(`Trying OCR engine: ${engine}`);
          ocrResult = await this.runOCR(engine, processedBuffer, debug);

          if (ocrResult && ocrResult.confidence > 0.7) {
            engineUsed = engine;
            break;
          }
        } catch (error) {
          logger.warn(`OCR engine ${engine} failed:`, error.message);
        }
      }

      if (!ocrResult) {
        throw new Error('All OCR engines failed');
      }

      // Parse bet slip data
      const betSlip = this.parseBetSlip(ocrResult.text);

      const time = Date.now() - startTime;

      logger.info('OCR analysis completed', {
        engine: engineUsed,
        confidence: ocrResult.confidence,
        time: `${time}ms`,
        textLength: ocrResult.text.length
      });

      return {
        success: true,
        data: betSlip,
        engine: engineUsed,
        confidence: ocrResult.confidence,
        time: time,
        rawText: ocrResult.text
      };

    } catch (error) {
      logger.error('OCR analysis failed:', error);
      return {
        success: false,
        error: error.message,
        time: Date.now() - startTime
      };
    }
  }

  async downloadImage (imageUrl) {
    const response = await axios.get(imageUrl, {
      responseType: 'arraybuffer',
      timeout: 10000
    });
    return Buffer.from(response.data);
  }

  async preprocessImage (imageBuffer, debug = false) {
    try {
      // Use Sharp for image preprocessing
      const processed = await sharp(imageBuffer)
        .resize(1200, null, { withoutEnlargement: true }) // Resize for better OCR
        .grayscale() // Convert to grayscale
        .normalize() // Normalize contrast
        .sharpen() // Sharpen edges
        .png() // Convert to PNG
        .toBuffer();

      if (debug) {
        try {
          // Create debug directory if it doesn't exist
          const fs = await import('fs');
          const path = await import('path');
          const debugDir = 'debug';
          if (!fs.existsSync(debugDir)) {
            fs.mkdirSync(debugDir, { recursive: true });
          }
          await sharp(processed).toFile(path.join(debugDir, 'preprocessed.png'));
        } catch (error) {
          logger.warn('Could not save debug image:', error.message);
        }
      }

      return processed;
    } catch (error) {
      logger.warn('Image preprocessing failed, using original:', error.message);
      return imageBuffer;
    }
  }

  async runOCR (engine, imageBuffer, debug = false) {
    switch (engine) {
    case 'tesseract':
      return await this.runTesseract(imageBuffer, debug);
    case 'easyocr':
      return await this.runEasyOCR(imageBuffer, debug);
    case 'paddleocr':
      return await this.runPaddleOCR(imageBuffer, debug);
    default:
      throw new Error(`Unknown OCR engine: ${engine}`);
    }
  }

  async runTesseract (imageBuffer, debug = false) {
    const worker = await Tesseract.createWorker();
    await worker.loadLanguage('eng');
    await worker.initialize('eng');

    // Configure for better text recognition
    await worker.setParameters({
      tessedit_char_whitelist: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-/.()$%',
      preserve_interword_spaces: '1'
    });

    const result = await worker.recognize(imageBuffer);
    await worker.terminate();

    if (debug) {
      logger.info('Tesseract result:', {
        text: result.data.text,
        confidence: result.data.confidence,
        words: result.data.words.length
      });
    }

    return {
      text: result.data.text,
      confidence: result.data.confidence / 100
    };
  }

  async runEasyOCR (imageBuffer, _debug = false) {
    // Placeholder for EasyOCR integration
    // In production, you would use a Python subprocess or API
    throw new Error('EasyOCR not implemented yet');
  }

  async runPaddleOCR (imageBuffer, _debug = false) {
    // Placeholder for PaddleOCR integration
    // In production, you would use a Python subprocess or API
    throw new Error('PaddleOCR not implemented yet');
  }

  parseBetSlip (text) {
    // Simple bet slip parser - can be enhanced with AI
    const lines = text.split('\n').filter(line => line.trim());

    // Extract basic information
    const betSlip = {
      legs: [],
      totalOdds: null,
      stake: null,
      potentialWin: null
    };

    // Look for common patterns
    for (const line of lines) {
      // Look for team names and odds
      const teamMatch = line.match(/([A-Za-z\s]+)\s+vs\s+([A-Za-z\s]+)/i);
      if (teamMatch) {
        betSlip.legs.push({
          teamA: teamMatch[1].trim(),
          teamB: teamMatch[2].trim(),
          odds: null
        });
      }

      // Look for odds
      const oddsMatch = line.match(/(\+|-)?\d+(\.\d+)?/);
      if (oddsMatch && betSlip.legs.length > 0) {
        betSlip.legs[betSlip.legs.length - 1].odds = parseFloat(oddsMatch[0]);
      }

      // Look for stake
      const stakeMatch = line.match(/\$(\d+(\.\d+)?)/);
      if (stakeMatch) {
        betSlip.stake = parseFloat(stakeMatch[1]);
      }
    }

    // If no legs were found, create a default one
    if (betSlip.legs.length === 0) {
      betSlip.legs.push({
        teamA: 'Team A',
        teamB: 'Team B',
        odds: null
      });
    }

    return betSlip;
  }
}

const ocrService = new OCRService();
export const { analyzeImage } = ocrService;
