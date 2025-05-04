import requests
from config.config import NEWSAPI_KEY
from datetime import datetime, timedelta

class NewsFetcher:
    BASE = 'https://newsapi.org/v2/everything'

    def fetch(self, query: str, days_back: int = 1) -> list[dict]:
        from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'publishedAt',
            'apiKey': NEWSAPI_KEY
        }
        resp = requests.get(self.BASE, params=params)
        data = resp.json().get('articles', [])
        return [
            {
                'title': a['title'],
                'description': a.get('description'),
                'url': a['url'],
                'published_at': datetime.fromisoformat(a['publishedAt'].rstrip('Z'))
            }
            for a in data
        ]