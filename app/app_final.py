from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables

app = Flask(__name__)

# Configure PostgreSQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Flight Model
class Flight(db.Model):
    __tablename__ = 'flights'

    flight_id = db.Column(db.String(10), primary_key=True)
    airline_code = db.Column(db.String(3), nullable=False)
    flight_number = db.Column(db.String(10), nullable=False)
    departure_airport = db.Column(db.String(3), nullable=False)
    arrival_airport = db.Column(db.String(3), nullable=False)
    scheduled_departure = db.Column(db.DateTime(timezone=True), nullable=False)
    scheduled_arrival = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Scheduled')
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Flight {self.flight_id}>'

# Create Flight
@app.route('/flights', methods=['POST'])
def create_flight():
    data = request.get_json()
    new_flight = Flight(
        flight_id=data['flight_id'],
        airline_code=data['airline_code'],
        flight_number=data['flight_number'],
        departure_airport=data['departure_airport'],
        arrival_airport=data['arrival_airport'],
        scheduled_departure=data['scheduled_departure'],
        scheduled_arrival=data['scheduled_arrival'],
        status=data.get('status', 'Scheduled')
    )
    db.session.add(new_flight)
    db.session.commit()
    return jsonify({"message": "Flight created"}), 201

# Get All Flights
@app.route('/flights', methods=['GET'])
def get_flights():
    flights = Flight.query.all()
    return jsonify([
        {
            "flight_id": flight.flight_id,
            "airline_code": flight.airline_code,
            "flight_number": flight.flight_number,
            "departure_airport": flight.departure_airport,
            "arrival_airport": flight.arrival_airport,
            "scheduled_departure": flight.scheduled_departure.isoformat(),
            "scheduled_arrival": flight.scheduled_arrival.isoformat(),
            "status": flight.status
        } for flight in flights
    ])

# Get Single Flight
@app.route('/flights/<string:flight_id>', methods=['GET'])
def get_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    return jsonify({
        "flight_id": flight.flight_id,
        "airline_code": flight.airline_code,
        "flight_number": flight.flight_number,
        "departure_airport": flight.departure_airport,
        "arrival_airport": flight.arrival_airport,
        "scheduled_departure": flight.scheduled_departure.isoformat(),
        "scheduled_arrival": flight.scheduled_arrival.isoformat(),
        "status": flight.status
    })

# Update Flight
@app.route('/flights/<string:flight_id>', methods=['PUT'])
def update_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    data = request.get_json()

    flight.airline_code = data.get('airline_code', flight.airline_code)
    flight.flight_number = data.get('flight_number', flight.flight_number)
    flight.departure_airport = data.get('departure_airport', flight.departure_airport)
    flight.arrival_airport = data.get('arrival_airport', flight.arrival_airport)
    flight.scheduled_departure = data.get('scheduled_departure', flight.scheduled_departure)
    flight.scheduled_arrival = data.get('scheduled_arrival', flight.scheduled_arrival)
    flight.status = data.get('status', flight.status)

    db.session.commit()
    return jsonify({"message": "Flight updated"})

# Delete Flight
@app.route('/flights/<string:flight_id>', methods=['DELETE'])
def delete_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    db.session.delete(flight)
    db.session.commit()
    return jsonify({"message": "Flight deleted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


