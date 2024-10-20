from flask import Flask, jsonify, request
import psycopg2
import redis
import hashlib
import jwt
import requests
import time
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
API_GATEWAY_URL = "http://api-gateway:3000"

# Retry logic to connect to PostgreSQL
while True:
    try:
        conn = psycopg2.connect(
            database="users_db",
            user="postgres",
            password="1234",
            host="postgres",  # Service name in Docker
            port="5432"
        )
        print("Connected to PostgreSQL successfully!")
        break  # Exit loop when connection is successful
    except psycopg2.OperationalError as e:
        print("PostgreSQL is not ready. Retrying in 5 seconds...")
        time.sleep(5)  # Wait for 5 seconds before retrying

cursor = conn.cursor()

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Helper function to verify JWT token using Redis
def verify_token(token):
    try:
        # Decode the token
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        token_key = f"jwt_{decoded['email']}"
        # Check if token exists in Redis
        stored_token = redis_client.get(token_key)
        if stored_token and stored_token.decode('utf-8') == token:
            return decoded
        else:
            return None
    except jwt.InvalidTokenError:
        return None

#Route for user registration
@app.route('/api/users/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        hashed_password = hash_password(data['password'])
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (data['name'], data['email'], hashed_password))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return jsonify({"error": str(e)}), 500

# @app.route('/api/users/register', methods=['POST'])
# def register_user():
#     try:
#         data = request.json
#         print(f"Received data: {data}")  # Add this for debugging
#         hashed_password = hash_password(data['password'])
#         cursor.execute(
#             "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
#             (data['name'], data['email'], hashed_password)
#         )
#         conn.commit()
#         return jsonify({"message": "User registered successfully"}), 201
#     except Exception as e:
#         conn.rollback()  # Rollback in case of error
#         print(f"Error: {e}")  # Add this to see the exact error
#         return jsonify({"error": str(e)}), 500


# Route for user login
@app.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.json
    hashed_password = hash_password(data['password'])
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (data['email'], hashed_password))
    user = cursor.fetchone()
    if user:
        # Generate JWT token
        token = jwt.encode({"email": data['email']}, app.config['SECRET_KEY'], algorithm="HS256")
        # Store token in Redis with an expiration time (e.g., 1 hour)
        token_key = f"jwt_{data['email']}"
        redis_client.setex(token_key, 3600, token)
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Invalid email or password"}), 401

# Route for retrieving user profile
@app.route('/api/users/profile', methods=['GET'])
def get_user_profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token missing"}), 401

    # Verify token using Redis
    decoded = verify_token(token)
    if decoded:
        cursor.execute("SELECT name, email FROM users WHERE email = %s", (decoded['email'],))
        user = cursor.fetchone()
        return jsonify({"name": user[0], "email": user[1]})
    else:
        return jsonify({"error": "Invalid or expired token"}), 401

# Route for updating user profile
@app.route('/api/users/profile/update', methods=['POST'])
def update_user_profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token missing"}), 401

    data = request.json
    # Verify token using Redis
    decoded = verify_token(token)
    if decoded:
        try:
            cursor.execute("UPDATE users SET name = %s WHERE email = %s", (data['name'], decoded['email']))
            conn.commit()
            return jsonify({"message": "Profile updated successfully"})
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid or expired token"}), 401

# Status endpoint for User Management Service
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"message": "User Management Service is running!"})

# Endpoint for Buy Action
@app.route('/api/users/buy', methods=['POST'])
def buy_stock():
    data = request.json
    transaction_data = {
        "user_id": data["user_id"],
        "operation": "buy",
        "quantity": data["quantity"],
        "currency": data["currency"]
    }
    response = requests.post(f"{API_GATEWAY_URL}/api/transactions/store", json=transaction_data)
    return jsonify(response.json()), response.status_code

# Endpoint for Sell Action
@app.route('/api/users/sell', methods=['POST'])
def sell_stock():
    data = request.json
    transaction_data = {
        "user_id": data["user_id"],
        "operation": "sell",
        "quantity": data["quantity"],
        "currency": data["currency"]
    }
    response = requests.post(f"{API_GATEWAY_URL}/api/transactions/store", json=transaction_data)
    return jsonify(response.json()), response.status_code

@app.route('/test_redis', methods=['GET'])
def test_redis():
    try:
        redis_client.set('test_key', 'test_value')
        value = redis_client.get('test_key').decode('utf-8')
        return jsonify({"message": f"Successfully set and got value from Redis: {value}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)


