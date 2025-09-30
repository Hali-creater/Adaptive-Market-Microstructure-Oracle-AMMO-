# AMMO Trading Agent

AMMO (AI-Managed Market Operations) is a Streamlit-based application that serves as an AI-powered agent for financial market analysis. It analyzes stock data to provide a trading recommendation based on market personality, sentiment analysis, and risk assessment.

## 🚀 Features

- **Interactive UI**: A user-friendly Streamlit interface to input stock symbols and view analysis.
- **Modular Design**: The agent's logic is broken down into distinct modules:
    - `DataCollector`: Fetches historical market data.
    - `SentimentAnalyzer`: Analyzes market sentiment from news sources.
    - `PersonalityDetector`: Determines the current market personality (e.g., trending, volatile).
    - `RiskManager`: Calculates position sizing based on portfolio value and risk parameters.
- **Configuration-Driven**: Manages API keys and settings through a `.env` file.
- **Simulated Data**: Can run without API keys by generating simulated data, making it easy to test and develop.
- **Custom Styling**: Includes custom CSS for an improved visual experience.

## 📁 File Structure

```
ammo_trading_agent/
│
├── app.py                          # Main Streamlit app
├── ammo_agent.py                   # Core AMMO logic
├── config.py                       # Configuration settings
├── requirements.txt                # Dependencies
├── .env                            # API keys (user-created)
├── README.md                       # Project documentation
├── .gitignore                      # Git ignore file
│
├── .streamlit/
│   └── config.toml                 # Streamlit theme configuration
│
├── modules/
│   ├── data_collector.py           # Market data collection
│   ├── sentiment_analyzer.py       # News and sentiment analysis
│   ├── personality_detector.py     # Market personality detection
│   └── risk_manager.py             # Risk management logic
│
├── utils/
│   ├── helpers.py                  # Helper functions
│   └── constants.py                # Application constants
│
└── assets/
    ├── style.css                   # Custom styling
    └── logo.png                    # App logo (user-provided)
```

## 🛠️ Setup and Installation

Follow these steps to get the AMMO Trading Agent running on your local machine.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ammo_trading_agent
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

The agent uses external APIs to fetch real-time data. You will need to provide your own API keys.

1.  Make a copy of the `.env.example` file (or create a new file) and name it `.env`.
2.  Open the `.env` file and add your API keys.

```env
# --- API Keys and Configuration ---
# Replace with your actual API keys

# Example for a data provider (e.g., Alpha Vantage)
ALPHA_VANTAGE_API_KEY="YOUR_ALPHA_VANTAGE_API_KEY"

# Example for a news provider (e.g., NewsAPI)
NEWS_API_KEY="YOUR_NEWS_API_KEY"

# Example for a trading platform (e.g., Alpaca)
ALPACA_API_KEY="YOUR_ALPACA_API_KEY"
ALPACA_SECRET_KEY="YOUR_ALPACA_SECRET_KEY"
ALPACA_BASE_URL="https://paper-api.alpaca.markets"
```
**Note**: If you don't provide API keys, the application will run in a "simulation mode" with randomly generated data.

## ▶️ How to Run the Application

Once you have completed the setup, you can run the Streamlit application with a single command:

```bash
streamlit run app.py
```

Your web browser should automatically open a new tab with the application running. If not, the command line will provide a local URL (usually `http://localhost:8501`) that you can navigate to.