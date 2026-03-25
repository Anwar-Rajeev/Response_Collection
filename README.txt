PulseCloud Live - Streamlit App

Files included:
- app.py
- pages/1_Student_Response.py
- pages/2_Live_Word_Cloud.py
- pages/3_Admin_Dashboard.py
- utils/db.py
- utils/helpers.py
- requirements.txt

How to run locally:
1. Open terminal in this folder
2. Install packages:
   pip install -r requirements.txt
3. Run:
   streamlit run app.py

How to use:
1. Open Admin Dashboard
2. Password = admin123
3. Enter your deployed public app URL in Admin page, for example:
   https://your-app-name.streamlit.app
4. Enter a question and click Start new session
5. Open Live Word Cloud on projector
6. Students scan QR code and submit responses
7. Use Clear responses / Clear question / Close session when needed

Important:
- Change the admin password inside pages/3_Admin_Dashboard.py before deploying.
- The app stores data in a local SQLite file: pulsecloud.db
- This is suitable for a simple classroom deployment.
