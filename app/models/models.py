# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy without attaching it to a specific Flask app yet
# It will be attached in app.py
db = SQLAlchemy()

# Define the Airline model
class Airline(db.Model):
    __tablename__ = 'airlines' # Explicitly set table name

    airline_id = db.Column(db.String(3), primary_key=True)
    iata_code = db.Column(db.String(2), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50))

    # Relationship (optional but helpful): An airline can have many flights
    flights = db.relationship('Flight', backref='airline', lazy=True)

    def __repr__(self):
        return f"<Airline {self.airline_id}: {self.name}>"

    # Helper to convert model object to dictionary
    def to_dict(self):
        return {
            'airline_id': self.airline_id,
            'iata_code': self.iata_code,
            'name': self.name,
            'country': self.country
        }

# Define the Airport model
class Airport(db.Model):
    __tablename__ = 'airports'

    airport_id = db.Column(db.String(3), primary_key=True)
    icao_code = db.Column(db.String(4), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Numeric(10, 6), nullable=False)
    longitude = db.Column(db.Numeric(10, 6), nullable=False)

    # Relationships (optional but helpful)
    departing_flights = db.relationship('Flight', foreign_keys='Flight.departure_airport', backref='departure_airport_ref', lazy=True)
    arriving_flights = db.relationship('Flight', foreign_keys='Flight.arrival_airport', backref='arrival_airport_ref', lazy=True)


    def __repr__(self):
        return f"<Airport {self.airport_id}: {self.name}, {self.city}>"

    def to_dict(self):
        return {
            'airport_id': self.airport_id,
            'icao_code': self.icao_code,
            'name': self.name,
            'city': self.city,
            'country': self.country,
            # Convert Decimal to string or float for JSON serialization
            'latitude': str(self.latitude),
            'longitude': str(self.longitude)
        }

# Define the Flight model
class Flight(db.Model):
    __tablename__ = 'flights'

    flight_id = db.Column(db.Integer, primary_key=True) # SERIAL becomes Integer
    airline_id = db.Column(db.String(3), db.ForeignKey('airlines.airline_id'), nullable=False)
    flight_number = db.Column(db.String(10), nullable=False)
    departure_airport = db.Column(db.String(3), db.ForeignKey('airports.airport_id'), nullable=False)
    arrival_airport = db.Column(db.String(3), db.ForeignKey('airports.airport_id'), nullable=False)
    scheduled_departure = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    scheduled_arrival = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    actual_departure = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    actual_arrival = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    # Assuming flight_status ENUM is handled correctly by SQLAlchemy/psycopg2
    # If issues arise, may need explicit Enum handling or use String
    status = db.Column(db.String, nullable=False, default='Scheduled') # Map ENUM to String for simplicity here
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Constraints defined in SQL (like uq_flight) are usually enforced by the DB

    def __repr__(self):
        return f"<Flight {self.airline_id}{self.flight_number} {self.departure_airport}->{self.arrival_airport}>"

    def to_dict(self):
        return {
            'flight_id': self.flight_id,
            'airline_id': self.airline_id,
            'flight_number': self.flight_number,
            'departure_airport': self.departure_airport,
            'arrival_airport': self.arrival_airport,
            # Format timestamps as ISO strings for JSON
            'scheduled_departure': self.scheduled_departure.isoformat() if self.scheduled_departure else None,
            'scheduled_arrival': self.scheduled_arrival.isoformat() if self.scheduled_arrival else None,
            'actual_departure': self.actual_departure.isoformat() if self.actual_departure else None,
            'actual_arrival': self.actual_arrival.isoformat() if self.actual_arrival else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

# Helper function to initialize DB within application context
def init_db(app):
    db.init_app(app)
    with app.app_context():
        print("Database connection verified")