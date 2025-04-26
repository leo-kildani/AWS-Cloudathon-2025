# models.py

- Acts as a bridge between the Flask app and the PostgreSQL database. Uses **Flask-SQLAlchemy**, which is an ORM for Flask.

# app.py

- Main Flask application file that initializes the app, sets up routes, and handles requests.

## API Endpoints

### `create_airline()` -> **POST /airlines**:

- **Purpose:** Creates a new airline record.
- **Expected JSON Request Body:**

  ```json
  {
    "airline_id": "string (max 3 chars, required)",
    "iata_code": "string (max 2 chars, required)",
    "name": "string (max 100 chars, required)",
    "country": "string (max 50 chars, optional)"
  }
  ```

- **Expected JSON Responses:**
  1.  **Missing Required Fields (HTTP 400):**
      ```json
      { "message": "Missing required fields" }
      ```
  2.  **Airline Already Exists (HTTP 409):**
      ```json
      { "message": "Airline with this ID already exists" }
      ```
  3.  **Airline Created Successfully (HTTP 201):**
      ```json
      // Example:
      {
        "airline_id": "BAW",
        "iata_code": "BA",
        "name": "British Airways",
        "country": "United Kingdom"
      }
      ```
  4.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to create airline",
        "error": "<detailed SQLAlchemy error>"
      }
      ```

### `get_airlines()` -\> **GET /airlines**:

- **Purpose:** Retrieves a list of all airlines.
- **Expected Request:** None (No body or required parameters).
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      // Example:
      [
        {
          "airline_id": "BAW",
          "iata_code": "BA",
          "name": "British Airways",
          "country": "United Kingdom"
        },
        {
          "airline_id": "UAL",
          "iata_code": "UA",
          "name": "United Airlines",
          "country": "United States"
        }
        // ... more airlines
      ]
      ```
      _Note: Returns an empty list `[]` if no airlines exist._
  2.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to retrieve airlines",
        "error": "<detailed SQLAlchemy error>"
      }
      ```

### `get_airline()` -\> **GET /airlines/[https://www.google.com/search?q=string:airline_id](https://www.google.com/search?q=string:airline_id)**:

- **Purpose:** Retrieves a specific airline by its ID.
- **Expected Request:**
  - **URL Parameter:** `airline_id` (string, max 3 chars).
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      // Example:
      {
        "airline_id": "UAL",
        "iata_code": "UA",
        "name": "United Airlines",
        "country": "United States"
      }
      ```
  2.  **Not Found (HTTP 404):**
      ```json
      { "message": "Airline not found" }
      ```

### `update_airline()` -\> **PUT /airlines/[https://www.google.com/search?q=string:airline_id](https://www.google.com/search?q=string:airline_id)**:

- **Purpose:** Updates an existing airline's details (replaces the resource).
- **Expected Request:**
  - **URL Parameter:** `airline_id` (string, max 3 chars).
  - **JSON Request Body:**
    ```json
    // Fields are optional in the request,
    // but at least one should be present for an update.
    // Missing fields retain their current value.
    {
      "iata_code": "string (max 2 chars)",
      "name": "string (max 100 chars)",
      "country": "string (max 50 chars)"
    }
    ```
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      // Example: Shows the state AFTER the update
      {
        "airline_id": "UAL",
        "iata_code": "UA",
        "name": "United Airlines Inc.", // Updated name
        "country": "United States"
      }
      ```
  2.  **Not Found (HTTP 404):**
      ```json
      { "message": "Airline not found" }
      ```
  3.  **No Input Data (HTTP 400):**
      ```json
      { "message": "No input data provided" }
      ```
  4.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to update airline",
        "error": "<detailed SQLAlchemy error>"
      }
      ```

### `delete_airline()` -\> **DELETE /airlines/[https://www.google.com/search?q=string:airline_id](https://www.google.com/search?q=string:airline_id)**:

- **Purpose:** Deletes a specific airline by its ID.
- **Expected Request:**
  - **URL Parameter:** `airline_id` (string, max 3 chars).
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      { "message": "Airline deleted successfully" }
      ```
  2.  **Not Found (HTTP 404):**
      ```json
      { "message": "Airline not found" }
      ```
  3.  **Cannot Delete (Associated Flights) (HTTP 400):**
      ```json
      { "message": "Cannot delete airline with associated flights" }
      ```
  4.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to delete airline",
        "error": "<detailed SQLAlchemy error>"
      }
      ```

