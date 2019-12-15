Hemogram - Web application for reading Pheripheral Blood smears remotely
===

**Hemogram**, a web application, is developed as a prototype project that aims at providing a user-friendly yet robust platform to remotely examine peripheral blood smears by experienced laboratory professionals. The primary objective of this application is to support telelaboratory medicine and introduce the concept of tele-hematology to provide remote smear evaluation service to
resource-limited clinics. Implementing Hemogram to resource-limited clinics can provide added laboratory support in diagnosing
hematologic disorders and alleviate the problem of shortage of laboratory professionals.

**App url** - http://hemogram.labmed.uw.edu/

Table of Contents
---
1. Technologies
2. Features
3. Installation
4. Testing
5. Deployment
6. Author
7. References


Technologies
---
Back-end: Python3.6, Flask, Jinja2, PostgreSQL, SQLAlchemy

Front-end: Bootstrap, Javascript, jQuery, Ajax, HTML, CSS

Hosting: Heroku

Object Storage: Amazon Web Services S3

Features
---
Admin - User Management, Assign Roles

Users - Login, Logout, Update Profile, Update Password

System - Pending Log, Event Trace, New Sample Alert

Smear Evaluation - Drag and Drop, Context Menu, Cell Morphologoy Annotation, Final Laboratory Report

Installation
---
In order to run this application on local machine, please follow these instructions.

**Prerequisite:**
1. Install PostgreSQL
2. Add postgresql /bin and /lib directory path to your 'System Variables PATH'
3. Create required databases through command terminal
	* `createdb hemogram`
	* `createdb test_hemogram`


**Set Up:**	
1. Create and activate a virtual environment with following steps
	
	In command line 
	* `pip install virtualenv`
	
	* `mkdir Environments`

	Inside Environments directory - create and activate a virtual environment

	* `virtualenv hemogram`

	* `.\hemogram\Scripts\activate`

2. Clone the repository to using git bash

	* `git clone https://github.com/sukraBhandari/hemogram.git`

3. Install requirements.txt using

	* `pip install -r requirements.txt`

4. set all environment configuration variables[located in config.py file] in local machine

5. Create a dabatase tables through command-line
	
	* `set FLASK_APP=hemogram.py`

	* `flask shell`

	* `>>> from app import db`

	* `>>> db.create_all()`

**Run:**
1. To run app in the web browser

	  * Start the web server
		`set FLASK_APP=hemogram.py`

	  * Run the app
		`flask run`

	  * Access the app in your web browser
		`http://localhost:5000/`

2. To access app in command-line

	`set FLASK_APP=hemogram.py`

	`flask shell`



1. To test app using unittest

	`TODO`
	
**Author:**
---
Sukra Bhandari
