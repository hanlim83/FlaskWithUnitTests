# Flask Application With Unit Tests
A dummy flask application with unit tests for IS212 Software Project Management

**This repo is meant to run within a GitHub Codepace. To run it locally, you will need to ensure that you have MySQL Server and Python 3 installed**

# Installation Guide
1. Create a virtual environment: `python -m venv venv`
2. Install Python dependencies:
```
chmod +x venv\bin\activate
venv\bin\activate
python install -r requirements.txt
```
3. Run the SQL Script to set up the local MySQL database:  `sudo mysql -u root < is212_example.sql`

# How to run this application
1. Run the application to verify that it works: `python app.py`
2. Visit the webpages at `http://<codespace provided-url or localhost:5000>/view-consultations.html`
3. Run Coverage Tests as needed:
```
python -m coverage run test_unit.py 
python -m coverage run test_integration.py 
```
4. Generate the coverage report: `python -m coverage html`