### `create_airport()` -\> **POST /airports**:

- **Purpose:** Creates a new airport record.
- **Expected JSON Request Body:**
  ```json
  {
    "airport_id": "string (max 3 chars, required)",
    "icao_code": "string (max 4 chars, required)",
    "name": "string (max 100 chars, required)",
    "city": "string (max 50 chars, required)",
    "country": "string (max 50 chars, required)",
    "latitude": "number (decimal, required)",
    "longitude": "number (decimal, required)"
  }
  ```
- **Expected JSON Responses:**
  1.  **Missing Required Fields (HTTP 400):**
      ```json
      { "message": "Missing required fields" }
      ```
  2.  **Invalid Lat/Lon Format (HTTP 400):**
      ```json
      { "message": "Invalid latitude or longitude format" }
      ```
  3.  **Airport Already Exists (HTTP 409):**
      ```json
      { "message": "Airport with this ID already exists" }
      ```
  4.  **Airport Created Successfully (HTTP 201):**
      ```json
      // Example: Note lat/lon returned as strings
      {
        "airport_id": "SFO",
        "icao_code": "KSFO",
        "name": "San Francisco International",
        "city": "San Francisco",
        "country": "United States",
        "latitude": "37.621313",
        "longitude": "-122.378955"
      }
      ```
  5.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to create airport",
        "error": "<detailed SQLAlchemy error>"
      }
      ```

### `get_airports()` -\> **GET /airports**:

- **Purpose:** Retrieves a list of all airports.
- **Expected Request:** None.
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      // Example:
      [
        {
          "airport_id": "SFO",
          "icao_code": "KSFO",
          "name": "San Francisco International",
          "city": "San Francisco",
          "country": "United States",
          "latitude": "37.621313",
          "longitude": "-122.378955"
        },
        {
          "airport_id": "LHR",
          "icao_code": "EGLL",
          "name": "London Heathrow",
          "city": "London",
          "country": "United Kingdom",
          "latitude": "51.470022",
          "longitude": "-0.454296"
        }
        // ... more airports
      ]
      ```
      _Note: Returns an empty list `[]` if no airports exist._
  2.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to retrieve airports",
        "error": "<detailed SQLAlchemy error>"
      }
      ```

### `get_airport()` -\> **GET /airports/[https://www.google.com/search?q=string:airport_id](https://www.google.com/search?q=string:airport_id)**:

- **Purpose:** Retrieves a specific airport by its ID.
- **Expected Request:**
  - **URL Parameter:** `airport_id` (string, max 3 chars).
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      // Example:
      {
        "airport_id": "SFO",
        "icao_code": "KSFO",
        "name": "San Francisco International",
        "city": "San Francisco",
        "country": "United States",
        "latitude": "37.621313",
        "longitude": "-122.378955"
      }
      ```
  2.  **Not Found (HTTP 404):**
      ```json
      { "message": "Airport not found" }
      ```

### `update_airport()` -\> **PUT /airports/[https://www.google.com/search?q=string:airport_id](https://www.google.com/search?q=string:airport_id)**:

- **Purpose:** Updates an existing airport's details.
- **Expected Request:**
  - **URL Parameter:** `airport_id` (string, max 3 chars).
  - **JSON Request Body:**
    ```json
    // Fields are optional in the request.
    {
      "icao_code": "string (max 4 chars)",
      "name": "string (max 100 chars)",
      "city": "string (max 50 chars)",
      "country": "string (max 50 chars)",
      "latitude": "number (decimal)",
      "longitude": "number (decimal)"
    }
    ```
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      // Example: Shows the state AFTER the update
      {
        "airport_id": "SFO",
        "icao_code": "KSFO",
        "name": "San Francisco Intl Airport", // Updated name
        "city": "San Francisco",
        "country": "United States",
        "latitude": "37.621313",
        "longitude": "-122.378955"
      }
      ```
  2.  **Not Found (HTTP 404):**
      ```json
      { "message": "Airport not found" }
      ```
  3.  **No Input Data (HTTP 400):**
      ```json
      { "message": "No input data provided" }
      ```
  4.  **Invalid Lat/Lon Format (HTTP 400):**
      ```json
      { "message": "Invalid latitude or longitude format" }
      ```
  5.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to update airport",
        "error": "<detailed SQLAlchemy error>"
      }
      ```

