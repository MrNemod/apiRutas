from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import jwt
import datetime
import os

DB_URI = os.environ.get('DB_URI')

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
    # Ejecutar la consulta SQL directamente para obtener todos los registros, incluidos los duplicados
    sql_query = text("""
        SELECT 
            ir.id_rote AS route_id,
            ir.name_rote AS route_name,
            ir.first_departure_time,
            ir.last_departure_time,
            ir.type_vehicle AS vehicle_type,
            NULL::text AS passing_frequency,
            ir.color_rote AS route_color,
            is1.id_stops AS stop_id,
            is1.name_stop AS stop_name,
            is1.location_coordinates,
            is1.district,
            e.id_event AS event_id,
            e.name_event AS event_name,
            e.date_event AS event_date,
            e.start_event_time AS event_start_time,
            e.end_event_time AS event_end_time,
            e.status AS event_status,
            trs.follow_up
        FROM 
            ((((information_routes ir
            JOIN table_route_stop trs ON ((ir.id_rote = trs.fk_id_name_route)))
            JOIN information_stop is1 ON ((trs.fk_id_name_stops = is1.id_stops)))
            LEFT JOIN affected_stop afs ON ((is1.id_stops = afs.fk_id_stop)))
            LEFT JOIN incident_report e ON ((afs.fk_idevent = e.id_event)))
        ORDER BY 
            ir.id_rote, trs.follow_up
    """)

    result = db.session.execute(sql_query)
    all_info = []

    for row in result:
        all_info.append({
            'route_id': row.route_id,
            'route_name': row.route_name,
            'first_departure_time': row.first_departure_time.strftime("%H:%M:%S") if row.first_departure_time else None,
            'last_departure_time': row.last_departure_time.strftime("%H:%M:%S") if row.last_departure_time else None,
            'vehicle_type': row.vehicle_type,
            'passing_frequency': row.passing_frequency,
            'route_color': row.route_color,
            'stop_id': row.stop_id,
            'stop_name': row.stop_name,
            'location_coordinates': row.location_coordinates,
            'district': row.district,
            'event_id': row.event_id,
            'event_name': row.event_name,
            'event_date': row.event_date.strftime("%Y-%m-%d") if row.event_date else None,
            'event_start_time': row.event_start_time.strftime("%H:%M:%S") if row.event_start_time else None,
            'event_end_time': row.event_end_time.strftime("%H:%M:%S") if row.event_end_time else None,
            'event_status': row.event_status,
            'follow_up': row.follow_up
        })

    return jsonify(all_info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
