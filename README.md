# Flask Application With Unit Tests
A dummy flask application with unit tests for IS212 Software Project Management

# Installation Guide
1. set up and run a WAMP or MAMP server
2.  execute the contents of 'is212_example.sql' in phpMyAdmin, i.e. at:
-  http://localhost/phpmyadmin
-  http://localhost/phpMyAdmin

3. find your web server's root directory (e.g. C:\wamp\www) and create a
    folder called 'is212'. Copy the contents of 'htdocs' into 'is212'.
4. if you don't already have Flask installed, do:
```
	   python -m pip install flask
	   python -m pip install flask_cors
	   python -m pip install Flask-SQLAlchemy
	   python -m pip install mysql-connector-python
```

5. in the 'flask' directory, run "python app.py" in a terminal. If it fails to run, open app.py in an editor and check that the DB connection string is correct (e.g. port 3306 vs. 8889)

6. go to http://localhost/is212 where the application should be working!
