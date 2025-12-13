from flask import Flask, request, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

spaces_db = {}

@app.route('/spaces', methods=['GET'])
def get_spaces():
    return jsonify(list(spaces_db.values()))

@app.route('/spaces', methods=['POST'])
def create_space():
    data = request.json
    space_id = len(spaces_db) + 1
    space = {
        'id': space_id,
        'name': data['name'],
        'description': data.get('description', ''),
        'capacity': data['capacity'],
        'price_per_hour': data['price_per_hour'],
        'photo_url': data.get('photo_url', '')
    }
    spaces_db[space_id] = space
    return jsonify({'id': space_id}), 201

@app.route('/spaces/<int:space_id>', methods=['GET'])
def get_space(space_id):
    space = spaces_db.get(space_id)
    if not space:
        return jsonify({'error': 'Space not found'}), 404
    return jsonify(space)

@app.route('/spaces/<int:space_id>', methods=['PUT'])
def update_space(space_id):
    space = spaces_db.get(space_id)
    if not space:
        return jsonify({'error': 'Space not found'}), 404
    
    data = request.json
    space.update({
        'name': data.get('name', space['name']),
        'description': data.get('description', space['description']),
        'capacity': data.get('capacity', space['capacity']),
        'price_per_hour': data.get('price_per_hour', space['price_per_hour'])
    })
    return jsonify(space)

@app.route('/spaces/<int:space_id>', methods=['DELETE'])
def delete_space(space_id):
    if space_id in spaces_db:
        del spaces_db[space_id]
        return jsonify({'message': 'Space deleted'})
    return jsonify({'error': 'Space not found'}), 404

@app.route('/spaces/<int:space_id>/availability', methods=['GET'])
def check_availability(space_id):
    return jsonify({'available': True, 'slots': ['09:00', '10:00', '14:00']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)