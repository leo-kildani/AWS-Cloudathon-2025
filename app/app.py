# app.py
from flask import Flask, request, jsonify
from models import db, Airline, Airport, Flight, init_db
from database import config
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime
import os
from dateutil import parser

app = Flask(__name__)

# Load configuration from config.py
app.config.from_object(config)

# Initialize security extensions
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})
Talisman(app, **app.config['SECURITY_HEADERS'])
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=[app.config['RATE_LIMITS']['default']]
)

# Configure logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Initialize the database with the app
init_db(app)

# --- Schemas for Input Validation ---
class AirlineSchema(Schema):
    airline_id = fields.Str(required=True, validate=validate.Length(min=2, max=3))
    iata_code = fields.Str(required=True, validate=validate.Length(equal=2))
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    country = fields.Str(validate=validate.Length(max=50))

class AirportSchema(Schema):
    airport_id = fields.Str(required=True, validate=validate.Length(min=3, max=3))
    icao_code = fields.Str(required=True, validate=validate.Length(equal=4))
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    city = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    country = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)

class FlightSchema(Schema):
    airline_id = fields.Str(required=True, validate=validate.Length(min=2, max=3))
    flight_number = fields.Str(required=True, validate=validate.Length(min=1, max=10))
    departure_airport = fields.Str(required=True, validate=validate.Length(equal=3))
    arrival_airport = fields.Str(required=True, validate=validate.Length(equal=3))
    scheduled_departure = fields.DateTime(required=True)
    scheduled_arrival = fields.DateTime(required=True)
    actual_departure = fields.DateTime(allow_none=True)
    actual_arrival = fields.DateTime(allow_none=True)
    status = fields.Str(validate=validate.OneOf(['Scheduled', 'On Time', 'Delayed', 'Cancelled', 'Completed']))

# --- Authentication Endpoints ---
@app.route('/login', methods=['POST'])
@limiter.limit(app.config['RATE_LIMITS']['auth'])
def login():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        
        # In production, replace with proper user authentication
        if username != 'admin' or password != 'securepassword':
            return jsonify({"message": "Bad username or password"}), 401
            
        access_token = create_access_token(identity={'username': username, 'role': 'admin'})
        return jsonify(access_token=access_token), 200
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"message": "Login failed"}), 500

