## NYC Taxi Analytics V1

This ALU full-stack Summative project for processing, analyzing, and visualizing New York City yellow taxi trip data from January 2019. It includes data cleaning, a backend API, and an interactive frontend dashboard.


**TEAM MEMEBERS**




# How to Run the Project

Follow these steps to set up and run the NYC Taxi Analytics project:

1. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Process and Optimize Data:**
   Run the unified data parser.
   ```bash
   python dsa/data_parser.py
   ```
   *Note: This processes ~680MB of data and may take 1-2 minutes.*

4. **Start the Backend API:**
   ```bash
   python api/app.py
   ```

5. **Open the Dashboard:**
   Open `web/index.html` in your browser. (Ideally using a local server like "Live Server" at `http://127.0.0.1:5500` to avoid CORS issues).


