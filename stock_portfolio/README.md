# Stock Portfolio Dashboard

A real-time stock portfolio dashboard that displays your investment portfolio with live price updates and performance metrics.

## Features

- Real-time stock price updates
- Portfolio performance tracking
- Individual stock performance metrics
- Clean and responsive web interface
- Automatic data refresh every 5 minutes

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd stock_portfolio
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your configuration:

```env
REDIS_URL=redis://localhost:6379/0
FLASK_ENV=development
FLASK_DEBUG=1
```

## Configuration

The application uses a Redis database to store portfolio data. Make sure Redis is installed and running on your system.

### Portfolio Configuration

Create a `portfolio.json` file in the `data` directory with your portfolio information:

```json
{
    "stocks": [
        {
            "symbol": "AAPL",
            "shares": 10,
            "purchase_price": 150.0
        },
        {
            "symbol": "GOOGL",
            "shares": 5,
            "purchase_price": 2500.0
        }
    ]
}
```

## Running the Application

1. Start Redis server:

```bash
redis-server
```

2. Run the Flask application:

```bash
python src/app.py
```

3. Open your web browser and navigate to `http://localhost:5000`

## Project Structure

```

stock_portfolio/
├── src/
│   ├── app.py              # Main Flask application
│   ├── portfolio.py        # Portfolio management
│   ├── stock_data.py       # Stock data fetching
│   └── templates/
│       └── index.html      # Dashboard template
├── data/
│   └── portfolio.json      # Portfolio configuration
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Dependencies

- Flask: Web framework
- Redis: Data storage and caching
- yfinance: Yahoo Finance API client
- APScheduler: Task scheduling
- python-dotenv: Environment variable management

## License

MIT License 