from flask import Flask, request, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/notify/email', methods=['POST'])
def send_email():
    """Enviar e-mail
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            to:
              type: string
            subject:
              type: string
            body:
              type: string
    """
    data = request.json
    # Simular envio de e-mail
    print(f"Email sent to {data['to']}: {data['subject']}")
    return jsonify({'message': 'Email sent successfully'})

@app.route('/notify/sms', methods=['POST'])
def send_sms():
    """Enviar SMS
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            phone:
              type: string
            message:
              type: string
    """
    data = request.json
    print(f"SMS sent to {data['phone']}: {data['message']}")
    return jsonify({'message': 'SMS sent successfully'})

@app.route('/notify/push', methods=['POST'])
def send_push():
    """Enviar push notification
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            user_id:
              type: integer
            title:
              type: string
            message:
              type: string
    """
    data = request.json
    print(f"Push sent to user {data['user_id']}: {data['title']}")
    return jsonify({'message': 'Push notification sent'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007)