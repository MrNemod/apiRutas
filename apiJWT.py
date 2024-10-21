from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
import os

DB_URI = os.getenv('DB_URI')


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

SECRET_KEY = 'secret_key'
db = SQLAlchemy(app)


class RouteStopEventInfo(db.Model):
    __tablename__ = 'view_full_route_stop_event_info'
    __table_args__ = {'extend_existing': True}

    route_id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String)
    first_departure_time = db.Column(db.Time)
    last_departure_time = db.Column(db.Time)
    vehicle_type = db.Column(db.String)
    passing_frequency = db.Column(db.String)
    route_color = db.Column(db.String)
    stop_id = db.Column(db.Integer)
    stop_name = db.Column(db.String)
    location_coordinates = db.Column(db.String)
    district = db.Column(db.String)
    event_id = db.Column(db.Integer)
    event_name = db.Column(db.String)
    event_date = db.Column(db.Date)
    event_start_time = db.Column(db.Time)
    event_end_time = db.Column(db.Time)
    event_status = db.Column(db.String)
    follow_up = db.Column(db.String)


@app.route('/generate_jwt', methods=['GET'])
def generate_jwt():
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    return jsonify({'jwt': token})


@app.route('/get_view_full_route_stop_event_info', methods=['GET'])
def get_view_full_route_stop_event_info():
    result = RouteStopEventInfo.query.all()

    all_info = []

    for row in result:
        all_info.append({
            'route_id': row.route_id,
            'route_name': row.route_name,
            'first_departure_time': row.first_departure_time,
            'last_departure_time': row.last_departure_time,
            'vehicle_type': row.vehicle_type,
            'passing_frequency': row.passing_frequency,
            'route_color': row.route_color,
            'stop_id': row.stop_id,
            'stop_name': row.stop_name,
            'location_coordinates': row.location_coordinates,
            'district': row.district,
            'event_id': row.event_id,
            'event_name': row.event_name,
            'event_date': row.event_date,
            'event_start_time': row.event_start_time,
            'event_end_time': row.event_end_time,
            'event_status': row.event_status,
            'follow_up': row.follow_up
        })

    return jsonify(all_info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
