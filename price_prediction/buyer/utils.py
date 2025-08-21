def predict_future_price(price, years=10, annual_growth=0.06):
    """
    Predict property price after a number of years using compound growth.
    """
    return round(float(price) * ((1 + annual_growth) ** years), 2)