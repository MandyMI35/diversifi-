## Features

- Fetches the 3 most recent and relevant news articles for a given Indian stock symbol
- Performs sentiment analysis using VADER from NLTK
- Caches results in PostgreSQL for 10 minutes to avoid repeated API calls
- Uses NewsAPI for fetching latest news articles

## Setup Instructions

## 1. Clone the Repository
- bashgit 
- clone <your-repo-url>
- cd draft1

## 2. Configure Environment
- Edit the .env file and add your NewsAPI key:
- notepad .env  # Windows
- Add NewsAPI key:
- envNEWSAPI_KEY=your_newsapi_key_here

## 3. Get NewsAPI Key 

- Go to https://newsapi.org/
- Sign up for free account
- Copy your API key from dashboard
- Paste it in the .env file

## 4. Run the Application
- bash# 
- Build and start all services
- docker-compose up --build

# Or run in background
- docker-compose up -d --build

The API will be available at:
- **Base URL**: http://127.0.0.1:8000
- **Interactive docs**: http://127.0.0.1:8000/docs

Note - The postgres service in the docker-compose.yml pulls and runs PostgreSQL in a container.
It automatically creates the database, user, and handles all configuration.

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
