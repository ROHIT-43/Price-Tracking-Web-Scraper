from requests import post
from dotenv import load_dotenv

load_dotenv()

REALURL = os.getenv("REACT_APP_API_URL", "http://localhost:5000")
URL = f"{REALURL}/update-tracked-products"

if __name__ == "__main__":
    print("Sending request to", URL)
    response = post(URL)
    print("Status code:", response.status_code)
