from pymongo import MongoClient, ASCENDING, TEXT
from datetime import datetime, timedelta
from config.config import MONGO_CONFIG
from sentiment import SentimentAnalyzer
from fetch_news import NewsFetcher

class MongoHandler:
    def __init__(self):
        self.client = MongoClient(MONGO_CONFIG['uri'])
        self.db = self.client[MONGO_CONFIG['db_name']]
        self.col = self.db[MONGO_CONFIG['collection']]
        self.sent = SentimentAnalyzer()
        self.fake_detector = NewsFetcher() 
        self._ensure_indexes()

    def _ensure_indexes(self):
        self.col.create_index([('query', ASCENDING), ('fetched_at', ASCENDING)])
        self.col.create_index([('url', ASCENDING)], unique=True)

    def get_cached(self, query: str, minutes: int = 10):
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return list(self.col.find({
            'query': query,
            'fetched_at': {'$gte': cutoff} },
            { "_id": False }
        ))
    
    def save_articles(self, query: str, articles: list[dict]):
        now = datetime.utcnow()
        for art in articles:
            art['query'] = query
            art['fetched_at'] = now
            content = f"{art['title']} {art.get('description','')}"
            art['sentiment'] = self.sent.analyze(content)['compound']
            art['fake_news_score'] = self.fake_detector.detect_fake_news(content)
            self.col.update_one(
                {'url': art['url']},
                {'$setOnInsert': art},
                upsert=True
            )



    def get_sentiment_trend(self, days: int = 7):
        pipeline = [
            {'$match': {
                'fetched_at': {'$gte': datetime.utcnow() - timedelta(days=days)}
            }},
            {'$group': {
                '_id': {'$dateToString': {'format':'%Y-%m-%d','date':'$fetched_at'}},
                'avg_sentiment': {'$avg':'$sentiment'}
            }},
            {'$sort': {'_id':1}}
        ]
        return list(self.col.aggregate(pipeline))