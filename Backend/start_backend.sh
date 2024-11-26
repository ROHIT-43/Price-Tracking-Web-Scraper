#!/bin/bash

# Run the script to generate auth.json
python3 scripts/generate_auth.py

# Now run the Flask app with gunicorn
gunicorn app:app
