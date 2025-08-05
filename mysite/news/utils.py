from .models import DailyNews
from datetime import date

import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
#from IPython.display import Markdown, display
from openai import OpenAI

env_path = os.path.expanduser('~/django_projects/mysite/.env')
load_dotenv(env_path, override = True)
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:

    def __init__(self, url):
        """
        Create this Website object from the given url using the BeautifulSoup library
        """
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in html please do not mention the name of the website but mention To days news paper's abstract."

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of the headlines and editorial of this website in html. \
Only include news and head line, then summarize.\n\n"
    user_prompt += '''
Sample output is as under:
<div id="about" class="section">
    <h1>Todays Newspaper Abstract</h1>
    <h2>Top Headlines</h2>
    <h3>
        <ul>
            <li>news item you find 1</li>
            <li>item 2 here</li>
            .....
            <li>item n here</li>
        </ul>
    </h3>
    <h2>Editorial Summary</h2>
    <h3>
        <p>your editorial summary here</p>
    </h3>
</div>
'''

    user_prompt += website.text
    return user_prompt

def get_or_update_today_news():
    today = date.today()

    try:
        return DailyNews.objects.get(date=today)
    except DailyNews.DoesNotExist:
        # Fetch from web and save
        thehindu = Website("https://thehindu.com")
        user_prompt = user_prompt_for(thehindu)

        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        summary = response.choices[0].message.content.strip()

        news = DailyNews.objects.create(date=today, summary_html=summary)
        return news
