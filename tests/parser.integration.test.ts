import { parseBetSlip, BetSlip } from '../src/utils/parser';

describe('parseBetSlip integration', () => {
  it('parses a 2-leg SGP betslip correctly', async () => {
    const lines = [
      '2 Leg SGP +1750',
      'Rafael Devers 1+',
      'ALT Home Runs',
      'San Francisco Giants at Arizona Diamondbacks',
      'Willy Adames 1+',
      'ALT Home Runs',
      'San Francisco Giants at Arizona Diamondbacks'
    ];

    const result: BetSlip = await parseBetSlip(lines);

    expect(result.legs).toHaveLength(2);
    expect(result.legs[0]).toBeDefined();
    expect(result.legs[1]).toBeDefined();

    // Check first leg (Rafael Devers)
    expect(result.legs[0]!.teamA.toUpperCase()).toContain('RAFAEL DEVERS');
    expect(result.legs[0]!.teamB.toUpperCase()).toContain('ARIZONA DIAMONDBACKS');
    expect(typeof result.legs[0]!.odds).toBe('number');

    // Check second leg (Willy Adames)
    expect(result.legs[1]!.teamA.toUpperCase()).toContain('WILLY ADAMES');
    expect(result.legs[1]!.teamB.toUpperCase()).toContain('ARIZONA DIAMONDBACKS');
    expect(typeof result.legs[1]!.odds).toBe('number');
  });

  it('parses a single-leg ML betslip correctly', async () => {
    const lines = [
      'San Francisco Giants',
      'ML -145',
      'FanDuel'
    ];

    const result: BetSlip = await parseBetSlip(lines);

    expect(result.legs).toHaveLength(1);
    expect(result.legs[0]).toBeDefined();
    expect(result.legs[0]!.teamA.toUpperCase()).toBe('SAN FRANCISCO GIANTS');
    expect(typeof result.legs[0]!.teamB).toBe('string');
    expect(result.legs[0]!.odds).toBe(-145);
  });
}); 