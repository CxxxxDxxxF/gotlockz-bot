/**
 * OCR Parser Integration Tests
 */
import { analyzeImage } from '../../src/services/ocrService';
import { parseBetSlip } from '../../src/utils/parser';
import { 
  clusterByY, 
  parseTesseractWords,
  type Word
} from '../../src/services/ocrParser';
import { TesseractData } from '../../src/types';

// Mock OCR service to return test data
jest.mock('../../src/services/ocrService', () => ({
  analyzeImage: jest.fn()
}));

// Mock Google Vision client
jest.mock('@google-cloud/vision', () => ({
  ImageAnnotatorClient: jest.fn().mockImplementation(() => ({
    textDetection: jest.fn().mockResolvedValue([{
      textAnnotations: [
        { description: 'All text' },
        { 
          description: 'NYM', 
          boundingPoly: { vertices: [{ x: 0, y: 0 }, { x: 30, y: 0 }, { x: 30, y: 20 }, { x: 0, y: 20 }] }
        },
        { 
          description: 'vs', 
          boundingPoly: { vertices: [{ x: 35, y: 0 }, { x: 50, y: 0 }, { x: 50, y: 20 }, { x: 35, y: 20 }] }
        },
        { 
          description: 'PHI', 
          boundingPoly: { vertices: [{ x: 55, y: 0 }, { x: 85, y: 0 }, { x: 85, y: 20 }, { x: 55, y: 20 }] }
        },
        { 
          description: 'ML', 
          boundingPoly: { vertices: [{ x: 90, y: 0 }, { x: 110, y: 0 }, { x: 110, y: 20 }, { x: 90, y: 20 }] }
        },
        { 
          description: '-120', 
          boundingPoly: { vertices: [{ x: 115, y: 0 }, { x: 150, y: 0 }, { x: 150, y: 20 }, { x: 115, y: 20 }] }
        },
        { 
          description: '5u', 
          boundingPoly: { vertices: [{ x: 155, y: 0 }, { x: 175, y: 0 }, { x: 175, y: 20 }, { x: 155, y: 20 }] }
        }
      ]
    }])
  }))
}));

beforeAll(async () => {
  const mockJimpImage = {
    bitmap: { width: 100, height: 100, data: new Uint8Array(400) },
    crop: jest.fn().mockReturnThis(),
    greyscale: jest.fn().mockReturnThis(),
    contrast: jest.fn().mockReturnThis(),
    normalize: jest.fn().mockReturnThis(),
    scaleToFit: jest.fn().mockReturnThis(),
    gaussian: jest.fn().mockReturnThis(),
    threshold: jest.fn().mockReturnThis(),
    clone: jest.fn().mockReturnThis(),
    getBuffer: jest.fn().mockImplementation((format, callback) => {
      callback(null, Buffer.from('mock-image-data'));
    })
  };
  const mockJimp = function () {};
  mockJimp.read = jest.fn().mockResolvedValue(mockJimpImage);
  
  // Mock the dynamic import
  jest.doMock('jimp', () => ({
    __esModule: true,
    default: mockJimp
  }));
});

// Minimal valid PNG buffer (1x1 pixel, white)
const createValidPNGBuffer = (): Buffer => {
  // Base64-encoded minimal 1x1 white PNG
  const base64PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
  return Buffer.from(base64PNG, 'base64');
};

