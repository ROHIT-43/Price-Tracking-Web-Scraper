# Project Information

This project provides a user interface to interact with an automated price tracking web scraper. Currently the tracker scrapes amazon.ca, but could be configured to scrape multiple sources.

## Libraries/Frameworks/Modules

This project uses:

- React
- Flask
- Playwright
- Bright Data (Web Scraping Browser)

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.x** - Required for the Flask backend
- **Node.js and npm** - Required for the React frontend
  - Download from [nodejs.org](https://nodejs.org/)
  - This will install both Node.js and npm together
  - After installation, restart your terminal/PowerShell

## Using the Scraper

Install all dependencies, create the `auth.json` file, start the flask backend, run the react frontend and interact with the tool.

### auth.json

Fill in your [Bright Data Scraping Browser](https://brightdata.com/products/scraping-browser) credentials in a `Backend/scraper/auth.json` file (see `auth_example.json`).

**How to get your Bright Data credentials:**
1. Sign up or log in to [Bright Data](https://brightdata.com/)
2. Navigate to your dashboard and select the **Scraping Browser** product
3. Go to your zone settings/credentials section
4. Copy the following values:
   - **host**: Usually `brd.superproxy.io:9222` (check your dashboard)
   - **username**: Format like `brd-customer-{customer_id}-zone-{zone_name}`
   - **password**: Your zone's password/authentication token
5. Paste them into `Backend/scraper/auth.json` replacing the example values

### Python Flask Backend

- `cd Backend`
- Activate the virtual environment:
  - **Windows PowerShell:** `.\venv\Scripts\Activate.ps1`
  - **Windows Command Prompt:** `venv\Scripts\activate.bat`
  - **Linux/Mac:** `source venv/bin/activate`
- If packages aren't installed: `pip install -r requirements.txt`
- `playwright install`
- `python app.py` or `python3 app.py`

### Running the React Frontend

- `cd frontend`
- `npm i`
- `npm run start`

## Setting Up Automation

To automate the collection of prices from this software simply run the `scheduler/main.py` file at your desired increment while the python flask backend is running.

### Windows

I have created a simple `.bat` script called `run.bat` that you can schedule to execute using the Windows Task Scheduler that will automatically run the backend api and send the appropriate request to it.


# 💻 Launch Your Software Development Career Today!  

🎓 **No degree? No problem!** My program equips you with everything you need to break into tech and land an entry-level software development role.  

🚀 **Why Join?**  
- 💼 **$70k+ starting salary potential**  
- 🕐 **Self-paced:** Complete on your own time  
- 🤑 **Affordable:** Low risk compared to expensive bootcamps or degrees
- 🎯 **45,000+ job openings** in the market  

👉 **[Start your journey today!](https://techwithtim.net/dev)**  
No experience needed—just your determination. Future-proof your career and unlock six-figure potential like many of our students have!  
