from flask import Flask, jsonify
import jwt
import datetime

app = Flask(__name__)

SECRET_KEY = 'secret_key'

@app.route('/generate_jwt', methods=['GET'])
def generate_jwt():
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    return jsonify({'jwt': token})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
