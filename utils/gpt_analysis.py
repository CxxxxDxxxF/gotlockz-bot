import os
import openai

def generate_analysis(bet_info, game_stats):
    """Use OpenAI to generate analysis text for the bet."""
    openai.api_key = os.getenv('OPENAI_API_KEY')
    prompt = f"Provide a concise analysis for this MLB bet: {bet_info}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()
