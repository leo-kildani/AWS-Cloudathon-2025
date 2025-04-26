-- Simplified Flight Tracking Schema for MVP

-- Create enum type for flight status (essential for tracking)
CREATE TYPE flight_status AS ENUM (
    'Scheduled',
    'Boarding',
    'Departed',
    'In Air',
    'Landed',
    'Cancelled',
    'Diverted',
    'Delayed'
);

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS flights CASCADE;
DROP TABLE IF EXISTS airlines CASCADE;
DROP TABLE IF EXISTS airports CASCADE;

-- Airlines table (Simplified)
CREATE TABLE airlines (
    airline_id VARCHAR(3) PRIMARY KEY,  -- ICAO or simplified code
    iata_code VARCHAR(2) NOT NULL UNIQUE, -- IATA code [cite: 10, 11]
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) -- Kept country for basic context [cite: 10]
);

COMMENT ON TABLE airlines IS 'Basic information about airlines';

-- Airports table (Simplified)
CREATE TABLE airports (
    airport_id VARCHAR(3) PRIMARY KEY,  -- IATA code [cite: 12]
    icao_code VARCHAR(4) NOT NULL UNIQUE, -- ICAO code [cite: 12, 13]
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL, -- Kept location for basic mapping [cite: 12]
    longitude DECIMAL(10, 6) NOT NULL -- Kept location for basic mapping [cite: 12]
);

COMMENT ON TABLE airports IS 'Basic information about airports';

-- Flights table (Simplified)
CREATE TABLE flights (
    flight_id SERIAL PRIMARY KEY, -- Simplified to auto-incrementing integer
    airline_id VARCHAR(3) NOT NULL REFERENCES airlines(airline_id),
    flight_number VARCHAR(10) NOT NULL,
    departure_airport VARCHAR(3) NOT NULL REFERENCES airports(airport_id),
    arrival_airport VARCHAR(3) NOT NULL REFERENCES airports(airport_id),
    scheduled_departure TIMESTAMP WITH TIME ZONE NOT NULL,
    scheduled_arrival TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_departure TIMESTAMP WITH TIME ZONE, -- Kept actual times for status updates [cite: 23, 24]
    actual_arrival TIMESTAMP WITH TIME ZONE, -- Kept actual times for status updates [cite: 24]
    status flight_status NOT NULL DEFAULT 'Scheduled', -- Essential status field [cite: 24]
    -- Removed: aircraft_id, estimated times, gates, runways, duration, distance, delay, baggage, live tracking fields etc. [cite: 23, 24]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_flight UNIQUE (airline_id, flight_number, scheduled_departure) -- Basic uniqueness constraint
);

COMMENT ON TABLE flights IS 'Core information about scheduled and active flights for MVP';

-- Add basic indexes for performance on essential lookups
CREATE INDEX idx_flights_airline ON flights(airline_id);
CREATE INDEX idx_flights_departure_airport ON flights(departure_airport);
CREATE INDEX idx_flights_arrival_airport ON flights(arrival_airport);
CREATE INDEX idx_flights_status ON flights(status);
CREATE INDEX idx_flights_scheduled_departure ON flights(scheduled_departure);