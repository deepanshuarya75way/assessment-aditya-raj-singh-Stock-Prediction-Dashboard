import yfinance as yf
import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_next_price(symbol):

    data=yf.download(
        symbol,
        period="1y",
        progress=False
    )


    if isinstance(data.columns,pd.MultiIndex):
        data.columns=data.columns.get_level_values(0)


    data=data[['Close']]


    data['Prediction']=data['Close'].shift(-1)


    data.dropna(inplace=True)


    X=data[['Close']]

    y=data['Prediction']


    model=LinearRegression()

    model.fit(X,y)


    today_price=data.iloc[-1]['Close']


    prediction=model.predict(
        [[today_price]]
    )


    return round(float(prediction[0]),2)