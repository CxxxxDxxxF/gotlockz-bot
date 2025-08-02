/**
 * @typedef {Object} BetSlip
 * @property {string[]} teams
 * @property {number|null} odds
 * @property {string[]} players
 * @property {string|null} betType
 * @property {string|null} homeTeam
 * @property {string|null} awayTeam
 */

/**
 * Example bet slip schema object
 * @type {BetSlip}
 */
export const betSlipSchema = {
  teams: [],
  odds: null,
  players: [],
  betType: null,
  homeTeam: null,
  awayTeam: null
}; 