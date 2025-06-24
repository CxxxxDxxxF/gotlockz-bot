"""
Analysis Service - AI-powered MLB betting analysis
"""
import logging
from typing import Dict, Any, Optional
import openai
import random

from src.config.settings import settings

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
        """Build context for AI analysis."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            is_parlay = bet_data.get('is_parlay', False)
            
            context = f"""
            MLB Betting Analysis Context:
            
            Teams: {teams[0]} vs {teams[1]}
            Bet Type: {description}
            Odds: {odds}
            Parlay: {'Yes' if is_parlay else 'No'}
            """
            
            if stats_data:
                team1_stats = stats_data.get('team1', {})
                team2_stats = stats_data.get('team2', {})
                
                context += f"""
                
            Team Statistics:
            
            {teams[0]}:
            - Record: {team1_stats.get('wins', 0)}-{team1_stats.get('losses', 0)}
            - Win %: {team1_stats.get('win_pct', 0):.3f}
            - Runs Scored: {team1_stats.get('runs_scored', 0)}
            - Runs Allowed: {team1_stats.get('runs_allowed', 0)}
            - Run Differential: {team1_stats.get('run_diff', 0)}
            - Games Played: {team1_stats.get('games_played', 0)}
            
            {teams[1]}:
            - Record: {team2_stats.get('wins', 0)}-{team2_stats.get('losses', 0)}
            - Win %: {team2_stats.get('win_pct', 0):.3f}
            - Runs Scored: {team2_stats.get('runs_scored', 0)}
            - Runs Allowed: {team2_stats.get('runs_allowed', 0)}
            - Run Differential: {team2_stats.get('run_diff', 0)}
            - Games Played: {team2_stats.get('games_played', 0)}
            """
            
            return context
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            return "Error building analysis context"
    
    async def _generate_ai_analysis(self, context: str) -> str:
        """Generate AI analysis using OpenAI with a dynamic intro, bolded key phrases, and three concise paragraphs."""
        try:
            intros = [
                "GotLockz family, Free Play is here!",
                "Free Play drop for the squad!",
                "Let's get into today's edge!",
                "Alright team, here's today's Free Play!",
                "Lockz fam, let's break down today's best spot!"
            ]
            intro = random.choice(intros)
            prompt = f"""
Write as if you're a sharp, trusted MLB bettor talking to your 21+ Discord community. Use Discord bold markdown (**text**) for key teams, stats, or phrases. Write exactly three short paragraphs:
1. Why this matchup/bet is interesting
2. The key stats/factors (pitching, park, weather, odds)
3. A confident, concise call to action
Each paragraph should be 2-3 sentences, direct and to the point. Use a mature, confident, stats-driven, and slightly witty tone. No corny or kid language. Use emojis only for emphasis, not as filler or punchlines. End with 'Let's cash.' or 'Lock it in.'
Do NOT generate an intro, the intro will be provided. Start your response directly with the first paragraph.

Here's the context for the bet:
{context}
"""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a sharp, trusted MLB bettor writing for a 21+ Discord audience. Use a mature, confident, stats-driven, and slightly witty tone. Avoid corny or kid language and forced hype. Use Discord bold markdown (**text**) for key teams, stats, or phrases. Write exactly three short paragraphs as described. Use emojis only for emphasis. Do NOT generate an intro, the intro will be provided. Start your response directly with the first paragraph. End with 'Let's cash.' or 'Lock it in.'"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=350,
                temperature=0.76
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
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            
            if teams[0] == 'TBD' or teams[1] == 'TBD':
                return "GotLockz family, Free Play is here!\n\nAnalysis: Unable to extract team information from the betting slip. Please verify the image quality and try again."
            
            if description == 'TBD':
                return f"GotLockz family, Free Play is here!\n\nAnalysis: MLB betting pick for {teams[0]} vs {teams[1]}. Please review the betting slip for specific bet details and odds."
            
            return f"GotLockz family, Free Play is here!\n\nAnalysis: {description} for {teams[0]} vs {teams[1]} at {odds}. Review recent team performance, pitching matchups, and head-to-head statistics before placing this bet. Let's cash."
            
        except Exception as e:
            logger.error(f"Error generating fallback analysis: {e}")
            return "GotLockz family, Free Play is here!\n\nAnalysis: Unable to generate analysis at this time. Please review the betting slip manually."
    
    async def generate_quick_analysis(self, bet_data: Dict[str, Any]) -> str:
        """Generate a quick analysis without API calls."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            
            if teams[0] == 'TBD' or teams[1] == 'TBD':
                return "Quick Analysis: Team information not detected. Please ensure the betting slip image is clear and contains team names."
            
            # Generate basic analysis based on bet type
            if 'over' in description.lower():
                return f"Quick Analysis: Over bet for {teams[0]} vs {teams[1]}. Consider recent scoring trends and pitching matchups."
            elif 'under' in description.lower():
                return f"Quick Analysis: Under bet for {teams[0]} vs {teams[1]}. Review recent defensive performance and weather conditions."
            else:
                return f"Quick Analysis: {description} for {teams[0]} vs {teams[1]}. Check recent form and head-to-head statistics."
            
        except Exception as e:
            logger.error(f"Error generating quick analysis: {e}")
            return "Quick Analysis: Unable to analyze at this time."
    
    async def generate_risk_assessment(self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate risk assessment for the bet."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            is_parlay = bet_data.get('is_parlay', False)
            
            if teams[0] == 'TBD' or teams[1] == 'TBD':
                return "Risk Assessment: Unable to assess risk without team information."
            
            risk_factors = []
            
            # Check if it's a parlay
            if is_parlay:
                risk_factors.append("Parlay bet - higher risk due to multiple outcomes required")
            
            # Check if we have stats
            if stats_data:
                team1_stats = stats_data.get('team1', {})
                team2_stats = stats_data.get('team2', {})
                
                # Check for close records
                team1_wins = team1_stats.get('wins', 0)
                team1_losses = team1_stats.get('losses', 0)
                team2_wins = team2_stats.get('wins', 0)
                team2_losses = team2_stats.get('losses', 0)
                
                if abs((team1_wins - team1_losses) - (team2_wins - team2_losses)) <= 5:
                    risk_factors.append("Close team records - unpredictable outcome")
                
                # Check for high scoring teams
                if team1_stats.get('runs_scored', 0) > 500 or team2_stats.get('runs_scored', 0) > 500:
                    risk_factors.append("High scoring teams - consider over/under implications")
            
            if not risk_factors:
                return "Risk Assessment: Standard risk level. Review recent performance and trends."
            
            return f"Risk Assessment: {'; '.join(risk_factors)}"
            
        except Exception as e:
            logger.error(f"Error generating risk assessment: {e}")
            return "Risk Assessment: Unable to assess risk at this time." 