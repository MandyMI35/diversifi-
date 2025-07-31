from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import nltk 
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

# Load environment variables
load_dotenv()

nltk.download('vader_lexicon')
analyzer = SentimentIntensityAnalyzer()

app = FastAPI(title="Indian Stock News Fetcher",
description="Fetches 3 latest news headlines for Indian stocks",
version="1.0")

# Configuration
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
if not NEWSAPI_KEY:
    raise ValueError("Missing NEWSAPI_KEY in environment variables")

NEWSAPI_URL = "https://newsapi.org/v2/everything"

DATABASE_URL = "postgresql://postgres:postgres@host.docker.internal:5432/stock_news"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Company mapping for better relevance
COMPANY_MAPPING = {
    "RELIANCE": ["Reliance Industries", "RIL", "Mukesh Ambani"],
    "TCS": ["Tata Consultancy Services", "TCS Ltd"],
    "HDFCBANK": ["HDFC Bank", "Housing Development Finance Corporation"],
    "INFY": ["Infosys", "Infosys Limited"],
    "WIPRO": ["Wipro Limited", "Wipro Ltd"],
    "ITC": ["ITC Limited", "Indian Tobacco Company"],
    "BHARTIARTL": ["Bharti Airtel", "Airtel"],
    "SBIN": ["State Bank of India", "SBI"],
    "ICICIBANK": ["ICICI Bank"],
    "HINDUNILVR": ["Hindustan Unilever", "HUL"]
}

class StockSymbol(BaseModel):
    symbol: str

def is_recent_news(published_at: str) -> bool:
    """Check if news is from the last 14 days (more lenient)"""
    try:
        news_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        return (datetime.utcnow() - news_date) < timedelta(days=14)
    except:
        return False

def is_relevant_to_symbol(title: str, symbol: str, company_names: list = None) -> bool:
    """
    Very lenient title check - only exclude obvious generic patterns
    """
    title_lower = title.lower()
    
    # Check if company/symbol is in title
    symbol_in_title = symbol.lower() in title_lower
    company_in_title = company_names and any(comp.lower() in title_lower for comp in company_names)
    
    # Only exclude very specific generic patterns
    generic_patterns = ["10 things that will decide", "market action on monday", "market action on tuesday", "market action on wednesday"]
    is_generic = any(pattern in title_lower for pattern in generic_patterns)
    
    # Accept almost anything that mentions the company/symbol
    return (symbol_in_title or company_in_title) and not is_generic

def analyze_sentiment(text: str) -> str:
    """Return sentiment: positive, negative, or neutral."""
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.05:
        return "positive"
    elif compound <= -0.05:
        return "negative"
    else:
        return "neutral"
    
class StockNews(Base):
    __tablename__ = "stock_news"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True)
    timestamp = Column(DateTime)
    title = Column(Text)
    sentiment = Column(String(10))

# Create table if not exists
Base.metadata.create_all(bind=engine)


@app.post("/news-sentiment",
          summary="Get news for stock symbol",
          response_description="List of 3 recent news articles")
async def get_news_sentiment(stock_symbol: StockSymbol):
    try:
        symbol = stock_symbol.symbol.upper()
        company_names = COMPANY_MAPPING.get(symbol, [])
        current_time = datetime.utcnow()
        ten_minutes_ago = current_time - timedelta(minutes=10)

        db = SessionLocal()

        # Step 1: Check DB cache
        recent_entries = db.query(StockNews).filter(
            and_(
                StockNews.symbol == symbol,
                StockNews.timestamp >= ten_minutes_ago
            )
        ).all()

        headlines = []
        sentiment_scores = []

        if recent_entries:
            for entry in recent_entries:
                sentiment_label = entry.sentiment
                sentiment_scores.append(
                    1 if sentiment_label == "positive" else -1 if sentiment_label == "negative" else 0
                )
                headlines.append({
                    "title": entry.title,
                    "sentiment": sentiment_label
                })

            overall_score = sum(sentiment_scores) / len(sentiment_scores)
            overall_sentiment = (
                "positive" if overall_score > 0.05 else
                "negative" if overall_score < -0.05 else
                "neutral"
            )

            return {
                "symbol": symbol,
                "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "headlines": headlines,
                "overall_sentiment": overall_sentiment,
                "message": "Served from cached DB results"
            }

        # Step 2: Clear stale entries
        db.query(StockNews).filter(StockNews.symbol == symbol).delete()
        db.commit()

        # Step 3: Fetch from NewsAPI
        if company_names:
            company_query = " OR ".join([f'"{name}"' for name in company_names])
            query = f'({company_query} OR "{symbol}")'
        else:
            query = f'"{symbol}"'

        params = {
            "q": query,
            "pageSize": 100,
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": NEWSAPI_KEY
        }

        response = requests.get(NEWSAPI_URL, params=params)
        response.raise_for_status()
        news_data = response.json()

        titles_seen = set()

        if 'articles' in news_data:
            for article in news_data['articles']:
                if len(headlines) >= 3:
                    break

                if is_recent_news(article.get("publishedAt", "")):
                    title = article.get("title", "").strip()
                    if title in titles_seen:
                        continue

                    if is_relevant_to_symbol(title, symbol, company_names):
                        sentiment = analyze_sentiment(title)
                        score = 1 if sentiment == "positive" else -1 if sentiment == "negative" else 0

                        headlines.append({
                            "title": title,
                            "sentiment": sentiment
                        })
                        sentiment_scores.append(score)
                        titles_seen.add(title)

        if not headlines:
            return {
                "symbol": symbol,
                "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "headlines": [],
                "overall_sentiment": "neutral",
                "message": f"No recent relevant news found for {symbol}"
            }

        # Store in DB
        for item in headlines:
            news_entry = StockNews(
                symbol=symbol,
                timestamp=current_time,
                title=item["title"],
                sentiment=item["sentiment"]
            )
            db.add(news_entry)
        db.commit()

        # Calculate overall sentiment
        overall_score = sum(sentiment_scores) / len(sentiment_scores)
        overall_sentiment = (
            "positive" if overall_score > 0.05 else
            "negative" if overall_score < -0.05 else
            "neutral"
        )

        return {
            "symbol": symbol,
            "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "headlines": headlines,
            "overall_sentiment": overall_sentiment
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=429 if "rate limited" in str(e).lower() else 500,
            detail=f"NewsAPI error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)