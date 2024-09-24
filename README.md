# Flask Application With Unit Tests
A dummy flask application with unit tests for IS212 Software Project Management

# Installation Guide
1. Create a virutal environment: `python -m venv venv`
2. Install Python dependencies:
```
chmod +x venv\bin\activate
venv\bin\activate
python install -r requirements.txt
```
3. Run the SQL Script to set up the local MySQL database:  `sudo mysql -u root < is212_example.sql`
4. Run the application to verify that it works: `python app.py`
5. Run Coverage Tests as needed:
```
python -m coverage run test_unit.py 
python -m coverage run test_integration.py 
```
6. Generate the coverage report: `python -m coverage html`