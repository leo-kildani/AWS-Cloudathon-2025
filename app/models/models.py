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

