# Stock Market Dashboard 📈

A comprehensive real-time stock market dashboard that provides live stock data, market analysis, and AI-powered predictions for both Indian and international markets.

![Stock Dashboard Screenshot](https://github.com/AnkithBangre/stock-dashboard/blob/main/Screenshot%202025-08-15%20120920.png)

## ✨ Features

- **Real-time Stock Data**: Live price updates for Indian (NSE/BSE) and US markets
- **Interactive Dashboard**: Clean, modern interface with dark theme
- **AI Price Predictions**: Machine learning-based next-day price forecasting
- **Market Overview**: Real-time market indices and status
- **Advanced Search**: Smart stock search with auto-complete
- **Technical Analysis**: RSI, SMA, volume analysis, and key metrics
- **Trending Stocks**: Most active stocks across markets
- **Quick Access**: Pre-configured popular stocks sidebar
- **Responsive Design**: Works seamlessly across devices

## 🚀 Live Demo

Running on http://127.0.0.1:5000

## 🛠️ Tech Stack

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript (ES6+)**: Interactive functionality
- **Chart.js**: Beautiful stock charts and visualizations
- **Socket.IO**: Real-time data streaming

### Backend
- **Python Flask**: RESTful API server
- **yfinance**: Yahoo Finance API integration
- **pandas**: Data manipulation and analysis
- **scikit-learn**: Machine learning for predictions
- **NumPy**: Numerical computations
- **Flask-CORS**: Cross-origin resource sharing

### Database
- **Vercel PostgreSQL**: Cloud database for real-time access
- **Real-time caching**: Optimized data retrieval

### Deployment
- **Vercel**: Full-stack deployment platform
- **Environment Variables**: Secure API key management

## 📋 Prerequisites

- Python 3.8+
- Vercel CLI (for deployment)

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/AnkithBangre/stock-dashboard.git
cd stock-dashboard
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application Locally
```bash
# Start the Flask development server
python app.py

# The app will be available at http://localhost:5000
```

### 4. Using Docker (Alternative)
```bash
# Build the Docker image
docker build -t stock-dashboard .

# Run the container
docker run -p 5000:5000 stock-dashboard

# The app will be available at http://localhost:5000
```

### 5. Requirements File (requirements.txt)
```txt
Flask==2.3.3
yfinance==0.2.18
numpy==1.24.3
scikit-learn==1.3.0
```

## 📊 API Endpoints

### Stock Data
- `GET /api/stock/{symbol}` - Get comprehensive stock data
- `GET /api/real-time/{symbol}` - Get real-time price updates
- `GET /api/search/{query}` - Search stocks by symbol/name

### Market Data
- `GET /api/market-summary` - Get market indices overview
- `GET /api/market-status` - Get current market status
- `GET /api/trending` - Get trending stocks

### User Features
- `GET /api/companies` - Get available companies list
- `GET/POST/DELETE /api/watchlist` - Manage user watchlist

## 📱 Supported Markets

### Indian Markets
- **NSE (National Stock Exchange)**: RELIANCE.NS, TCS.NS, INFY.NS
- **BSE (Bombay Stock Exchange)**: Major Indian stocks
- **Market Hours**: 9:15 AM - 3:30 PM IST

### International Markets
- **US Markets**: AAPL, GOOGL, MSFT, TSLA, NVDA
- **Market Hours**: 9:30 AM - 4:00 PM EST
- **Extended Hours**: Pre/post market data available

## 🔍 Key Features Explained

### AI Price Prediction
- Uses Linear Regression on 30-day price history
- Provides confidence score based on R-squared value
- Indicates bullish/bearish trend direction

### Real-time Updates
- 30-second auto-refresh for market data
- Live price streaming via WebSocket
- Smart caching to minimize API calls

### Search Functionality
- Real-time search with 300ms debouncing
- Searches both symbol and company name
- Keyboard shortcuts (Ctrl+K to focus)

### Technical Indicators
- **RSI**: 14-day Relative Strength Index
- **SMA**: 20-day and 50-day Simple Moving Averages
- **Volume Analysis**: Average 30-day volume
- **52-week High/Low**: Annual price range

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Test API endpoints
python -m pytest tests/api/
```

## 📊 Performance Optimization

- **Caching Strategy**: PostgreSQL-based intelligent caching
- **API Rate Limiting**: Prevents Yahoo Finance API abuse
- **Lazy Loading**: Components load on demand
- **Data Compression**: Minified responses
- **CDN Integration**: Static assets via Vercel Edge Network

## 🔒 Security Features

- **CORS Configuration**: Secure cross-origin requests
- **Input Validation**: SQL injection prevention
- **Rate Limiting**: API abuse protection
- **Environment Variables**: Secure credential management

## 🐛 Known Issues & Limitations

- Yahoo Finance API has rate limits (200 requests/hour)
- Real-time data may have 15-20 minute delays for free tier
- Some international stocks may have limited data
- Market status detection is timezone-dependent
