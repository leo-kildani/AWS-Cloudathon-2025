-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE flights (
    flight_id VARCHAR(10) PRIMARY KEY,              
    airline_code VARCHAR(3) NOT NULL,                
    flight_number VARCHAR(10) NOT NULL,              
    departure_airport VARCHAR(3) NOT NULL,           
    arrival_airport VARCHAR(3) NOT NULL,             
    scheduled_departure TIMESTAMP WITH TIME ZONE NOT NULL,  
    scheduled_arrival TIMESTAMP WITH TIME ZONE NOT NULL,    
    status VARCHAR(20) NOT NULL DEFAULT 'Scheduled', -- Values: 'Scheduled', 'Departed', 'Landed', 'Cancelled'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
