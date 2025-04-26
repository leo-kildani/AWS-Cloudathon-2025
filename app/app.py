# app.py
from flask import Flask, request, jsonify
from models import db, Airline, Airport, Flight, init_db
from database import config

app = Flask(__name__)

# Load configuration from config.py
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = config.SECRET_KEY

# Initialize the database with the app
init_db(app)

# --- Helper Functions ---
def get_or_404(model, identifier):
    """Gets an object by ID or returns 404."""
    obj = db.session.get(model, identifier) # Use db.session.get for primary key lookup
    if obj is None:
        return jsonify({"message": f"{model.__name__} not found"}), 404
    return obj

# --- Root Endpoint ---
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Flight Tracking MVP API!"})

# --- Airline CRUD Endpoints ---

@app.route('/airlines', methods=['POST'])
def create_airline():
    data = request.get_json()
    if not data or not all(k in data for k in ('airline_id', 'iata_code', 'name')):
        return jsonify({"message": "Missing required fields"}), 400

    # Check if airline already exists
    if db.session.get(Airline, data['airline_id']):
         return jsonify({"message": "Airline with this ID already exists"}), 409 # Conflict

    new_airline = Airline(
        airline_id=data['airline_id'],
        iata_code=data['iata_code'],
        name=data['name'],
        country=data.get('country') # Optional field
    )
    try:
        db.session.add(new_airline)
        db.session.commit()
        return jsonify(new_airline.to_dict()), 201 # Created
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create airline", "error": str(e)}), 500

@app.route('/airlines', methods=['GET'])
def get_airlines():
    try:
        all_airlines = Airline.query.all()
        return jsonify([airline.to_dict() for airline in all_airlines]), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve airlines", "error": str(e)}), 500


@app.route('/airlines/<string:airline_id>', methods=['GET'])
def get_airline(airline_id):
    airline = get_or_404(Airline, airline_id)
    if isinstance(airline, tuple): # Check if it's the 404 response
        return airline
    return jsonify(airline.to_dict()), 200