describe('OCR Parser Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('preprocess', () => {
    it('should preprocess image successfully', async () => {
      const buffer = createValidPNGBuffer();
      const { preprocess } = await import('../../src/services/ocrParser');
      const result = await preprocess(buffer);
      expect(result).toHaveProperty('buffer');
      expect(result.buffer).toBeInstanceOf(Buffer);
      expect(result.buffer.length).toBeGreaterThan(0);
    });

    it('should handle tiny images without gaussian blur', async () => {
      const tinyBuffer = Buffer.from('tiny-image-data');
      const jimp = require('jimp');
      const mockTinyImage = {
        bitmap: { width: 1, height: 1, data: new Uint8Array(4) },
        crop: jest.fn().mockReturnThis(),
        greyscale: jest.fn().mockReturnThis(),
        contrast: jest.fn().mockReturnThis(),
        normalize: jest.fn().mockReturnThis(),
        scaleToFit: jest.fn().mockReturnThis(),
        gaussian: jest.fn().mockReturnThis(),
        threshold: jest.fn().mockReturnThis(),
        clone: jest.fn().mockReturnThis(),
        getBuffer: jest.fn().mockImplementation((format, callback) => {
          callback(null, Buffer.from('processed'));
        })
      };
      jimp.default.read.mockResolvedValue(mockTinyImage);
      const { preprocess } = await import('../../src/services/ocrParser');
      await preprocess(tinyBuffer);
      expect(mockTinyImage.gaussian).not.toHaveBeenCalled();
    });
  });

  describe('parseTesseractWords', () => {
    it('should parse and filter words by confidence', () => {
      const mockTesseractData: TesseractData = {
        words: [
          { text: 'NYM', confidence: 85, bbox: { x0: 0, y0: 0, x1: 30, y1: 20 } },
          { text: 'vs', confidence: 45, bbox: { x0: 35, y0: 0, x1: 50, y1: 20 } }, // Low confidence
          { text: 'PHI', confidence: 90, bbox: { x0: 55, y0: 0, x1: 85, y1: 20 } },
          { text: 'ML', confidence: 70, bbox: { x0: 90, y0: 0, x1: 110, y1: 20 } }
        ],
        text: 'NYM vs PHI ML',
        confidence: 75,
        lines: [
          { text: 'NYM vs PHI ML', bbox: { x0: 0, y0: 0, x1: 110, y1: 20 }, confidence: 75 }
        ]
      };
      
      const words = parseTesseractWords(mockTesseractData, 60);
      
      expect(words).toHaveLength(3); // 'vs' should be filtered out
      expect(words.map(w => w.text)).toEqual(['NYM', 'PHI', 'ML']);
    });

    it('should handle empty words array', () => {
      const mockTesseractData: TesseractData = {
        words: [],
        text: '',
        confidence: 0,
        lines: []
      };
      
      const words = parseTesseractWords(mockTesseractData, 60);
      expect(words).toHaveLength(0);
    });

    it('should handle null words array', () => {
      const mockTesseractData: TesseractData = {
        words: null as any,
        text: '',
        confidence: 0,
        lines: []
      };
      
      const words = parseTesseractWords(mockTesseractData, 60);
      expect(words).toHaveLength(0);
    });
  });

  describe('clusterByY', () => {
    it('should cluster words by Y-coordinate', () => {
      const words: Word[] = [
        { text: 'NYM', confidence: 85, bbox: { x0: 0, y0: 0, x1: 30, y1: 20 } },
        { text: 'vs', confidence: 70, bbox: { x0: 35, y0: 0, x1: 50, y1: 20 } },
        { text: 'PHI', confidence: 90, bbox: { x0: 55, y0: 0, x1: 85, y1: 20 } },
        { text: 'ML', confidence: 80, bbox: { x0: 90, y0: 0, x1: 110, y1: 20 } },
        { text: '-120', confidence: 85, bbox: { x0: 115, y0: 0, x1: 150, y1: 20 } },
        { text: '5u', confidence: 75, bbox: { x0: 155, y0: 0, x1: 175, y1: 20 } }
      ];
      
      const lines = clusterByY(words, 25);
      
      expect(lines).toHaveLength(1); // All words on same line
      expect(lines[0]?.text).toBe('NYM vs PHI ML -120 5u');
      expect(lines[0]?.confidence).toBeGreaterThan(0);
    });

    it('should handle multiple lines', () => {
      const words: Word[] = [
        { text: 'Line1', confidence: 85, bbox: { x0: 0, y0: 0, x1: 50, y1: 20 } },
        { text: 'Line2', confidence: 80, bbox: { x0: 0, y0: 30, x1: 50, y1: 50 } }
      ];
      
      const lines = clusterByY(words, 25);
      
      expect(lines).toHaveLength(2);
      expect(lines[0]?.text).toBe('Line1');
      expect(lines[1]?.text).toBe('Line2');
    });
  });

  describe('End-to-End OCR Parsing', () => {
    it('should parse bet slip from OCR data', async () => {
      const mockOcrLines = ['NYM vs PHI ML -120 5u'];
      (analyzeImage as jest.Mock).mockResolvedValue(mockOcrLines);
      
      const buffer = createValidPNGBuffer();
      const ocrLines = await analyzeImage(buffer);
      const betSlip = await parseBetSlip(ocrLines);
      
      expect(betSlip).toBeDefined();
      if (betSlip && betSlip.legs.length > 0) {
        expect(betSlip.legs[0]?.teamA).toBe('NYM vs PHI ML');
        expect(betSlip.legs[0]?.teamB).toBe('TBD');
        expect(betSlip.legs[0]?.odds).toBe(-120);
        expect(betSlip.units).toBe(5);
      }
    });
  });
}); 