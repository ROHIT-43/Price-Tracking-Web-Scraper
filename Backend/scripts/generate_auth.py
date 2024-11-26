import os
import json
from dotenv import load_dotenv

# Load the .env file from the root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

# Access environment variables
BRIGHT_DATA_HOST = os.getenv("BRIGHT_DATA_HOST")
BRIGHT_DATA_USERNAME = os.getenv("BRIGHT_DATA_USERNAME")
BRIGHT_DATA_PASSWORD = os.getenv("BRIGHT_DATA_PASSWORD")

# Example: Use these variables
auth_data = {
    "host": BRIGHT_DATA_HOST,
    "username": BRIGHT_DATA_USERNAME,
    "password": BRIGHT_DATA_PASSWORD,
}

output_file = os.path.join(os.path.dirname(__file__), "../scraper/auth.json")

# Write the auth data to auth.json
with open(output_file, "w") as f:
    json.dump(auth_data, f, indent=4)

print(auth_data)