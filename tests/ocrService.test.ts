import axios from 'axios';
import { analyzeImage } from '../src/services/ocrService';
import { getEnv } from '../src/utils/env';

// Mock dependencies
jest.mock('axios');
jest.mock('../src/utils/env');
jest.mock('tesseract.js');
jest.mock('../src/services/ocrParser');

const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockedGetEnv = getEnv as jest.MockedFunction<typeof getEnv>;

describe('OCR Service', () => {
  const mockImageBuffer = Buffer.from('fake-image-data');
  
  beforeEach(() => {
    jest.clearAllMocks();
    mockedGetEnv.mockReturnValue({
      DISCORD_BOT_TOKEN: 'test-token',
      DISCORD_CLIENT_ID: 'test-client-id',
      DISCORD_GUILD_ID: 'test-guild-id',
      OPENAI_API_KEY: 'test-openai-key',
      OCR_SPACE_API_KEY: 'test-ocr-key',
      GOOGLE_APPLICATION_CREDENTIALS: undefined,
      OPENWEATHERMAP_KEY: 'test-weather-key',
      PORT: undefined,
    });
  });

  describe('OCR.space timeout handling', () => {
    it('should fallback to Tesseract.js when OCR.space times out', async () => {
      // Mock OCR.space timeout error
      const timeoutError = new Error('timeout of 10000ms exceeded');
      (timeoutError as any).code = 'ECONNABORTED';
      (timeoutError as any).isAxiosError = true;
      
      mockedAxios.post.mockRejectedValueOnce(timeoutError);

      // Mock Tesseract.js to return some text
      const mockTesseract = require('tesseract.js');
      mockTesseract.recognize.mockResolvedValueOnce({
        data: {
          text: 'Test text from Tesseract',
          confidence: 85
        }
      });

      // Mock the advanced OCR parser to throw an error to trigger fallback
      const mockOcrParser = require('../src/services/ocrParser');
      mockOcrParser.parseImage.mockRejectedValueOnce(new Error('Advanced OCR failed'));

      const result = await analyzeImage(mockImageBuffer);

      // Verify OCR.space was called with timeout
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'https://api.ocr.space/parse/image',
        expect.any(FormData),
        expect.objectContaining({
          timeout: 10000
        })
      );

      // Verify Tesseract.js was called as fallback
      expect(mockTesseract.recognize).toHaveBeenCalled();

      // Verify we got some result
      expect(result).toEqual(['Test text from Tesseract']);
    });

    it('should fallback to Tesseract.js when OCR.space has connection error', async () => {
      // Mock OCR.space connection error
      const connectionError = new Error('connect ETIMEDOUT');
      (connectionError as any).code = 'ETIMEDOUT';
      (connectionError as any).isAxiosError = true;
      
      mockedAxios.post.mockRejectedValueOnce(connectionError);

      // Mock Tesseract.js to return some text
      const mockTesseract = require('tesseract.js');
      mockTesseract.recognize.mockResolvedValueOnce({
        data: {
          text: 'Test text from Tesseract',
          confidence: 85
        }
      });

      // Mock the advanced OCR parser to throw an error to trigger fallback
      const mockOcrParser = require('../src/services/ocrParser');
      mockOcrParser.parseImage.mockRejectedValueOnce(new Error('Advanced OCR failed'));

      const result = await analyzeImage(mockImageBuffer);

      // Verify Tesseract.js was called as fallback
      expect(mockTesseract.recognize).toHaveBeenCalled();

      // Verify we got some result
      expect(result).toEqual(['Test text from Tesseract']);
    });

    it('should skip OCR.space when no API key is provided', async () => {
      // Mock getEnv to return no OCR key
      mockedGetEnv.mockReturnValue({
        DISCORD_BOT_TOKEN: 'test-token',
        DISCORD_CLIENT_ID: 'test-client-id',
        DISCORD_GUILD_ID: 'test-guild-id',
        OPENAI_API_KEY: 'test-openai-key',
        OCR_SPACE_API_KEY: undefined,
        GOOGLE_APPLICATION_CREDENTIALS: undefined,
        OPENWEATHERMAP_KEY: 'test-weather-key',
        PORT: undefined,
      });

      // Mock Tesseract.js to return some text
      const mockTesseract = require('tesseract.js');
      mockTesseract.recognize.mockResolvedValueOnce({
        data: {
          text: 'Test text from Tesseract',
          confidence: 85
        }
      });

      // Mock the advanced OCR parser to throw an error to trigger fallback
      const mockOcrParser = require('../src/services/ocrParser');
      mockOcrParser.parseImage.mockRejectedValueOnce(new Error('Advanced OCR failed'));

      const result = await analyzeImage(mockImageBuffer);

      // Verify OCR.space was NOT called
      expect(mockedAxios.post).not.toHaveBeenCalled();

      // Verify Tesseract.js was called directly
      expect(mockTesseract.recognize).toHaveBeenCalled();

      // Verify we got some result
      expect(result).toEqual(['Test text from Tesseract']);
    });
  });
}); 