# ai_analysis.py

#!/usr/bin/env python3
"""
ai_analysis.py

Enhanced AI-powered betting analysis using OpenAI GPT-4.
Provides detailed analysis with edge calculations, risk assessment,
and betting recommendations.
"""
import logging
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

import openai
from openai import AsyncOpenAI


from .config import OPENAI_API_KEY, OPENAI_MODEL, ANALYSIS_TEMPERATUREfrom data_enrichment import enrich_bet_analysis
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


class BettingAnalysisError(Exception):
    """Custom exception for betting analysis errors."""
    pass


async def analyze_bet_slip(
    bet_details: Dict[str, Any],
    user_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Comprehensive AI analysis of a betting slip.
    
    Args:
        bet_details: Parsed bet information from OCR
        user_context: Optional user-provided context or notes
        
    Returns:
        Dict containing detailed analysis and recommendations
    """
    try:
        logger.info(f"Starting AI analysis for bet type: {bet_details.get('type', 'unknown')}")
        
        # Enrich with dynamic data
        enriched_data = await enrich_bet_analysis(bet_details)
        
        # Generate AI analysis
        analysis = await _generate_ai_analysis(enriched_data, user_context)
        
        # Add metadata
        analysis['metadata'] = {
            'analysis_timestamp': datetime.now().isoformat(),
            'model_used': OPENAI_MODEL,
            'bet_type': bet_details.get('type', 'unknown')
        }
        
        logger.info("AI analysis completed successfully")
        return analysis
        
    except Exception as e:
        logger.exception("Failed to analyze bet slip")
        raise BettingAnalysisError(f"Analysis failed: {str(e)}")


async def _generate_ai_analysis(
    enriched_data: Dict[str, Any],
    user_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate AI analysis using OpenAI GPT-4.
    """
    
    # Build comprehensive prompt
    prompt = _build_analysis_prompt(enriched_data, user_context)
    
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": _get_system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=ANALYSIS_TEMPERATURE,
            max_tokens=2000
        )
        
        # Parse AI response
        ai_response = response.choices[0].message.content
        if ai_response is None:
            raise BettingAnalysisError("Empty response from OpenAI API")
        analysis = _parse_ai_response(ai_response)
        
        return analysis
        
    except openai.RateLimitError:
        logger.error("OpenAI rate limit exceeded")
        raise BettingAnalysisError("Rate limit exceeded. Please try again later.")
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise BettingAnalysisError(f"API error: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error in AI analysis")

        raise BettingAnalysisError(f"Unexpected error: {str(e)}")

def _get_system_prompt() -> str:
    """Get the system prompt for AI analysis."""
    return """You are an expert sports betting analyst with deep knowledge of MLB statistics, 
    betting markets, and risk assessment. Your role is to provide comprehensive analysis of betting slips.

    ANALYSIS REQUIREMENTS:
    1. **Risk Assessment**: Evaluate the risk level (Low/Medium/High) based on bet type, odds, and historical data
    2. **Edge Analysis**: Calculate and explain the betting edge using implied vs true probability
    3. **Confidence Rating**: Provide a confidence score (1-10) with detailed reasoning
    4. **Recommendation**: Give a clear Bet/Pass/Consider recommendation with justification
    5. **Key Factors**: Identify the most important factors affecting this bet
    6. **Historical Context**: Reference relevant historical data and trends
    7. **Market Analysis**: Consider current betting market conditions

    RESPONSE FORMAT:
    Provide your analysis in the following JSON structure:
    {
        "risk_assessment": {
            "level": "Low/Medium/High",
            "reasoning": "Detailed explanation of risk factors"
        },
        "edge_analysis": {
            "implied_probability": 0.XX,
            "true_probability": 0.XX,
            "edge_percentage": X.X,
            "explanation": "Detailed edge calculation explanation"
        },
        "confidence_rating": {
            "score": X,
            "reasoning": "Detailed confidence explanation"
        },
        "recommendation": {
            "action": "Bet/Pass/Consider",
            "reasoning": "Detailed recommendation explanation",
            "stake_suggestion": "Percentage of bankroll (1-5%)"
        },
        "key_factors": [
            "Factor 1 with explanation",
            "Factor 2 with explanation",
            "Factor 3 with explanation"
        ],
        "historical_context": "Relevant historical data and trends",
        "market_analysis": "Current market conditions and implications"
    }

    Be thorough, analytical, and provide actionable insights. Use specific data points when available."""


