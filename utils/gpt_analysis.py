import os
import openai
from typing import Dict, Any, Optional

def generate_analysis(bet_info: str, game_stats: Optional[Dict[str, Any]] = None) -> str:
    """Use OpenAI to generate analysis text for the bet."""
    try:
        # Use new OpenAI API format
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""Provide a concise analysis for this betting pick: {bet_info}
        
        Consider:
        - Team performance trends
        - Head-to-head statistics
        - Recent form
        - Key factors affecting the outcome
        
        Provide a brief, professional analysis."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        return content.strip() if content else "Analysis unavailable"
        
    except Exception as e:
        return f"Analysis unavailable: {str(e)}"

def generate_pick_summary(bet_details: Dict[str, Any], confidence: int = 7) -> str:
    """Generate a summary for a betting pick."""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""Create a brief summary for this betting pick:
        
        Bet Details: {bet_details}
        Confidence Level: {confidence}/10
        
        Provide a 2-3 sentence summary highlighting key points."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.5
        )
        
        content = response.choices[0].message.content
        return content.strip() if content else "Summary unavailable"
        
    except Exception as e:
        return "Summary unavailable"
