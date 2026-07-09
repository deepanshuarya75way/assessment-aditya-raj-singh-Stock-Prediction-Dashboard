import yfinance as yf


def get_stock_data(symbol):
    stock = yf.Ticker(symbol)

    # Get last 2 days of data
    history = stock.history(period="2d")

    latest = history.iloc[-1]
    previous = history.iloc[-2]

    return {
        "name": stock.info.get("longName", symbol),
        "symbol": symbol,
        "price": round(float(latest["Close"]), 2),
        "high": round(float(latest["High"]), 2),
        "low": round(float(latest["Low"]), 2),
        "volume": int(latest["Volume"]),
        "previous_close": round(float(previous["Close"]), 2)
    }


def get_historical_data(symbol, period="6mo"):
    stock = yf.Ticker(symbol)

    history = stock.history(period=period)

    dates = history.index.strftime("%Y-%m-%d").tolist()
    prices = history["Close"].round(2).tolist()

    return dates, prices