# --- Role-Based Access Decorator ---
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        jwt_required()
        current_user = get_jwt_identity()
        if current_user.get('role') != 'admin':
            return jsonify({"message": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

# --- Helper Functions ---
def get_or_404(model, identifier):
    """Gets an object by ID or returns 404."""
    obj = db.session.get(model, identifier)
    if obj is None:
        return jsonify({"message": f"{model.__name__} not found"}), 404
    return obj

def validate_input(schema, data):
    try:
        return schema().load(data)
    except ValidationError as err:
        raise ValueError(err.messages)

# --- Root Endpoint ---
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Flight Tracking MVP API!"})

# --- Airline CRUD Endpoints ---
@app.route('/airlines', methods=['POST'])
@jwt_required()
@admin_required
@limiter.limit(app.config['RATE_LIMITS']['sensitive'])
def create_airline():
    try:
        data = validate_input(AirlineSchema, request.get_json())
        
        if db.session.get(Airline, data['airline_id']):
            return jsonify({"message": "Airline with this ID already exists"}), 409

        new_airline = Airline(**data)
        db.session.add(new_airline)
        db.session.commit()
        return jsonify(new_airline.to_dict()), 201
    except ValueError as e:
        return jsonify({"message": "Validation error", "errors": e.args[0]}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Create airline error: {str(e)}")
        return jsonify({"message": "Failed to create airline"}), 500

@app.route('/airlines', methods=['GET'])
def get_airlines():
    try:
        all_airlines = Airline.query.all()
        return jsonify([airline.to_dict() for airline in all_airlines]), 200
    except Exception as e:
        app.logger.error(f"Get airlines error: {str(e)}")
        return jsonify({"message": "Failed to retrieve airlines"}), 500

@app.route('/airlines/<string:airline_id>', methods=['GET'])
def get_airline(airline_id):
    airline = get_or_404(Airline, airline_id)
    if isinstance(airline, tuple):
        return airline
    return jsonify(airline.to_dict()), 200

@app.route('/airlines/<string:airline_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_airline(airline_id):
    airline = get_or_404(Airline, airline_id)
    if isinstance(airline, tuple):
        return airline

    try:
        data = validate_input(AirlineSchema, request.get_json())
        
        airline.iata_code = data.get('iata_code', airline.iata_code)
        airline.name = data.get('name', airline.name)
        airline.country = data.get('country', airline.country)

        db.session.commit()
        return jsonify(airline.to_dict()), 200
    except ValueError as e:
        return jsonify({"message": "Validation error", "errors": e.args[0]}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Update airline error: {str(e)}")
        return jsonify({"message": "Failed to update airline"}), 500

@app.route('/airlines/<string:airline_id>', methods=['DELETE'])
@jwt_required()
@admin_required
@limiter.limit(app.config['RATE_LIMITS']['sensitive'])
def delete_airline(airline_id):
    airline = get_or_404(Airline, airline_id)
    if isinstance(airline, tuple):
        return airline

    try:
        if Flight.query.filter_by(airline_id=airline_id).first():
            return jsonify({"message": "Cannot delete airline with associated flights"}), 400

        db.session.delete(airline)
        db.session.commit()
        return jsonify({"message": "Airline deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Delete airline error: {str(e)}")
        return jsonify({"message": "Failed to delete airline"}), 500

# --- Airport CRUD Endpoints ---
@app.route('/airports', methods=['POST'])
@jwt_required()
@admin_required
@limiter.limit(app.config['RATE_LIMITS']['sensitive'])
def create_airport():
    try:
        data = validate_input(AirportSchema, request.get_json())
        
        if db.session.get(Airport, data['airport_id']):
            return jsonify({"message": "Airport with this ID already exists"}), 409

        new_airport = Airport(**data)
        db.session.add(new_airport)
        db.session.commit()
        return jsonify(new_airport.to_dict()), 201
    except ValueError as e:
        return jsonify({"message": "Validation error", "errors": e.args[0]}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Create airport error: {str(e)}")
        return jsonify({"message": "Failed to create airport"}), 500

@app.route('/airports', methods=['GET'])
def get_airports():
    try:
        all_airports = Airport.query.all()
        return jsonify([airport.to_dict() for airport in all_airports]), 200
    except Exception as e:
        app.logger.error(f"Get airports error: {str(e)}")
        return jsonify({"message": "Failed to retrieve airports"}), 500

@app.route('/airports/<string:airport_id>', methods=['GET'])
def get_airport(airport_id):
    airport = get_or_404(Airport, airport_id)
    if isinstance(airport, tuple):
        return airport
    return jsonify(airport.to_dict()), 200

@app.route('/airports/<string:airport_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_airport(airport_id):
    airport = get_or_404(Airport, airport_id)
    if isinstance(airport, tuple):
        return airport

    try:
        data = validate_input(AirportSchema, request.get_json())
        
        airport.icao_code = data.get('icao_code', airport.icao_code)
        airport.name = data.get('name', airport.name)
        airport.city = data.get('city', airport.city)
        airport.country = data.get('country', airport.country)
        airport.latitude = data.get('latitude', airport.latitude)
        airport.longitude = data.get('longitude', airport.longitude)

        db.session.commit()
        return jsonify(airport.to_dict()), 200
    except ValueError as e:
        return jsonify({"message": "Validation error", "errors": e.args[0]}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Update airport error: {str(e)}")
        return jsonify({"message": "Failed to update airport"}), 500

@app.route('/airports/<string:airport_id>', methods=['DELETE'])
@jwt_required()
@admin_required
@limiter.limit(app.config['RATE_LIMITS']['sensitive'])
def delete_airport(airport_id):
    airport = get_or_404(Airport, airport_id)
    if isinstance(airport, tuple):
        return airport

    try:
        if Flight.query.filter((Flight.departure_airport == airport_id) | (Flight.arrival_airport == airport_id)).first():
            return jsonify({"message": "Cannot delete airport with associated flights"}), 400

        db.session.delete(airport)
        db.session.commit()
        return jsonify({"message": "Airport deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Delete airport error: {str(e)}")
        return jsonify({"message": "Failed to delete airport"}), 500

# --- Flight CRUD Endpoints ---
@app.route('/flights', methods=['POST'])
@jwt_required()
@admin_required
@limiter.limit(app.config['RATE_LIMITS']['sensitive'])
def create_flight():
    try:
        data = validate_input(FlightSchema, request.get_json())
        
        # Validate foreign keys exist
        if not db.session.get(Airline, data['airline_id']):
            return jsonify({"message": f"Airline {data['airline_id']} not found"}), 400
        if not db.session.get(Airport, data['departure_airport']):
            return jsonify({"message": f"Departure airport {data['departure_airport']} not found"}), 400
        if not db.session.get(Airport, data['arrival_airport']):
            return jsonify({"message": f"Arrival airport {data['arrival_airport']} not found"}), 400

        new_flight = Flight(
            airline_id=data['airline_id'],
            flight_number=data['flight_number'],
            departure_airport=data['departure_airport'],
            arrival_airport=data['arrival_airport'],
            scheduled_departure=data['scheduled_departure'],
            scheduled_arrival=data['scheduled_arrival'],
            actual_departure=data.get('actual_departure'),
            actual_arrival=data.get('actual_arrival'),
            status=data.get('status', 'Scheduled')
        )
        
        db.session.add(new_flight)
        db.session.commit()
        return jsonify(new_flight.to_dict()), 201
    except ValueError as e:
        return jsonify({"message": "Validation error", "errors": e.args[0]}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Create flight error: {str(e)}")
        return jsonify({"message": "Failed to create flight"}), 500

@app.route('/flights', methods=['GET'])
def get_flights():
    status_filter = request.args.get('status')
    airline_filter = request.args.get('airline_id')

    query = Flight.query
    if status_filter:
        query = query.filter(Flight.status == status_filter)
    if airline_filter:
        query = query.filter(Flight.airline_id == airline_filter)

    try:
        all_flights = query.order_by(Flight.scheduled_departure.desc()).all()
        return jsonify([flight.to_dict() for flight in all_flights]), 200
    except Exception as e:
        app.logger.error(f"Get flights error: {str(e)}")
        return jsonify({"message": "Failed to retrieve flights"}), 500

@app.route('/flights/<int:flight_id>', methods=['GET'])
def get_flight(flight_id):
    flight = get_or_404(Flight, flight_id)
    if isinstance(flight, tuple):
        return flight
    return jsonify(flight.to_dict()), 200

@app.route('/flights/<int:flight_id>', methods=['PUT', 'PATCH'])
@jwt_required()
@admin_required
def update_flight(flight_id):
    flight = get_or_404(Flight, flight_id)
    if isinstance(flight, tuple):
        return flight

    try:
        data = validate_input(FlightSchema, request.get_json())
        
        if 'airline_id' in data:
            if not db.session.get(Airline, data['airline_id']):
                return jsonify({"message": f"Airline {data['airline_id']} not found"}), 400
            flight.airline_id = data['airline_id']
        if 'flight_number' in data:
            flight.flight_number = data['flight_number']
        if 'departure_airport' in data:
            if not db.session.get(Airport, data['departure_airport']):
                return jsonify({"message": f"Departure airport {data['departure_airport']} not found"}), 400
            flight.departure_airport = data['departure_airport']
        if 'arrival_airport' in data:
            if not db.session.get(Airport, data['arrival_airport']):
                return jsonify({"message": f"Arrival airport {data['arrival_airport']} not found"}), 400
            flight.arrival_airport = data['arrival_airport']
        if 'scheduled_departure' in data:
            flight.scheduled_departure = data['scheduled_departure']
        if 'scheduled_arrival' in data:
            flight.scheduled_arrival = data['scheduled_arrival']
        if 'actual_departure' in data:
            flight.actual_departure = data['actual_departure']
        if 'actual_arrival' in data:
            flight.actual_arrival = data['actual_arrival']
        if 'status' in data:
            flight.status = data['status']

        db.session.commit()
        return jsonify(flight.to_dict()), 200
    except ValueError as e:
        return jsonify({"message": "Validation error", "errors": e.args[0]}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Update flight error: {str(e)}")
        return jsonify({"message": "Failed to update flight"}), 500

@app.route('/flights/<int:flight_id>', methods=['DELETE'])
@jwt_required()
@admin_required
@limiter.limit(app.config['RATE_LIMITS']['sensitive'])
def delete_flight(flight_id):
    flight = get_or_404(Flight, flight_id)
    if isinstance(flight, tuple):
        return flight

    try:
        db.session.delete(flight)
        db.session.commit()
        return jsonify({"message": "Flight deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Delete flight error: {str(e)}")
        return jsonify({"message": "Failed to delete flight"}), 500

# --- Error Handlers ---
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"message": "Bad request"}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"message": "Unauthorized"}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"message": "Forbidden"}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Not found"}), 404

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"message": "Rate limit exceeded"}), 429

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {str(e)}")
    return jsonify({"message": "Internal server error"}), 500

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True', 
            host='0.0.0.0', 
            port=int(os.environ.get('PORT', 5000)))