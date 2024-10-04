from flask import Flask, jsonify, request
import psycopg2
import redis
import hashlib
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  


conn = psycopg2.connect(
    database="users_db",
    user="postgres",
    password="1234",  
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Route for user registration
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

# Route for user login
@app.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.json
    hashed_password = hash_password(data['password'])
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (data['email'], hashed_password))
    user = cursor.fetchone()
    if user:
        token = jwt.encode({"email": data['email']}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Invalid email or password"}), 401

# Route for retrieving user profile
@app.route('/api/users/profile', methods=['GET'])
def get_user_profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token missing"}), 401

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        cursor.execute("SELECT name, email FROM users WHERE email = %s", (data['email'],))
        user = cursor.fetchone()
        return jsonify({"name": user[0], "email": user[1]})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

# Route for updating user profile
@app.route('/api/users/profile/update', methods=['POST'])
def update_user_profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token missing"}), 401

    data = request.json
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        cursor.execute("UPDATE users SET name = %s WHERE email = %s", (data['name'], decoded['email']))
        conn.commit()
        return jsonify({"message": "Profile updated successfully"})
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

# Status endpoint for User Management Service
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"message": "User Management Service is running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
