/**
 * OCR Parser Integration Tests
 */
import { analyzeImage } from '../../src/services/ocrService';
import { parseBetSlip } from '../../src/utils/parser';

// Mock OCR service to return test data
jest.mock('../../src/services/ocrService', () => ({
  analyzeImage: jest.fn()
}));

const mockAnalyzeImage = analyzeImage as jest.MockedFunction<typeof analyzeImage>;

describe('OCR Parser Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('parses a single-leg bet slip correctly', async () => {
    // Mock OCR text for a single bet
    const singleBetText = [
      'BET SLIP',
      'YANKEES VS RED SOX',
      'YANKEES +150',
      '1 UNIT'
    ];
    
    mockAnalyzeImage.mockResolvedValue(singleBetText);
    
    const slip = await parseBetSlip(singleBetText);
    
    expect(slip.type).toBe('SINGLE');
    expect(slip.legs).toHaveLength(1);
    if (slip.legs.length === 0) throw new Error('No legs parsed for single bet');
    const firstLeg = slip.legs[0]!;
    expect(firstLeg.teamA).toBe('YANKEES');
    expect(firstLeg.teamB).toBe('RED SOX');
    expect(firstLeg.odds).toBe(150);
    expect(slip.units).toBe(1);
  });

  it('parses a multi-leg parlay correctly', async () => {
    // Mock OCR text for a parlay
    const parlayText = [
      'PARLAY BET SLIP',
      '1) YANKEES VS RED SOX',
      'YANKEES +150',
      '2) DODGERS VS GIANTS',
      'DODGERS +120',
      '3) ASTROS VS RANGERS',
      'ASTROS +180',
      '2 UNITS'
    ];
    
    mockAnalyzeImage.mockResolvedValue(parlayText);
    
    const slip = await parseBetSlip(parlayText);
    
    expect(slip.type).toBe('PARLAY');
    expect(slip.legs.length).toBeGreaterThan(1);
    expect(slip.legs).toHaveLength(3);
    if (slip.legs.length < 3) throw new Error('Not all parlay legs parsed');
    const firstLeg = slip.legs[0]!;
    const secondLeg = slip.legs[1]!;
    const thirdLeg = slip.legs[2]!;
    expect(firstLeg.teamA).toBe('YANKEES');
    expect(firstLeg.teamB).toBe('RED SOX');
    expect(firstLeg.odds).toBe(150);
    expect(secondLeg.teamA).toBe('DODGERS');
    expect(secondLeg.teamB).toBe('GIANTS');
    expect(secondLeg.odds).toBe(120);
    expect(thirdLeg.teamA).toBe('ASTROS');
    expect(thirdLeg.teamB).toBe('RANGERS');
    expect(thirdLeg.odds).toBe(180);
    expect(slip.units).toBe(2);
  });

  it('handles different text formats gracefully', async () => {
    // Test alternative format
    const altText = [
      'BETTING SLIP',
      'YANKEES @ RED SOX +150',
      '0.5 UNITS'
    ];
    
    mockAnalyzeImage.mockResolvedValue(altText);
    
    const slip = await parseBetSlip(altText);
    
    expect(slip.type).toBe('SINGLE');
    expect(slip.legs).toHaveLength(1);
    if (slip.legs.length === 0) throw new Error('No legs parsed for alt format');
    const firstLeg = slip.legs[0]!;
    expect(firstLeg.teamA).toBe('YANKEES');
    expect(firstLeg.teamB).toBe('RED SOX');
    expect(firstLeg.odds).toBe(150);
    expect(slip.units).toBe(0.5);
  });

  it('defaults to 1 unit when no units specified', async () => {
    const noUnitsText = [
      'YANKEES VS RED SOX +150'
    ];
    
    mockAnalyzeImage.mockResolvedValue(noUnitsText);
    
    const slip = await parseBetSlip(noUnitsText);
    
    expect(slip.units).toBe(1);
  });

  it('handles malformed text gracefully', async () => {
    const malformedText = [
      'INVALID TEXT',
      'NO TEAMS OR ODDS'
    ];
    
    mockAnalyzeImage.mockResolvedValue(malformedText);
    
    const slip = await parseBetSlip(malformedText);
    
    expect(slip.legs).toHaveLength(0);
    expect(slip.units).toBe(1);
  });
}); 