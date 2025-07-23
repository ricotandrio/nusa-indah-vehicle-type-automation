# Nusa Indah Vehicle Type Automation Server

This is the server component of the Nusa Indah Vehicle Type Automation project. This server fetch data from Arduino devices and processes it to determine the type of vehicle.

## Installation

1. Make virtual environment
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
3. Install the required packages
   ```bash
   pip install -r requirements.txt
   ```  
4. Copy the `.env.example` file to `.env` and fill in the required environment variables.
   ```bash
   cp .env.example .env
   ```
5. Run the server
   ```bash
   python run.py
   ```  