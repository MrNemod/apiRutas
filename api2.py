from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import jwt
import datetime
import os

DB_URI = os.environ.get('DB_URI')  # Cambia esto para obtener la variable de entorno

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

SECRET_KEY = 'secret_key'
db = SQLAlchemy(app)


@app.route('/generate_jwt', methods=['GET'])
def generate_jwt():
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    return jsonify({'jwt': token})


@app.route('/get_view_full_route_stop_event_info', methods=['GET'])
def get_view_full_route_stop_event_info():
    # Verificar si el JWT está presente en los encabezados de la solicitud
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token no proporcionado'}), 401

    try:
        # Decodificar el JWT
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token ha expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token inválido'}), 401

    # Ejecutar la consulta SQL directamente
    sql_query = text('SELECT * FROM view_full_route_stop_event_info')

    result = db.session.execute(sql_query)
    routes = {}

    for row in result:
        route_id = row.route_id

        # Si la ruta aún no está en el diccionario, la añadimos
        if route_id not in routes:
            routes[route_id] = {
                'ruta': {
                    'id': route_id,
                    'nombre': row.route_name,
                    'primera_hora_corrida': row.first_departure_time.strftime("%H:%M:%S") if row.first_departure_time else None,
                    'ultima_hora_corrida': row.last_departure_time.strftime("%H:%M:%S") if row.last_departure_time else None,
                    'tipo_vehiculo': row.vehicle_type,
                    'frecuencia_paso': row.passing_frequency,
                    'color': row.route_color
                },
                'estaciones': []
            }

        # Crear la información de la estación y evento
        estacion = {
            'id': row.stop_id,
            'nombre': row.stop_name,
            'coordenadas': row.location_coordinates,
            'distrito': row.district,
            'evento': {
                'id_evento': row.event_id,
                'fecha': row.event_date.strftime("%Y-%m-%d") if row.event_date else None,
                'nombre_evento': row.event_name,
                'hora_inicio': row.event_start_time.strftime("%H:%M:%S") if row.event_start_time else None,
                'hora_fin': row.event_end_time.strftime("%H:%M:%S") if row.event_end_time else None,
                'estado': row.event_status
            } if row.event_id else None
        }

        # Añadir la estación a la ruta correspondiente
        routes[route_id]['estaciones'].append(estacion)

    # Devolver los datos en formato JSON
    return jsonify(list(routes.values()))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