### `delete_airport()` -\> **DELETE /airports/[https://www.google.com/search?q=string:airport_id](https://www.google.com/search?q=string:airport_id)**:

- **Purpose:** Deletes a specific airport by its ID.
- **Expected Request:**
  - **URL Parameter:** `airport_id` (string, max 3 chars).
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      { "message": "Airport deleted successfully" }
      ```
  2.  **Not Found (HTTP 404):**
      ```json
      { "message": "Airport not found" }
      ```
  3.  **Cannot Delete (Associated Flights) (HTTP 400):**
      ```json
      { "message": "Cannot delete airport with associated flights" }
      ```
  4.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to delete airport",
        "error": "<detailed SQLAlchemy error>"
      }
      ```

### `create_flight()` -\> **POST /flights**:

- **Purpose:** Creates a new flight record.
- **Expected JSON Request Body:**
  ```json
  {
    "airline_id": "string (max 3 chars, required)",
    "flight_number": "string (max 10 chars, required)",
    "departure_airport": "string (max 3 chars, required)",
    "arrival_airport": "string (max 3 chars, required)",
    "scheduled_departure": "string (ISO 8601 format, required)", // e.g., "2025-04-27T10:00:00+00:00"
    "scheduled_arrival": "string (ISO 8601 format, required)", // e.g., "2025-04-27T18:30:00+00:00"
    "actual_departure": "string (ISO 8601 format, optional)",
    "actual_arrival": "string (ISO 8601 format, optional)",
    "status": "string (optional, defaults to 'Scheduled')" // e.g., 'Scheduled', 'Departed', 'Landed' etc.
  }
  ```
- **Expected JSON Responses:**
  1.  **Missing Required Fields (HTTP 400):**
      ```json
      { "message": "Missing required fields" }
      ```
  2.  **Invalid Timestamp Format (HTTP 400):**
      ```json
      { "message": "Invalid timestamp format. Use ISO 8601 format." }
      ```
  3.  **Airline Not Found (HTTP 400):**
      ```json
      { "message": "Airline <airline_id> not found" }
      ```
  4.  **Departure Airport Not Found (HTTP 400):**
      ```json
      { "message": "Departure airport <airport_id> not found" }
      ```
  5.  **Arrival Airport Not Found (HTTP 400):**
      ```json
      { "message": "Arrival airport <airport_id> not found" }
      ```
  6.  **Flight Created Successfully (HTTP 201):**
      ```json
      // Example: Note auto-generated flight_id and timestamps returned as ISO strings
      {
        "flight_id": 1, // Auto-generated integer ID
        "airline_id": "UAL",
        "flight_number": "UA123",
        "departure_airport": "SFO",
        "arrival_airport": "LHR",
        "scheduled_departure": "2025-04-27T10:00:00+00:00",
        "scheduled_arrival": "2025-04-27T18:30:00+00:00",
        "actual_departure": null,
        "actual_arrival": null,
        "status": "Scheduled",
        "created_at": "2025-04-26T18:54:12+00:00", // Example timestamp
        "updated_at": "2025-04-26T18:54:12+00:00" // Example timestamp
      }
      ```
  7.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to create flight",
        "error": "<detailed SQLAlchemy error>"
      }
      ```

### `get_flights()` -\> **GET /flights**:

- **Purpose:** Retrieves a list of flights, optionally filtered.
- **Expected Request:**
  - **Optional Query Parameters:**
    - `?status=<status_string>` (e.g., `?status=Landed`)
    - `?airline_id=<airline_id_string>` (e.g., `?airline_id=UAL`)
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      // Example:
      [
        {
          "flight_id": 1,
          "airline_id": "UAL",
          "flight_number": "UA123",
          // ... other fields
          "status": "Scheduled"
        },
        {
          "flight_id": 2,
          "airline_id": "BAW",
          "flight_number": "BA456",
          // ... other fields
          "status": "Landed"
        }
        // ... more flights matching filter (if any)
      ]
      ```
      _Note: Returns an empty list `[]` if no flights match._
  2.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to retrieve flights",
        "error": "<detailed SQLAlchemy error>"
      }
      ```

### `get_flight()` -\> **GET /flights/[https://www.google.com/search?q=int:flight_id](https://www.google.com/search?q=int:flight_id)**:

- **Purpose:** Retrieves a specific flight by its ID.
- **Expected Request:**
  - **URL Parameter:** `flight_id` (integer).
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      // Example:
      {
        "flight_id": 1,
        "airline_id": "UAL",
        "flight_number": "UA123",
        "departure_airport": "SFO",
        "arrival_airport": "LHR",
        "scheduled_departure": "2025-04-27T10:00:00+00:00",
        "scheduled_arrival": "2025-04-27T18:30:00+00:00",
        "actual_departure": null,
        "actual_arrival": null,
        "status": "Scheduled",
        "created_at": "2025-04-26T18:54:12+00:00",
        "updated_at": "2025-04-26T18:54:12+00:00"
      }
      ```
  2.  **Not Found (HTTP 404):**
      ```json
      { "message": "Flight not found" }
      ```

