from flask import Flask, request, jsonify
from flasgger import Swagger
import datetime

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/pricing/calc', methods=['POST'])
def calculate_price():
    """Calcular preço
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            space_id:
              type: integer
            start_time:
              type: string
            end_time:
              type: string
            user_plan:
              type: string
    """
    data = request.json
    
    # Preço base por hora
    base_price = 25.0
    
    # Calcular horas
    start = datetime.datetime.fromisoformat(data['start_time'])
    end = datetime.datetime.fromisoformat(data['end_time'])
    hours = (end - start).total_seconds() / 3600
    
    # Aplicar descontos por plano
    discounts = {
        'basic': 0.0,
        'premium': 0.1,
        'enterprise': 0.2
    }
    
    discount = discounts.get(data.get('user_plan', 'basic'), 0.0)
    total = base_price * hours * (1 - discount)
    
    return jsonify({
        'base_price': base_price,
        'hours': hours,
        'discount': discount,
        'total': round(total, 2)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)