from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@db-pagamentos:5432/pagamentos'
db = SQLAlchemy(app)
swagger = Swagger(app)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')
    transaction_id = db.Column(db.String(100))

@app.route('/payments/charge', methods=['POST'])
def charge_payment():
    """Processar pagamento
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            reservation_id:
              type: integer
            amount:
              type: number
            method:
              type: string
              enum: ['pix', 'card']
            card_data:
              type: object
    """
    data = request.json
    payment = Payment(
        reservation_id=data['reservation_id'],
        amount=data['amount'],
        method=data['method'],
        transaction_id=str(uuid.uuid4()),
        status='completed'
    )
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({
        'payment_id': payment.id,
        'transaction_id': payment.transaction_id,
        'status': payment.status
    })

@app.route('/payments/refund', methods=['POST'])
def refund_payment():
    """Estornar pagamento
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            payment_id:
              type: integer
            reason:
              type: string
    """
    data = request.json
    payment = Payment.query.get_or_404(data['payment_id'])
    payment.status = 'refunded'
    db.session.commit()
    
    return jsonify({
        'payment_id': payment.id,
        'status': payment.status,
        'refund_amount': payment.amount
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5004)