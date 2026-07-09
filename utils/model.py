import math
import pandas as pd
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def predict_next_price(symbol):
    # Fetch 1 year of daily historical data
    data = yf.download(symbol, period="1y", progress=False, auto_adjust=False)

    if data.empty:
        raise ValueError(f"No historical data found for {symbol}")

    # Handle MultiIndex columns (sometimes returned by yfinance)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    features = ["Open", "High", "Low", "Close", "Volume"]
    data = data[features].copy()

    # The features for the next day's prediction (tomorrow) are the very last row in the dataset
    latest_features = data[features].iloc[-1:]

    # For training, shift the target Close price back by 1 day (align Close at t+1 with features at t)
    data["Prediction"] = data["Close"].shift(-1)
    train_data = data.dropna().copy()

    X = train_data[features]
    y = train_data["Prediction"]

    # If we have very little data, fallback to naive prediction
    if len(train_data) < 10:
        latest_close = float(data["Close"].iloc[-1])
        naive_result = {
            "predicted_price": round(latest_close, 2),
            "mae": 0.0,
            "rmse": 0.0,
            "r2": 0.0
        }
        return {
            "linear_regression": naive_result,
            "random_forest": naive_result
        }

    # Chronological Split (Temporal data: avoid future leakage)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # Model 1: Linear Regression
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    lr_test_preds = lr_model.predict(X_test)
    lr_mae = mean_absolute_error(y_test, lr_test_preds)
    lr_rmse = math.sqrt(mean_squared_error(y_test, lr_test_preds))
    lr_r2 = r2_score(y_test, lr_test_preds)
    lr_pred_price = lr_model.predict(latest_features)[0]

    # Model 2: Random Forest Regressor
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_test_preds = rf_model.predict(X_test)
    rf_mae = mean_absolute_error(y_test, rf_test_preds)
    rf_rmse = math.sqrt(mean_squared_error(y_test, rf_test_preds))
    rf_r2 = r2_score(y_test, rf_test_preds)
    rf_pred_price = rf_model.predict(latest_features)[0]

    return {
        "linear_regression": {
            "predicted_price": round(float(lr_pred_price), 2),
            "mae": round(float(lr_mae), 2),
            "rmse": round(float(lr_rmse), 2),
            "r2": round(float(lr_r2), 3),
        },
        "random_forest": {
            "predicted_price": round(float(rf_pred_price), 2),
            "mae": round(float(rf_mae), 2),
            "rmse": round(float(rf_rmse), 2),
            "r2": round(float(rf_r2), 3),
        }
    }
