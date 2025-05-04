from flask import Flask, request, jsonify
from flask_cors import CORS
from mongo_handler import MongoHandler
from fetch_news import NewsFetcher

app = Flask(__name__)
CORS(app)

mongo = MongoHandler()
fetcher = NewsFetcher()

def fetch_or_cached(query):
    cached = mongo.get_cached(query)
    if cached:
        return cached
    arts = fetcher.fetch(query)
    
    mongo.save_articles(query, arts)
    return arts

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json() or {}
    q = data.get('query')
    if not q:
        return jsonify({'error':'Query missing'}),400
    res = fetch_or_cached(q)
    return jsonify(res)

@app.route('/sentiment-trend', methods=['GET'])
def trend():
    days = int(request.args.get('days',7))
    return jsonify(mongo.get_sentiment_trend(days))

if __name__ == '__main__':
    app.run(debug=True)