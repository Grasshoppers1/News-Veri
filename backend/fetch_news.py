import requests
from config.config import NEWSAPI_KEY
from datetime import datetime, timedelta
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class NewsFetcher:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("mrm8488/bert-tiny-finetuned-fake-news-detection")
        self.model = AutoModelForSequenceClassification.from_pretrained("mrm8488/bert-tiny-finetuned-fake-news-detection")



    def detect_fake_news(self, text):
        if not text:
            return "Unknown"
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        fake_prob = probs[0][1].item()  # probability of class 1 (Fake)
        return fake_prob



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
        results = []
        for a in data:
            content = f"{a.get('title', '')} {a.get('description', '')}"
            results.append({
                'title': a['title'],
                'description': a.get('description'),
                'url': a['url'],
                'published_at': datetime.fromisoformat(a['publishedAt'].rstrip('Z')),
                'fake_news': self.detect_fake_news(content)  # << ADD FAKE NEWS TAG
            })
        return results