def _build_analysis_prompt(
    enriched_data: Dict[str, Any],
    user_context: Optional[str] = None
) -> str:
    """Build the analysis prompt with all available data."""
    
    prompt_parts = []
    
    # Basic bet information
    prompt_parts.append(f"BET DETAILS:")
    prompt_parts.append(f"- Type: {enriched_data.get('type', 'Unknown')}")
    prompt_parts.append(f"- Bet: {enriched_data.get('bet', 'Unknown')}")
    prompt_parts.append(f"- Odds: {enriched_data.get('odds', 'Unknown')}")
    
    # Game information
    if 'game_info' in enriched_data:
        game_info = enriched_data['game_info']
        prompt_parts.append(f"\nGAME INFORMATION:")
        prompt_parts.append(f"- Game: {enriched_data.get('game', 'Unknown')}")
        prompt_parts.append(f"- Time: {game_info.get('game_time', 'Unknown')}")
        prompt_parts.append(f"- Venue: {game_info.get('venue', 'Unknown')}")
        
        if 'weather' in game_info:
            weather = game_info['weather']
            prompt_parts.append(f"- Weather: {weather.get('temperature', 'Unknown')}, {weather.get('conditions', 'Unknown')}")
            prompt_parts.append(f"- Wind: {weather.get('wind_speed', 'Unknown')} {weather.get('wind_direction', 'Unknown')}")
        
        if 'starting_pitchers' in game_info:
            pitchers = game_info['starting_pitchers']
            prompt_parts.append(f"- Pitchers: {pitchers.get('team1_pitcher', 'TBD')} vs {pitchers.get('team2_pitcher', 'TBD')}")
    
    # H2H statistics
    if 'h2h_stats' in enriched_data:
        h2h = enriched_data['h2h_stats']
        prompt_parts.append(f"\nHEAD-TO-HEAD STATISTICS:")
        prompt_parts.append(f"- {enriched_data.get('away', 'Team1')} wins: {h2h.get('team1_wins', 0)}")
        prompt_parts.append(f"- {enriched_data.get('home', 'Team2')} wins: {h2h.get('team2_wins', 0)}")
        prompt_parts.append(f"- Avg runs: {h2h.get('avg_runs_team1', 0)} vs {h2h.get('avg_runs_team2', 0)}")
    
    # Player statistics for props
    if 'player_stats' in enriched_data:
        player_stats = enriched_data['player_stats']
        prompt_parts.append(f"\nPLAYER STATISTICS:")
        prompt_parts.append(f"- Player: {enriched_data.get('player', 'Unknown')}")
        # Add relevant stats based on prop type
        if 'AVG' in player_stats:
            prompt_parts.append(f"- Season AVG: {player_stats.get('AVG', 'Unknown')}")
        if 'HR' in player_stats:
            prompt_parts.append(f"- Season HR: {player_stats.get('HR', 'Unknown')}")
    
    # Edge analysis
    if 'edge_analysis' in enriched_data:
        edge = enriched_data['edge_analysis']
        prompt_parts.append(f"\nEDGE ANALYSIS:")
        prompt_parts.append(f"- Implied Probability: {edge.get('implied_probability', 0):.3f}")
        prompt_parts.append(f"- True Probability: {edge.get('true_probability', 0):.3f}")
        prompt_parts.append(f"- Edge: {edge.get('edge_percentage', 0):.2f}%")
    
    # User context
    if user_context:
        prompt_parts.append(f"\nUSER CONTEXT:")
        prompt_parts.append(user_context)
    
    return "\n".join(prompt_parts)


