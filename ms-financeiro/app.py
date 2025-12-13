from flask import Flask, jsonify
from flasgger import Swagger
import random

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/financial/revenue', methods=['GET'])
def get_revenue():
    """Relatório de receita
    ---
    responses:
      200:
        description: Dados de receita
    """
    return jsonify({
        'monthly_revenue': round(random.uniform(10000, 50000), 2),
        'yearly_revenue': round(random.uniform(120000, 600000), 2),
        'growth_rate': round(random.uniform(5, 25), 1)
    })

@app.route('/financial/expenses', methods=['GET'])
def get_expenses():
    """Relatório de despesas
    ---
    responses:
      200:
        description: Dados de despesas
    """
    return jsonify({
        'monthly_expenses': round(random.uniform(5000, 20000), 2),
        'operational_costs': round(random.uniform(3000, 15000), 2),
        'maintenance_costs': round(random.uniform(1000, 5000), 2)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)