# app.py
from flask import Flask, request, jsonify
from models import db, Airline, Airport, Flight, init_db
from database import config

app = Flask(__name__)

# --- Root Endpoint ---
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Flight Tracking MVP API!"})

# --- Run the App ---
if __name__ == '__main__':
    # Note: `debug=True` is helpful for development but should be `False` in production
    app.run(debug=True, host='0.0.0.0', port=5000) # Listen on all network interfaces