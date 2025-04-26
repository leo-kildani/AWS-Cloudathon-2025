# models.py

- Acts as a bridge between the Flask app and the PostgreSQL database. Uses **Flask-SQLAlchemy**, which is an ORM for Flask.

# app.py

- Main Flask application file that initializes the app, sets up routes, and handles requests.
  Create Airline -> "/airlines, POST"

## API Endpoints

### `create_airline()` -> **POST/airlines**:

- Creates a new airline in the database.
  - **Request Body**: JSON object with `name`, `iata_code`, and `icao_code` fields.
  - **Response**: Returns the created airline object with its ID.
- Creates an airline object given
