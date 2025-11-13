# In news/utils.py

import os
import feedparser  # 👈 Import the new library
from datetime import date
from django.conf import settings
from .models import DailyNews
from openai import OpenAI

# --- Setup ---
client = OpenAI()
try:
    # This is the primary way to get the key
    NEWS_API_KEY = settings.NEWS_API_KEY
except AttributeError:
    # This is a fallback for running scripts outside the full Django app
    from dotenv import load_dotenv
    env_path = os.path.expanduser('~/django_projects/mysite/.env')
    load_dotenv(env_path)
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# --- Prompts for the AI ---
system_prompt = """
You are an expert Indian journalist.
"""

def create_user_prompt(articles):
    """Formats a list of articles into a string for the OpenAI prompt."""
    prompt_text = "Here are today's top headlines from various Indian news sources. Please synthesize them into a summary:\n\n---\n\n"
    for article in articles:
        prompt_text += f"Source: {article['source']}\n"
        prompt_text += f"Headline: {article['title']}\n"
        prompt_text += f"Description: {article.get('description', 'N/A')}\n\n"
    prompt_text +='''
    Sample output is as under:
    <div class="section">
    <h2 id="snap-insight" style="margin:0.5rem 0; letter-spacing:0.3px;">
    Snap Insight
    </h2>
    <p style="margin:0; font-size:0.95rem; opacity:0.8;">
    Quick takes on headlines & editorials
    </p>
    <ul style="font-family: Arial, sans-serif; font-size: clamp(1.5rem, 2.5vw, 2rem); line-height: 1.6;">
        <li>Headline 1 here</li>
        <li>Headline 2 here</li>
        <li>Headline 3 here</li>
    </ul>
    <h2>Editorial Summary</h2>
    <p style="font-family: Arial, sans-serif; font-size: 20px; line-height: 1.6;">
        In summary, today’s headlines highlight [main theme, e.g., “economic recovery, global trade, poltics, and technology growth”].
        The editorial emphasizes how these developments are interconnected, offering readers both the facts and the underlying context.
    </p>
    </div>
    '''
    return prompt_text

# --- New Helper Function to Fetch from RSS ---
def fetch_articles_from_rss(feed_urls):
    """
    Parses a list of RSS feed URLs and returns a structured list of articles.
    """
    all_articles = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        source_name = feed.feed.title
        for entry in feed.entries:
            article = {
                'source': source_name,
                'title': entry.title,
                'description': entry.summary if 'summary' in entry else 'No description available.',
                'link': entry.link
            }
            all_articles.append(article)
    return all_articles

# --- Main Function (Updated) ---
def get_or_update_today_news():
    """
    Fetches today's news summary. If not in the DB, it reads RSS feeds,
    synthesizes a summary with OpenAI, and saves it.
    """
    today = date.today()
    try:
        return DailyNews.objects.get(date=today)
    except DailyNews.DoesNotExist:
        try:
            # 1. Define your RSS feed sources
            list_of_feeds = [
                "https://www.thehindu.com/feeder/default.rss",
                "http://rss.cnn.com/rss/edition.rss",
                "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
                # You can add more feeds here!
            ]

            # 2. Fetch all articles from the defined RSS feeds
            articles_for_ai = fetch_articles_from_rss(list_of_feeds)

            if not articles_for_ai:
                raise ValueError("No articles could be fetched from the RSS feeds.")

            # 3. Prepare the data and prompt for OpenAI
            user_prompt = create_user_prompt(articles_for_ai[:15]) # Use top 15 articles

            # 4. Call OpenAI to synthesize the summary
            ai_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            # ... (Your robust OpenAI response check here) ...
            summary_html = ai_response.choices[0].message.content.strip()

            # 5. Create an attribution block
            sources = {article['source'] for article in articles_for_ai[:15]}
            attribution_html = '<p style="font-size: 0.8em; color: #555;"><em>Sources: ' + ', '.join(sorted(list(sources))) + '</em></p>'
            final_html = summary_html + attribution_html
            
            # 6. Save the new summary to the database
            return DailyNews.objects.create(date=today, summary_html=final_html)

        except Exception as e:
            # Catch any error and create a graceful failure message.
            print(f"An error occurred while generating news from RSS: {e}")
            error_summary = "<p>Today's news summary could not be generated at this time. Please check back later.</p>"
            news, created = DailyNews.objects.get_or_create(
                date=today,
                defaults={'summary_html': error_summary}
            )
            return news
