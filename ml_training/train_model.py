import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

# Load the historical stock data (CSV file from Step 1)
df = pd.read_csv('aapl_historical_data.csv')

# Feature: Stock prices (use price from previous day as a feature)
df['prev_price'] = df['price'].shift(1)
df.dropna(inplace=True)

# Label: Will the stock price go up (1) or down (0)
df['label'] = (df['price'] > df['prev_price']).astype(int)

# Split data into features (X) and labels (y)
X = df[['prev_price']]  # Previous day’s stock price as the feature
y = df['label']         # 1 for 'buy' (price increase), 0 for 'sell' (price drop)

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the machine learning model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the trained model to a file
joblib.dump(model, 'stock_model.pkl')

print("Model trained and saved as stock_model.pkl")