@app.route('/airlines/<string:airline_id>', methods=['PUT'])
def update_airline(airline_id):
    airline = get_or_404(Airline, airline_id)
    if isinstance(airline, tuple): return airline # Return 404 response

    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    # Update fields if provided in request data
    airline.iata_code = data.get('iata_code', airline.iata_code)
    airline.name = data.get('name', airline.name)
    airline.country = data.get('country', airline.country)

    try:
        db.session.commit()
        return jsonify(airline.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update airline", "error": str(e)}), 500

@app.route('/airlines/<string:airline_id>', methods=['DELETE'])
def delete_airline(airline_id):
    airline = get_or_404(Airline, airline_id)
    if isinstance(airline, tuple): return airline # Return 404 response

    try:
        # Check if any flights are associated with this airline
        if Flight.query.filter_by(airline_id=airline_id).first():
            return jsonify({"message": "Cannot delete airline with associated flights"}), 400

        db.session.delete(airline)
        db.session.commit()
        return jsonify({"message": "Airline deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete airline", "error": str(e)}), 500


# --- Airport CRUD Endpoints --- (Similar structure to Airlines)

@app.route('/airports', methods=['POST'])
def create_airport():
    data = request.get_json()
    required = ['airport_id', 'icao_code', 'name', 'city', 'country', 'latitude', 'longitude']
    if not data or not all(k in data for k in required):
        return jsonify({"message": "Missing required fields"}), 400

    if db.session.get(Airport, data['airport_id']):
         return jsonify({"message": "Airport with this ID already exists"}), 409

    try:
        # Ensure latitude/longitude can be converted
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
    except ValueError:
        return jsonify({"message": "Invalid latitude or longitude format"}), 400

    new_airport = Airport(
        airport_id=data['airport_id'],
        icao_code=data['icao_code'],
        name=data['name'],
        city=data['city'],
        country=data['country'],
        latitude=latitude,
        longitude=longitude
    )
    try:
        db.session.add(new_airport)
        db.session.commit()
        return jsonify(new_airport.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create airport", "error": str(e)}), 500


@app.route('/airports', methods=['GET'])
def get_airports():
    try:
        all_airports = Airport.query.all()
        return jsonify([airport.to_dict() for airport in all_airports]), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve airports", "error": str(e)}), 500


@app.route('/airports/<string:airport_id>', methods=['GET'])
def get_airport(airport_id):
    airport = get_or_404(Airport, airport_id)
    if isinstance(airport, tuple): return airport
    return jsonify(airport.to_dict()), 200

@app.route('/airports/<string:airport_id>', methods=['PUT'])
def update_airport(airport_id):
    airport = get_or_404(Airport, airport_id)
    if isinstance(airport, tuple): return airport

    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    try:
        airport.icao_code = data.get('icao_code', airport.icao_code)
        airport.name = data.get('name', airport.name)
        airport.city = data.get('city', airport.city)
        airport.country = data.get('country', airport.country)
        if 'latitude' in data:
            airport.latitude = float(data['latitude'])
        if 'longitude' in data:
            airport.longitude = float(data['longitude'])
    except ValueError:
        return jsonify({"message": "Invalid latitude or longitude format"}), 400
    except Exception as e:
         return jsonify({"message": "Failed to parse update data", "error": str(e)}), 400

    try:
        db.session.commit()
        return jsonify(airport.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update airport", "error": str(e)}), 500


@app.route('/airports/<string:airport_id>', methods=['DELETE'])
def delete_airport(airport_id):
    airport = get_or_404(Airport, airport_id)
    if isinstance(airport, tuple): return airport

    try:
         # Check if any flights are associated
        if Flight.query.filter((Flight.departure_airport == airport_id) | (Flight.arrival_airport == airport_id)).first():
            return jsonify({"message": "Cannot delete airport with associated flights"}), 400

        db.session.delete(airport)
        db.session.commit()
        return jsonify({"message": "Airport deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete airport", "error": str(e)}), 500


# --- Flight CRUD Endpoints --- (Similar structure)
# Note: Handling timestamps and foreign keys requires care

@app.route('/flights', methods=['POST'])
def create_flight():
    data = request.get_json()
    required = ['airline_id', 'flight_number', 'departure_airport', 'arrival_airport', 'scheduled_departure', 'scheduled_arrival']
    if not data or not all(k in data for k in required):
        return jsonify({"message": "Missing required fields"}), 400

    # Validate foreign keys exist
    if not db.session.get(Airline, data['airline_id']):
        return jsonify({"message": f"Airline {data['airline_id']} not found"}), 400
    if not db.session.get(Airport, data['departure_airport']):
         return jsonify({"message": f"Departure airport {data['departure_airport']} not found"}), 400
    if not db.session.get(Airport, data['arrival_airport']):
         return jsonify({"message": f"Arrival airport {data['arrival_airport']} not found"}), 400

    try:
        # Convert ISO timestamp strings back to datetime objects
        # Basic error handling for timestamp format
        from dateutil import parser
        scheduled_departure = parser.isoparse(data['scheduled_departure'])
        scheduled_arrival = parser.isoparse(data['scheduled_arrival'])
        actual_departure = parser.isoparse(data['actual_departure']) if data.get('actual_departure') else None
        actual_arrival = parser.isoparse(data['actual_arrival']) if data.get('actual_arrival') else None

    except ValueError:
         return jsonify({"message": "Invalid timestamp format. Use ISO 8601 format."}), 400

    new_flight = Flight(
        airline_id=data['airline_id'],
        flight_number=data['flight_number'],
        departure_airport=data['departure_airport'],
        arrival_airport=data['arrival_airport'],
        scheduled_departure=scheduled_departure,
        scheduled_arrival=scheduled_arrival,
        actual_departure=actual_departure, # Handle optional fields
        actual_arrival=actual_arrival,     # Handle optional fields
        status=data.get('status', 'Scheduled') # Use default if not provided
    )
    try:
        db.session.add(new_flight)
        db.session.commit()
        # Access the auto-generated flight_id AFTER commit
        return jsonify(new_flight.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create flight", "error": str(e)}), 500

@app.route('/flights', methods=['GET'])
def get_flights():
    # Optional query parameters for filtering (example)
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
        return jsonify({"message": "Failed to retrieve flights", "error": str(e)}), 500


@app.route('/flights/<int:flight_id>', methods=['GET'])
def get_flight(flight_id):
    flight = get_or_404(Flight, flight_id)
    if isinstance(flight, tuple): return flight
    return jsonify(flight.to_dict()), 200

@app.route('/flights/<int:flight_id>', methods=['PUT', 'PATCH']) # Allow PATCH for partial updates
def update_flight(flight_id):
    flight = get_or_404(Flight, flight_id)
    if isinstance(flight, tuple): return flight

    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    try:
        from dateutil import parser
        # Update only fields provided in the request
        if 'airline_id' in data:
            if not db.session.get(Airline, data['airline_id']): return jsonify({"message": f"Airline {data['airline_id']} not found"}), 400
            flight.airline_id = data['airline_id']
        if 'flight_number' in data:
            flight.flight_number = data['flight_number']
        if 'departure_airport' in data:
            if not db.session.get(Airport, data['departure_airport']): return jsonify({"message": f"Departure airport {data['departure_airport']} not found"}), 400
            flight.departure_airport = data['departure_airport']
        if 'arrival_airport' in data:
            if not db.session.get(Airport, data['arrival_airport']): return jsonify({"message": f"Arrival airport {data['arrival_airport']} not found"}), 400
            flight.arrival_airport = data['arrival_airport']
        if 'scheduled_departure' in data:
            flight.scheduled_departure = parser.isoparse(data['scheduled_departure'])
        if 'scheduled_arrival' in data:
            flight.scheduled_arrival = parser.isoparse(data['scheduled_arrival'])
        if 'actual_departure' in data:
            flight.actual_departure = parser.isoparse(data['actual_departure']) if data['actual_departure'] else None
        if 'actual_arrival' in data:
            flight.actual_arrival = parser.isoparse(data['actual_arrival']) if data['actual_arrival'] else None
        if 'status' in data:
            # Optional: Validate against allowed flight_status ENUM values if needed
            flight.status = data['status']

    except ValueError:
         return jsonify({"message": "Invalid timestamp format. Use ISO 8601 format."}), 400
    except Exception as e:
        return jsonify({"message": "Failed to parse update data", "error": str(e)}), 400


    try:
        db.session.commit()
        return jsonify(flight.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update flight", "error": str(e)}), 500


@app.route('/flights/<int:flight_id>', methods=['DELETE'])
def delete_flight(flight_id):
    flight = get_or_404(Flight, flight_id)
    if isinstance(flight, tuple): return flight

    try:
        db.session.delete(flight)
        db.session.commit()
        return jsonify({"message": "Flight deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete flight", "error": str(e)}), 500

# --- Run the App ---
if __name__ == '__main__':
    # Note: `debug=True` is helpful for development but should be `False` in production
    app.run(debug=True, host='0.0.0.0', port=5000) # Listen on all network interfaces