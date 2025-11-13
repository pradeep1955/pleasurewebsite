import openai
import os
from django.conf import settings
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_gpt_comment(symbol, latest_rsi, latest_macd, latest_signal):
    if 'DJANGO_SETTINGS_MODULE' in os.environ:
        from django.conf import settings
        api_key = settings.OPENAI_API_KEY
    else:
        api_key = os.getenv("OPENAI_API_KEY")  # fallback for script running

    print(f"API Key Used: {api_key}")

    if not api_key or api_key.startswith("default"):
        return "Missing or default API key. Please set it correctly."

    openai.api_key = api_key
    # (rest of your logic unchanged)


    if not api_key or api_key.startswith("default"):
        return "Missing or default API key. Please set it correctly."
    print(f"Loaded API Key: {api_key}")  # Print the key to confirm it's loaded
    openai.api_key = api_key  # Use the key for OpenAI API
    # Your existing logic here...
    prompt = f"""You are a financial market expert. Based on these indicators for {symbol}:
- RSI: {latest_rsi}
- MACD: {latest_macd}
- Signal Line: {latest_signal}

Give a concise, human-like expert stock commentary: Buy, Sell, Hold advice and short reasoning.
"""

    try:
        client = openai.OpenAI(api_key=openai.api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            timeout=20  # <-- Add this line
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error fetching AI commentary: {e}"


if __name__ == "__main__":
    comment = generate_gpt_comment("TCS.BO", 55, 1.2, 1.0)  # Example values
    print(f"Generated Comment: {comment}")