### `update_flight()` -\> **PUT /flights/[https://www.google.com/search?q=int:flight_id](https://www.google.com/search?q=int:flight_id)** or **PATCH /flights/[https://www.google.com/search?q=int:flight_id](https://www.google.com/search?q=int:flight_id)**:

- **Purpose:** Updates an existing flight's details (handles full or partial updates).
- **Expected Request:**
  - **URL Parameter:** `flight_id` (integer).
  - **JSON Request Body:**
    ```json
    // Fields are optional in the request. Include only fields to change.
    {
      "airline_id": "string (max 3 chars)",
      "flight_number": "string (max 10 chars)",
      "departure_airport": "string (max 3 chars)",
      "arrival_airport": "string (max 3 chars)",
      "scheduled_departure": "string (ISO 8601 format)",
      "scheduled_arrival": "string (ISO 8601 format)",
      "actual_departure": "string (ISO 8601 format, or null)",
      "actual_arrival": "string (ISO 8601 format, or null)",
      "status": "string" // e.g., 'Departed', 'Landed' etc.
    }
    ```
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      // Example: Shows the state AFTER the update
      {
        "flight_id": 1,
        "airline_id": "UAL",
        "flight_number": "UA123",
        "departure_airport": "SFO",
        "arrival_airport": "LHR",
        "scheduled_departure": "2025-04-27T10:00:00+00:00",
        "scheduled_arrival": "2025-04-27T18:30:00+00:00",
        "actual_departure": "2025-04-27T10:15:00+00:00", // Updated
        "actual_arrival": null,
        "status": "Departed", // Updated
        "created_at": "2025-04-26T18:54:12+00:00",
        "updated_at": "2025-04-26T19:10:00+00:00" // Updated timestamp
      }
      ```
  2.  **Not Found (HTTP 404):**
      ```json
      { "message": "Flight not found" }
      ```
  3.  **No Input Data (HTTP 400):**
      ```json
      { "message": "No input data provided" }
      ```
  4.  **Invalid Timestamp Format (HTTP 400):**
      ```json
      { "message": "Invalid timestamp format. Use ISO 8601 format." }
      ```
  5.  **Airline Not Found (HTTP 400):** (If updating airline_id to non-existent one)
      ```json
      { "message": "Airline <airline_id> not found" }
      ```
  6.  **Airport Not Found (HTTP 400):** (If updating departure/arrival airport to non-existent one)
      ```json
      { "message": "Departure airport <airport_id> not found" }
      // or
      { "message": "Arrival airport <airport_id> not found" }
      ```
  7.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to update flight",
        "error": "<detailed SQLAlchemy error>"
      }
      ```

### `delete_flight()` -\> **DELETE /flights/[https://www.google.com/search?q=int:flight_id](https://www.google.com/search?q=int:flight_id)**:

- **Purpose:** Deletes a specific flight by its ID.
- **Expected Request:**
  - **URL Parameter:** `flight_id` (integer).
- **Expected JSON Responses:**
  1.  **Success (HTTP 200):**
      ```json
      { "message": "Flight deleted successfully" }
      ```
  2.  **Not Found (HTTP 404):**
      ```json
      { "message": "Flight not found" }
      ```
  3.  **Database Error (HTTP 500):**
      ```json
      {
        "message": "Failed to delete flight",
        "error": "<detailed SQLAlchemy error>"
      }
      ```
