from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flasgger import Swagger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
swagger = Swagger(app)

users_db = {}

@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.json
    if data['email'] in users_db:
        return jsonify({'error': 'User already exists'}), 400
    
    user_id = len(users_db) + 1
    users_db[data['email']] = {
        'id': user_id,
        'email': data['email'],
        'password_hash': generate_password_hash(data['password']),
        'name': data['name'],
        'role': data.get('role', 'user')
    }
    return jsonify({'message': 'User created'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    user = users_db.get(data['email'])
    if user and check_password_hash(user['password_hash'], data['password']):
        token = jwt.encode({
            'user_id': user['id'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token, 'role': user['role']})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/users/me', methods=['GET'])
def get_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user = next((u for u in users_db.values() if u['id'] == data['user_id']), None)
        if user:
            return jsonify({'id': user['id'], 'email': user['email'], 'name': user['name'], 'role': user['role']})
        return jsonify({'error': 'User not found'}), 404
    except:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/admin/users', methods=['GET'])
def list_users():
    return jsonify([{'id': u['id'], 'email': u['email'], 'name': u['name'], 'role': u['role']} for u in users_db.values()])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)