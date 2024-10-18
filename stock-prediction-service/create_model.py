from sklearn.linear_model import LinearRegression
import joblib

# Create and fit a simple model
model = LinearRegression()
X_train = [[0], [1], [2]]
y_train = [0, 1, 2]
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, 'stock_model2.pkl')
print("Model saved successfully!")
