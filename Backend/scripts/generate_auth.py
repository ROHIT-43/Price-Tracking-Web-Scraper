# import os
# import json
# from dotenv import load_dotenv

# # Load the .env file from the root directory
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

# # Access environment variables
# BRIGHT_DATA_HOST = os.getenv("BRIGHT_DATA_HOST")
# BRIGHT_DATA_USERNAME = os.getenv("BRIGHT_DATA_USERNAME")
# BRIGHT_DATA_PASSWORD = os.getenv("BRIGHT_DATA_PASSWORD")

# # Example: Use these variables
# auth_data = {
#     "host": BRIGHT_DATA_HOST,
#     "username": BRIGHT_DATA_USERNAME,
#     "password": BRIGHT_DATA_PASSWORD,
# }

# output_file = os.path.join(os.path.dirname(__file__), "../scraper/auth.json")

# # Write the auth data to auth.json
# with open(output_file, "w") as f:
#     json.dump(auth_data, f, indent=4)

# print(auth_data)

import os
import json
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file (if you have one)
load_dotenv()

# Collect the environment variables
auth_data = {
    "host": os.getenv("BRIGHT_DATA_HOST"),
    "username": os.getenv("BRIGHT_DATA_USERNAME"),
    "password": os.getenv("BRIGHT_DATA_PASSWORD"),
}

# Create a temporary directory
temp_dir = tempfile.gettempdir()

# Define the path for your temporary auth.json file
output_file = os.path.join(temp_dir, "auth.json")

# Write the JSON data to the temporary file
with open(output_file, "w") as f:
    json.dump(auth_data, f, indent=4)

print(f"auth.json file created at {output_file}")
