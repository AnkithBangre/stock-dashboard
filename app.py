from flask import Flask, request, jsonify, send_file
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression


app = Flask(__name__)

# Sample companies - mix of Indian and international stocks
COMPANIES = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "country": "India"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "country": "India"},
    {"symbol": "INFY.NS", "name": "Infosys", "country": "India"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "country": "India"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "country": "India"},
    {"symbol": "AAPL", "name": "Apple Inc.", "country": "USA"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "country": "USA"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "country": "USA"},
    {"symbol": "TSLA", "name": "Tesla, Inc.", "country": "USA"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "country": "USA"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "country": "USA"},
    {"symbol": "META", "name": "Meta Platforms Inc.", "country": "USA"}
]

@app.route("/")
def index():
    return send_file('index.html')

@app.route('/api/companies')
def get_companies():
    """Get list of available companies"""
    return jsonify(COMPANIES)

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get historical stock data for a symbol"""
    try:
        # Get stock info
        stock = yf.Ticker(symbol)
        
        # Get historical data (1 year)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        hist_data = stock.history(start=start_date, end=end_date)
        
        if hist_data.empty:
            return jsonify({"error": "No data found for symbol"}), 404
        
        # Get stock info
        info = stock.info
        
        # Prepare historical data
        historical = []
        for date, row in hist_data.iterrows():
            historical.append({
                "date": date.strftime('%Y-%m-%d'),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
        
        # Calculate additional metrics
        current_price = round(hist_data['Close'].iloc[-1], 2)
        prev_close = round(hist_data['Close'].iloc[-2], 2)
        change = round(current_price - prev_close, 2)
        change_percent = round((change / prev_close) * 100, 2)
        
        # 52-week high/low
        high_52_week = round(hist_data['High'].max(), 2)
        low_52_week = round(hist_data['Low'].min(), 2)
        
        # Average volume (30 days)
        avg_volume = int(hist_data['Volume'].tail(30).mean())
        
        # Simple moving averages
        sma_20 = round(hist_data['Close'].rolling(window=20).mean().iloc[-1], 2)
        sma_50 = round(hist_data['Close'].rolling(window=50).mean().iloc[-1], 2)
        
        # RSI calculation
        def calculate_rsi(prices, window=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        
        rsi = round(calculate_rsi(hist_data['Close']), 2)
        
        # AI Prediction (Simple Linear Regression)
        prediction = get_price_prediction(hist_data['Close'])
        
        response_data = {
            "symbol": symbol,
            "name": info.get('longName', 'N/A'),
            "current_price": current_price,
            "change": change,
            "change_percent": change_percent,
            "high_52_week": high_52_week,
            "low_52_week": low_52_week,
            "avg_volume": avg_volume,
            "market_cap": info.get('marketCap', 'N/A'),
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "sma_20": sma_20,
            "sma_50": sma_50,
            "rsi": rsi,
            "prediction": prediction,
            "historical": historical
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_price_prediction(prices):
    """Simple AI prediction using linear regression"""
    try:
        # Use last 30 days for prediction
        recent_prices = prices.tail(30).values.reshape(-1, 1)
        days = np.arange(len(recent_prices)).reshape(-1, 1)
        
        # Fit linear regression model
        model = LinearRegression()
        model.fit(days, recent_prices)
        
        # Predict next day
        next_day = np.array([[len(recent_prices)]])
        prediction = model.predict(next_day)[0][0]
        
        # Calculate confidence (based on R-squared)
        r_squared = model.score(days, recent_prices)
        confidence = round(r_squared * 100, 1)
        
        return {
            "next_day_price": round(prediction, 2),
            "confidence": confidence,
            "trend": "bullish" if model.coef_[0][0] > 0 else "bearish"
        }
    except:
        return {
            "next_day_price": "N/A",
            "confidence": 0,
            "trend": "neutral"
        }

@app.route('/api/market-summary')
def get_market_summary():
    """Get overall market summary"""
    try:
        # Get major indices
        indices = {
            "^NSEI": "NIFTY 50",
            "^BSESN": "BSE SENSEX",
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones"
        }
        
        summary = []
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                if not hist.empty:
                    current = round(hist['Close'].iloc[-1], 2)
                    previous = round(hist['Close'].iloc[-2], 2)
                    change = round(current - previous, 2)
                    change_percent = round((change / previous) * 100, 2)
                    
                    summary.append({
                        "name": name,
                        "value": current,
                        "change": change,
                        "change_percent": change_percent
                    })
            except:
                continue
        
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/search/<query>')
def search_stocks(query):
    """Search for stocks by symbol or name with real-time price information"""
    try:
        # Extended list of popular stocks for search
        extended_stocks = [
            # US Tech Stocks
            {"symbol": "AAPL", "name": "Apple Inc.", "country": "USA", "sector": "Technology"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "country": "USA", "sector": "Technology"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "country": "USA", "sector": "Technology"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "country": "USA", "sector": "E-commerce"},
            {"symbol": "TSLA", "name": "Tesla, Inc.", "country": "USA", "sector": "Automotive"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "country": "USA", "sector": "Technology"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "country": "USA", "sector": "Technology"},
            {"symbol": "NFLX", "name": "Netflix Inc.", "country": "USA", "sector": "Entertainment"},
            {"symbol": "CRM", "name": "Salesforce Inc.", "country": "USA", "sector": "Technology"},
            {"symbol": "ORCL", "name": "Oracle Corporation", "country": "USA", "sector": "Technology"},
            
            # US Financial & Others
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "country": "USA", "sector": "Financial"},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "country": "USA", "sector": "Healthcare"},
            {"symbol": "V", "name": "Visa Inc.", "country": "USA", "sector": "Financial"},
            {"symbol": "PG", "name": "Procter & Gamble Co.", "country": "USA", "sector": "Consumer Goods"},
            {"symbol": "UNH", "name": "UnitedHealth Group Inc.", "country": "USA", "sector": "Healthcare"},
            {"symbol": "HD", "name": "Home Depot Inc.", "country": "USA", "sector": "Retail"},
            {"symbol": "MA", "name": "Mastercard Inc.", "country": "USA", "sector": "Financial"},
            {"symbol": "BAC", "name": "Bank of America Corp.", "country": "USA", "sector": "Financial"},
            {"symbol": "XOM", "name": "Exxon Mobil Corporation", "country": "USA", "sector": "Energy"},
            {"symbol": "WMT", "name": "Walmart Inc.", "country": "USA", "sector": "Retail"},
            
            # Indian Stocks (NSE)
            {"symbol": "RELIANCE.NS", "name": "Reliance Industries Limited", "country": "India", "sector": "Energy"},
            {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "country": "India", "sector": "Technology"},
            {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Limited", "country": "India", "sector": "Banking"},
            {"symbol": "INFY.NS", "name": "Infosys Limited", "country": "India", "sector": "Technology"},
            {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Limited", "country": "India", "sector": "Banking"},
            {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Limited", "country": "India", "sector": "FMCG"},
            {"symbol": "ITC.NS", "name": "ITC Limited", "country": "India", "sector": "FMCG"},
            {"symbol": "SBIN.NS", "name": "State Bank of India", "country": "India", "sector": "Banking"},
            {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Limited", "country": "India", "sector": "Telecom"},
            {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "country": "India", "sector": "Banking"},
            {"symbol": "LT.NS", "name": "Larsen & Toubro Limited", "country": "India", "sector": "Infrastructure"},
            {"symbol": "ASIANPAINT.NS", "name": "Asian Paints Limited", "country": "India", "sector": "Paints"},
            {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Limited", "country": "India", "sector": "Automotive"},
            {"symbol": "HCLTECH.NS", "name": "HCL Technologies Limited", "country": "India", "sector": "Technology"},
            {"symbol": "WIPRO.NS", "name": "Wipro Limited", "country": "India", "sector": "Technology"},
            
            # Global Stocks
            {"symbol": "BABA", "name": "Alibaba Group Holding", "country": "China", "sector": "E-commerce"},
            {"symbol": "TSM", "name": "Taiwan Semiconductor", "country": "Taiwan", "sector": "Technology"},
            {"symbol": "NESN.SW", "name": "Nestle SA", "country": "Switzerland", "sector": "Food & Beverage"},
            {"symbol": "ASML", "name": "ASML Holding NV", "country": "Netherlands", "sector": "Technology"},
            {"symbol": "SAP", "name": "SAP SE", "country": "Germany", "sector": "Technology"}
        ]
        
        # Combine with existing companies
        all_stocks = COMPANIES + extended_stocks
        
        # Remove duplicates based on symbol
        seen_symbols = set()
        unique_stocks = []
        for stock in all_stocks:
            if stock['symbol'] not in seen_symbols:
                unique_stocks.append(stock)
                seen_symbols.add(stock['symbol'])
        
        # Search logic
        query_lower = query.lower().strip()
        results = []
        
        for stock in unique_stocks:
            symbol_match = query_lower in stock['symbol'].lower()
            name_match = query_lower in stock['name'].lower()
            
            if symbol_match or name_match:
                # Calculate relevance score
                score = 0
                if stock['symbol'].lower().startswith(query_lower):
                    score += 10
                elif symbol_match:
                    score += 5
                if stock['name'].lower().startswith(query_lower):
                    score += 8
                elif name_match:
                    score += 3
                
                try:
                    # Get real-time data for the stock
                    ticker = yf.Ticker(stock['symbol'])
                    hist = ticker.history(period="2d")  # Get 2 days of data for price change calculation
                    
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100
                        
                        # Get additional info
                        info = ticker.info
                        
                        enhanced_stock = {
                            **stock,
                            'current_price': round(current_price, 2),
                            'change': round(change, 2),
                            'change_percent': round(change_percent, 2),
                            'market_cap': info.get('marketCap', 'N/A'),
                            'volume': info.get('volume', 'N/A'),
                            'pe_ratio': info.get('trailingPE', 'N/A'),
                            'day_high': round(float(hist['High'].iloc[-1]), 2) if 'High' in hist else 'N/A',
                            'day_low': round(float(hist['Low'].iloc[-1]), 2) if 'Low' in hist else 'N/A',
                            'relevance_score': score
                        }
                        
                        results.append(enhanced_stock)
                except Exception as e:
                    # If we can't get real-time data, still include the stock with basic info
                    results.append({
                        **stock,
                        'current_price': 'N/A',
                        'change': 'N/A',
                        'change_percent': 'N/A',
                        'market_cap': 'N/A',
                        'volume': 'N/A',
                        'pe_ratio': 'N/A',
                        'day_high': 'N/A',
                        'day_low': 'N/A',
                        'relevance_score': score
                    })
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Remove relevance_score from final results
        for result in results:
            result.pop('relevance_score', None)
        
        return jsonify(results[:20])  # Return top 20 matches
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/real-time/<symbol>')
def get_real_time_data(symbol):
    """Get real-time stock data with minimal delay"""
    try:
        stock = yf.Ticker(symbol)
        
        # Get the most recent data
        hist_data = stock.history(period="1d", interval="1m")  # 1-minute intervals for today
        
        if hist_data.empty:
            return jsonify({"error": "No real-time data available"}), 404
        
        # Get the latest data point
        latest_data = hist_data.iloc[-1]
        
        # Get basic info
        info = stock.info
        
        # Calculate change from previous close
        if len(hist_data) > 1:
            prev_close = hist_data.iloc[-2]['Close']
        else:
            # Fallback to yesterday's close if available
            prev_close = info.get('previousClose', latest_data['Close'])
        
        current_price = float(latest_data['Close'])
        change = current_price - float(prev_close)
        change_percent = (change / float(prev_close)) * 100
        
        # Get market status
        market_time = hist_data.index[-1]
        is_market_open = is_market_currently_open(symbol)
        
        real_time_data = {
            "symbol": symbol,
            "name": info.get('longName', symbol),
            "current_price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": int(latest_data['Volume']),
            "high": round(float(latest_data['High']), 2),
            "low": round(float(latest_data['Low']), 2),
            "open": round(float(latest_data['Open']), 2),
            "market_time": market_time.strftime('%Y-%m-%d %H:%M:%S'),
            "is_market_open": is_market_open,
            "currency": info.get('currency', 'USD'),
            "market_cap": info.get('marketCap', 'N/A'),
            "timezone": str(market_time.tz) if hasattr(market_time, 'tz') else 'UTC'
        }
        
        return jsonify(real_time_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def is_market_currently_open(symbol):
    """Determine if the market is currently open for the given symbol"""
    try:
        from datetime import datetime
        import pytz
        
        now = datetime.now()
        
        # Determine market timezone based on symbol
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            # Indian markets (NSE/BSE)
            market_tz = pytz.timezone('Asia/Kolkata')
            market_start = 9  # 9:15 AM IST
            market_end = 15   # 3:30 PM IST
        else:
            # US markets (default)
            market_tz = pytz.timezone('America/New_York')
            market_start = 9  # 9:30 AM EST
            market_end = 16   # 4:00 PM EST
        
        # Convert current time to market timezone
        market_time = now.astimezone(market_tz)
        current_hour = market_time.hour
        
        # Check if it's a weekday and within market hours
        is_weekday = market_time.weekday() < 5  # 0-4 are Mon-Fri
        is_market_hours = market_start <= current_hour <= market_end
        
        return is_weekday and is_market_hours
        
    except:
        # If we can't determine, assume market could be open
        return True

@app.route('/api/market-status')
def get_market_status():
    """Get current market status for major exchanges"""
    try:
        from datetime import datetime
        import pytz
        
        now = datetime.now(pytz.UTC)
        
        markets = {
            "US": {
                "name": "US Markets (NYSE/NASDAQ)",
                "timezone": "America/New_York",
                "open_time": "09:30",
                "close_time": "16:00"
            },
            "India": {
                "name": "Indian Markets (NSE/BSE)", 
                "timezone": "Asia/Kolkata",
                "open_time": "09:15",
                "close_time": "15:30"
            },
            "UK": {
                "name": "London Stock Exchange",
                "timezone": "Europe/London",
                "open_time": "08:00",
                "close_time": "16:30"
            },
            "Japan": {
                "name": "Tokyo Stock Exchange",
                "timezone": "Asia/Tokyo",
                "open_time": "09:00",
                "close_time": "15:00"
            }
        }
        
        status_data = []
        
        for market_code, market_info in markets.items():
            try:
                tz = pytz.timezone(market_info["timezone"])
                local_time = now.astimezone(tz)
                
                # Parse open/close times
                open_hour, open_min = map(int, market_info["open_time"].split(":"))
                close_hour, close_min = map(int, market_info["close_time"].split(":"))
                
                # Check if market is open
                is_weekday = local_time.weekday() < 5
                current_minutes = local_time.hour * 60 + local_time.minute
                open_minutes = open_hour * 60 + open_min
                close_minutes = close_hour * 60 + close_min
                
                is_open = is_weekday and open_minutes <= current_minutes <= close_minutes
                
                status = "OPEN" if is_open else "CLOSED"
                if not is_weekday:
                    status = "WEEKEND"
                
                status_data.append({
                    "market": market_info["name"],
                    "status": status,
                    "local_time": local_time.strftime("%H:%M"),
                    "timezone": market_info["timezone"],
                    "is_open": is_open
                })
                
            except Exception as e:
                print(f"Error getting status for {market_code}: {e}")
                continue
        
        return jsonify(status_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trending')
def get_trending_stocks():
    """Get trending/most active stocks"""
    try:
        # Popular stocks that are frequently traded
        trending_symbols = [
            "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX",
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"
        ]
        
        trending_data = []
        
        for symbol in trending_symbols[:8]:  # Limit to 8 to avoid too many API calls
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="2d")
                
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                    change = current_price - prev_close
                    change_percent = (change / prev_close) * 100
                    volume = int(hist['Volume'].iloc[-1])
                    
                    info = stock.info
                    
                    trending_data.append({
                        "symbol": symbol,
                        "name": info.get('longName', symbol)[:30] + "..." if len(info.get('longName', symbol)) > 30 else info.get('longName', symbol),
                        "current_price": round(current_price, 2),
                        "change_percent": round(change_percent, 2),
                        "volume": volume,
                        "market_cap": info.get('marketCap', 0)
                    })
                    
            except Exception as e:
                print(f"Error fetching trending data for {symbol}: {e}")
                continue
        
        # Sort by volume (most active first)
        trending_data.sort(key=lambda x: x['volume'], reverse=True)
        
        return jsonify(trending_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
def manage_watchlist():
    """Manage user's watchlist (simplified in-memory version)"""
    # In a real application, this would be stored in database per user
    # For demo purposes, we'll use a simple in-memory store
    
    if not hasattr(manage_watchlist, 'watchlist'):
        manage_watchlist.watchlist = []
    
    if request.method == 'GET':
        # Return watchlist with current prices
        watchlist_data = []
        for symbol in manage_watchlist.watchlist:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1d")
                
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    info = stock.info
                    
                    watchlist_data.append({
                        "symbol": symbol,
                        "name": info.get('longName', symbol),
                        "current_price": round(current_price, 2)
                    })
            except:
                continue
        
        return jsonify(watchlist_data)
    
    elif request.method == 'POST':
        # Add to watchlist
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        
        if symbol and symbol not in manage_watchlist.watchlist:
            manage_watchlist.watchlist.append(symbol)
            return jsonify({"message": f"{symbol} added to watchlist"})
        
        return jsonify({"error": "Invalid symbol or already in watchlist"}), 400
    
    elif request.method == 'DELETE':
        # Remove from watchlist
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        
        if symbol in manage_watchlist.watchlist:
            manage_watchlist.watchlist.remove(symbol)
            return jsonify({"message": f"{symbol} removed from watchlist"})

        return jsonify({"error": "Symbol not in watchlist"}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
