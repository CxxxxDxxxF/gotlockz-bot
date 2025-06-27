"""
Analysis Service - AI-powered MLB betting analysis
"""

import asyncio
import logging
import random
from typing import Any, Dict, Optional

import openai

from config.settings import settings

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for AI-powered MLB betting analysis."""

    def __init__(self):
        try:
            self.client = openai.OpenAI(api_key=settings.api.openai_api_key)
            self.model = settings.api.openai_model or "gpt-4"
            logger.info(f"OpenAI client initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise Exception(f"Failed to initialize OpenAI client: {e}")

    async def generate_analysis(self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate AI analysis for MLB betting data."""
        try:
            # Build context
            context = self._build_context(bet_data, stats_data)

            # Generate analysis
            analysis = await self._generate_ai_analysis(context)

            return analysis

        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return self._get_fallback_analysis(bet_data)

    def _build_context(self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]]) -> str:
        """Build context for AI analysis with enhanced stats."""
        try:
            teams = bet_data.get("teams", ["TBD", "TBD"])
            description = bet_data.get("description", "TBD")
            odds = bet_data.get("odds", "TBD")
            is_parlay = bet_data.get("is_parlay", False)

            context = f"""
            MLB Betting Analysis Context:
            
            Teams: {teams[0]} vs {teams[1]}
            Bet Type: {description}
            Odds: {odds}
            Parlay: {'Yes' if is_parlay else 'No'}
            """

            if stats_data:
                team1_stats = stats_data.get("team1", {})
                team2_stats = stats_data.get("team2", {})
                statcast_data = stats_data.get("statcast", {})
                park_factors = stats_data.get("park_factors", {})
                weather_data = stats_data.get("weather", {})

                context += f"""
                
            Advanced Team Statistics:
            
            {teams[0]}:
            - Record: {team1_stats.get('wins', 0)}-{team1_stats.get('losses', 0)} ({team1_stats.get('win_pct', 0):.3f})
            - Runs: {team1_stats.get('runs_scored', 0)} scored, {team1_stats.get('runs_allowed', 0)} allowed
            - Run Differential: {team1_stats.get('run_diff', 0)}
            - Batting: .{team1_stats.get('avg', 0):.3f} AVG, .{team1_stats.get('obp', 0):.3f} OBP, .{team1_stats.get('slg', 0):.3f} SLG
            - Pitching: {team1_stats.get('era', 0):.2f} ERA, {team1_stats.get('whip', 0):.2f} WHIP
            - Recent: {team1_stats.get('recent_wins', 0)}-{team1_stats.get('recent_losses', 0)} last {team1_stats.get('recent_games', 0)} games
            - Recent Avg: {team1_stats.get('avg_runs_scored', 0)} scored, {team1_stats.get('avg_runs_allowed', 0)} allowed
            
            {teams[1]}:
            - Record: {team2_stats.get('wins', 0)}-{team2_stats.get('losses', 0)} ({team2_stats.get('win_pct', 0):.3f})
            - Runs: {team2_stats.get('runs_scored', 0)} scored, {team2_stats.get('runs_allowed', 0)} allowed
            - Run Differential: {team2_stats.get('run_diff', 0)}
            - Batting: .{team2_stats.get('avg', 0):.3f} AVG, .{team2_stats.get('obp', 0):.3f} OBP, .{team2_stats.get('slg', 0):.3f} SLG
            - Pitching: {team2_stats.get('era', 0):.2f} ERA, {team2_stats.get('whip', 0):.2f} WHIP
            - Recent: {team2_stats.get('recent_wins', 0)}-{team2_stats.get('recent_losses', 0)} last {team2_stats.get('recent_games', 0)} games
            - Recent Avg: {team2_stats.get('avg_runs_scored', 0)} scored, {team2_stats.get('avg_runs_allowed', 0)} allowed
            """

                # Add Statcast data if available
                if statcast_data:
                    team1_statcast = statcast_data.get("team1", {})
                    team2_statcast = statcast_data.get("team2", {})

                    if team1_statcast or team2_statcast:
                        context += f"""
                
            Statcast Data (Last 30 Days):
            
            {teams[0]}:
            - Batting: {team1_statcast.get('batting', {}).get('avg_exit_velocity', 0)} mph exit velo, {team1_statcast.get('batting', {}).get('barrel_pct', 0)}% barrel rate
            - Pitching: {team1_statcast.get('pitching', {}).get('avg_velocity', 0)} mph avg velo, {team1_statcast.get('pitching', {}).get('whiff_pct', 0)}% whiff rate
            
            {teams[1]}:
            - Batting: {team2_statcast.get('batting', {}).get('avg_exit_velocity', 0)} mph exit velo, {team2_statcast.get('batting', {}).get('barrel_pct', 0)}% barrel rate
            - Pitching: {team2_statcast.get('pitching', {}).get('avg_velocity', 0)} mph avg velo, {team2_statcast.get('pitching', {}).get('whiff_pct', 0)}% whiff rate
            """

                if park_factors:
                    context += f"""
            
            Park Factors:
            - Runs: {park_factors.get('runs', 1.0):.2f}x (1.0 = neutral)
            - Home Runs: {park_factors.get('hr', 1.0):.2f}x
            - Strikeouts: {park_factors.get('k', 1.0):.2f}x
            - Walks: {park_factors.get('bb', 1.0):.2f}x
            """

                if weather_data:
                    context += f"""
            
            Weather Conditions:
            - Temperature: {weather_data.get('temperature', 72)}°F
            - Wind: {weather_data.get('wind_speed', 8)} mph {weather_data.get('wind_direction', 'SW')}
            - Humidity: {weather_data.get('humidity', 65)}%
            - Conditions: {weather_data.get('conditions', 'Partly Cloudy')}
            """

            return context

        except Exception as e:
            logger.error(f"Error building context: {e}")
            return "Error building analysis context"

    async def _generate_ai_analysis(self, context: str) -> str:
        """Generate AI analysis using OpenAI with enhanced stats-driven insights."""
        try:
            intros = [
                "GotLockz family, Free Play is here!",
                "Free Play drop for the squad!",
                "Let's get into today's edge!",
                "Alright team, here's today's Free Play!",
                "Lockz fam, let's break down today's best spot!",
            ]
            intro = random.choice(intros)
            prompt = f"""
You are a sharp, trusted MLB bettor analyzing for a 21+ Discord community. Use Discord bold markdown (**text**) for key teams, stats, or phrases. Write exactly three short paragraphs:

1. **Matchup Analysis**: Why this specific matchup/bet is interesting based on the advanced stats provided (recent form, park factors, weather, team trends)

2. **Key Factors**: Highlight the most relevant stats that support this bet (ERA, WHIP, recent performance, park factors, weather impact, run differentials)

3. **Confident Call**: A decisive, stats-backed conclusion with clear reasoning

Each paragraph should be 2-3 sentences, direct and analytical. Use a mature, confident, stats-driven tone. Reference specific numbers from the data provided. Use emojis sparingly and only for emphasis. End with 'Let's cash.' or 'Lock it in.'

Do NOT generate an intro - start directly with paragraph 1.

Context:
{context}
"""
            # Use asyncio to run the OpenAI call in a thread pool to prevent blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a sharp, trusted MLB bettor writing for a 21+ Discord audience. Use a mature, confident, stats-driven, and analytical tone. Avoid corny or kid language and forced hype. Use Discord bold markdown (**text**) for key teams, stats, or phrases. Write exactly three short paragraphs as described. Use emojis only for emphasis. Do NOT generate an intro, the intro will be provided. Start your response directly with the first paragraph. End with 'Let's cash.' or 'Lock it in.'",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=400,
                    temperature=0.7,
                ),
            )

            if response and response.choices and len(response.choices) > 0:
                message_content = response.choices[0].message.content
                if message_content:
                    analysis = message_content.strip()
                    return f"{intro}\n\n{analysis}"
                else:
                    logger.warning("Empty response from OpenAI API")
                    return f"{intro}\n\nAI analysis temporarily unavailable. Please check the betting data manually."
            else:
                logger.warning("No response choices from OpenAI API")
                return f"{intro}\n\nAI analysis temporarily unavailable. Please check the betting data manually."
        except openai.AuthenticationError:
            logger.error("OpenAI authentication failed - check API key")
            return "AI analysis unavailable: Authentication error. Please check OpenAI API configuration."
        except openai.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            return "AI analysis temporarily unavailable due to rate limits. Please try again later."
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return f"AI analysis unavailable: API error. Please try again later."
        except Exception as e:
            logger.error(f"Error generating AI analysis: {e}")
            return "AI analysis temporarily unavailable. Please check the betting data manually."

    def _get_fallback_analysis(self, bet_data: Dict[str, Any]) -> str:
        """Get fallback analysis when AI is unavailable."""
        try:
            teams = bet_data.get("teams", ["TBD", "TBD"])
            description = bet_data.get("description", "TBD")
            odds = bet_data.get("odds", "TBD")

            if teams[0] == "TBD" or teams[1] == "TBD":
                return "GotLockz family, Free Play is here!\n\nAnalysis: Unable to extract team information from the betting slip. Please verify the image quality and try again."

            if description == "TBD":
                return f"GotLockz family, Free Play is here!\n\nAnalysis: MLB betting pick for {teams[0]} vs {teams[1]}. Please review the betting slip for specific bet details and odds."

            return f"GotLockz family, Free Play is here!\n\nAnalysis: {description} for {teams[0]} vs {teams[1]} at {odds}. Review recent team performance, pitching matchups, and head-to-head statistics before placing this bet. Let's cash."

        except Exception as e:
            logger.error(f"Error generating fallback analysis: {e}")
            return "GotLockz family, Free Play is here!\n\nAnalysis: Unable to generate analysis at this time. Please review the betting slip manually."

    async def generate_quick_analysis(self, bet_data: Dict[str, Any]) -> str:
        """Generate a quick analysis without API calls."""
        try:
            teams = bet_data.get("teams", ["TBD", "TBD"])
            description = bet_data.get("description", "TBD")
            odds = bet_data.get("odds", "TBD")

            if teams[0] == "TBD" or teams[1] == "TBD":
                return "Quick Analysis: Team information not detected. Please ensure the betting slip image is clear and contains team names."

            # Generate basic analysis based on bet type
            if "over" in description.lower():
                return f"Quick Analysis: Over bet for {teams[0]} vs {teams[1]}. Consider recent scoring trends and pitching matchups."
            elif "under" in description.lower():
                return f"Quick Analysis: Under bet for {teams[0]} vs {teams[1]}. Review recent defensive performance and weather conditions."
            else:
                return f"Quick Analysis: {description} for {teams[0]} vs {teams[1]}. Check recent form and head-to-head statistics."

        except Exception as e:
            logger.error(f"Error generating quick analysis: {e}")
            return "Quick Analysis: Unable to analyze at this time."

    async def generate_risk_assessment(
        self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate risk assessment for the bet."""
        try:
            teams = bet_data.get("teams", ["TBD", "TBD"])
            description = bet_data.get("description", "TBD")
            is_parlay = bet_data.get("is_parlay", False)

            if teams[0] == "TBD" or teams[1] == "TBD":
                return "Risk Assessment: Unable to assess risk without team information."

            risk_level = "Medium"
            reasoning = []

            if is_parlay:
                risk_level = "High"
                reasoning.append("Parlay bets have higher variance")

            if stats_data:
                team1_stats = stats_data.get("team1", {})
                team2_stats = stats_data.get("team2", {})

                # Analyze recent performance
                team1_recent = team1_stats.get("recent_win_pct", 0.5)
                team2_recent = team2_stats.get("recent_win_pct", 0.5)

                if abs(team1_recent - team2_recent) > 0.3:
                    reasoning.append("Significant recent performance gap")
                elif abs(team1_recent - team2_recent) < 0.1:
                    reasoning.append("Teams performing similarly recently")

            return f"Risk Assessment: {risk_level}\nReasoning: {'; '.join(reasoning) if reasoning else 'Standard MLB betting risk'}"

        except Exception as e:
            logger.error(f"Error generating risk assessment: {e}")
            return "Risk Assessment: Unable to assess at this time."
