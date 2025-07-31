## Features

- Fetches the 3 most recent and relevant news articles for a given Indian stock symbol
- Performs sentiment analysis using VADER from NLTK
- Caches results in PostgreSQL for 10 minutes to avoid repeated API calls
- Uses NewsAPI for fetching latest news articles

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd draft1
```

### 2. Set up the virtual environment

```
python -m venv venv
source venv\Scripts\activate    
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Environment variables

Create a `.env` file in the root directory and add NewsAPI key:

```
NEWSAPI_KEY=your_newsapi_key_here
```

### 5. Set up PostgreSQL

Ensure you have PostgreSQL running. Update the connection string in `main.py` if needed:

```
DATABASE_URL = "postgresql://postgres:postgres@host.docker.internal:5432/stock_news"
```

You can use Docker to spin up PostgreSQL locally or connect to an existing database.

### 6. Run the app

```
uvicorn main:app --reload
```

The API will be available at:
- **Base URL**: http://127.0.0.1:8000
- **Interactive docs**: http://127.0.0.1:8000/docs

## API Endpoint

### POST /news-sentiment

**Request Body:**
```json
{
  "symbol": "HDFC"
}
```

**Response:**
```json
{
  "symbol": "HDFC",
  "timestamp": "2025-07-31T15:44:10Z",
  "headlines": [
    {
      "title": "Indian ADRs Log Deep Cuts: Infosys, Wipro, HDFC Bank, Other ADR Shares Drop After Trump's 25% Tariff On India",
      "sentiment": "negative"
    },
    {
      "title": "Indian ATM Cash Withdrawal limitations 2025 : Find out the cash limitations for SBI, HDFC, PNB, ICICI, and other top banks",
      "sentiment": "positive"
    },
    {
      "title": "'Buy' L&T, GAIL, 'Add' Asian Paints, KEC, 'Reduce' Heidelberg Cement Says HDFC Securities Post Q1 Results",
      "sentiment": "positive"
    }
  ],
  "overall_sentiment": "positive"
}
```

## Tools & Technologies Used

- **FastAPI** – Web framework
- **NewsAPI** – Source of news articles
- **NLTK (VADER)** – Sentiment analysis
- **SQLAlchemy** – ORM for database
- **PostgreSQL** – Database
- **Docker** – For containerization 
- **Pydantic** – For request validation

**Use of AI tools**-
Used AI tools like chatGPT and claude to set up Docker configuration files and decide between OpenAI and other LLM APIs based on integration ease and performance. AI also helped compare TextBlob vs. VADER for sentiment analysis and guided the choice between NewsCatcher and Bing News via RapidAPI for news sourcing. Additionally, AI was used to debugging and troubleshooting errors during development.