def _parse_ai_response(ai_response: str) -> Dict[str, Any]:
    """Parse the AI response into structured data."""
    try:
        # Try to extract JSON from the response
        json_start = ai_response.find('{')
        json_end = ai_response.rfind('}') + 1
        
        if json_start != -1 and json_end != 0:
            json_str = ai_response[json_start:json_end]
            return json.loads(json_str)
        else:
            # Fallback: return raw response
            logger.warning("Could not parse JSON from AI response")
            return {
                "raw_analysis": ai_response,
                "parsing_error": "Could not extract structured data"
            }
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response JSON: {e}")
        return {
            "raw_analysis": ai_response,
            "parsing_error": f"JSON decode error: {str(e)}"
        }
    except Exception as e:
        logger.exception("Error parsing AI response")
        return {
            "raw_analysis": ai_response,
            "parsing_error": f"Unexpected error: {str(e)}"
        }


async def generate_pick_summary(
    bet_details: Dict[str, Any],
    analysis: Dict[str, Any],
    pick_type: str
) -> str:
    """
    Generate a formatted pick summary for Discord posting.
    
    Args:
        bet_details: Original bet details
        analysis: AI analysis results
        pick_type: Type of pick (vip, lotto, free)
        
    Returns:
        Formatted string for Discord
    """
    
    # Pick number
    pick_number = await _get_next_pick_number(pick_type)
    
    # Build summary
    summary_parts = []
    
    # Header
    summary_parts.append(f"🔒 **GOTLOCKZ {pick_type.upper()} PICK #{pick_number}** 🔒")
    summary_parts.append("")
    
    # Bet details
    summary_parts.append(f"**Bet:** {bet_details.get('bet', 'Unknown')}")
    summary_parts.append(f"**Odds:** {bet_details.get('odds', 'Unknown')}")
    
    if 'game' in bet_details:
        summary_parts.append(f"**Game:** {bet_details.get('game', 'Unknown')}")
    
    # Analysis highlights
    if 'recommendation' in analysis:
        rec = analysis['recommendation']
        summary_parts.append(f"**Recommendation:** {rec.get('action', 'Unknown')}")
        
        if 'stake_suggestion' in rec:
            summary_parts.append(f"**Stake:** {rec.get('stake_suggestion', 'Unknown')}")
    
    if 'confidence_rating' in analysis:
        conf = analysis['confidence_rating']
        score = conf.get('score', 0)
        summary_parts.append(f"**Confidence:** {score}/10")
    
    if 'edge_analysis' in analysis:
        edge = analysis['edge_analysis']
        edge_pct = edge.get('edge_percentage', 0)
        summary_parts.append(f"**Edge:** {edge_pct:.2f}%")
    
    # Risk assessment
    if 'risk_assessment' in analysis:
        risk = analysis['risk_assessment']
        summary_parts.append(f"**Risk:** {risk.get('level', 'Unknown')}")
    
    # Key factors (first 2)
    if 'key_factors' in analysis and analysis['key_factors']:
        factors = analysis['key_factors'][:2]  # Limit to first 2
        summary_parts.append("**Key Factors:**")
        for factor in factors:
            summary_parts.append(f"• {factor}")
    
    # Footer
    summary_parts.append("")
    summary_parts.append("🎯 *Powered by GotLockz AI Analysis*")
    
    return "\n".join(summary_parts)


async def _get_next_pick_number(pick_type: str) -> int:
    """Get the next pick number for the given type."""
    # This would typically read from a database or file
    # For now, return a placeholder
    return 1  # TODO: Implement proper pick numbering


async def validate_analysis_quality(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the quality and completeness of AI analysis.
    """
    validation = {
        "is_valid": True,
        "missing_fields": [],
        "quality_score": 0,
        "warnings": []
    }
    
    required_fields = [
        "risk_assessment", "edge_analysis", "confidence_rating",
        "recommendation", "key_factors"
    ]
    
    # Check for required fields
    for field in required_fields:
        if field not in analysis:
            validation["missing_fields"].append(field)
            validation["is_valid"] = False
    
    # Quality scoring
    score = 0
    if "risk_assessment" in analysis:
        score += 20
    if "edge_analysis" in analysis:
        score += 25
    if "confidence_rating" in analysis:
        score += 20
    if "recommendation" in analysis:
        score += 25
    if "key_factors" in analysis:
        score += 10
    
    validation["quality_score"] = score
    
    # Add warnings for low quality
    if score < 80:
        validation["warnings"].append("Analysis quality below threshold")
    
    return validation
