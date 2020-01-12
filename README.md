Hemogram - Web application for reading Pheripheral Blood smears remotely
===

**Hemogram**, a web application, is developed as a prototype project that aims at providing a user-friendly yet robust platform to remotely examine peripheral blood smears by experienced laboratory professionals. The primary objective of this application is to support telelaboratory medicine and introduce the concept of tele-hematology to provide remote smear evaluation service to
resource-limited clinics. Implementing Hemogram to resource-limited clinics can provide added laboratory support in diagnosing
a variety of toxic, infectious, and hematologic disorders. In addition to providing diagnositic support, hemogram can alleviate the problem of shortage of laboratory professionals in resource-limited clinics.

**App url** - http://hemogram.labmed.uw.edu/

**App Infrastructure** - https://github.com/sukraBhandari/Hemogram_AWS

**CI/CD using AWS CodePipeline and Elastic Beanstalk** - https://github.com/sukraBhandari/Hemogram_CICD_Beanstalk

Table of Contents
---
1. Technologies
2. Features
3. Installation and Deployment
4. Future outlook
5. Author
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

Installation and Deployment
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
	
Future Outlook
---
1. Training/Education
	* Deliver classifed images for references
	* Evaluate competency for laboratory scientists and pathologists
2. Machine Learning
	* Develop training/validation sets
	* Real-time decision support
	* Example - 
	
	![malaria_ml](https://user-images.githubusercontent.com/7229266/71325477-61a92b80-24a2-11ea-9519-cc77d8211908.JPG)
	
Application Screenshots
---
Demo of Hemogam applicaiton via screenshots.
* ### Login Page
![login_page](https://user-images.githubusercontent.com/7229266/71325586-d03ab900-24a3-11ea-841e-48be0904343c.jpg)

---

* ### Registration Page
![registration](https://user-images.githubusercontent.com/7229266/71325591-e34d8900-24a3-11ea-95f9-cf050b9da12b.jpg)

---
* ### Role assignment
![role](https://user-images.githubusercontent.com/7229266/71325597-f19ba500-24a3-11ea-97d9-158aef4461e7.jpg)

---
* ### Dashboard
![dashboard](https://user-images.githubusercontent.com/7229266/71325617-38899a80-24a4-11ea-8530-2341a8377e36.jpg)

---
* ### Patient Profile page
![patientprofile](https://user-images.githubusercontent.com/7229266/71325600-02e4b180-24a4-11ea-8911-e0180c345421.jpg)

---
* ### List of Patients
![patientlist](https://user-images.githubusercontent.com/7229266/71325602-1001a080-24a4-11ea-87f0-7c32bd44ce9a.jpg)

---
* ### Clinic Profile page
![clinicProfile](https://user-images.githubusercontent.com/7229266/71325609-1bed6280-24a4-11ea-9b62-ba920b11cee7.jpg)

---
* ### Patient Blood Cells for evaluation
![wbc](https://user-images.githubusercontent.com/7229266/71325632-6f5fb080-24a4-11ea-9f0f-bf98b7ba4861.jpg)

---
* ### Blood Cells annotation/classification via drag and drop
![draganddrop](https://user-images.githubusercontent.com/7229266/71325624-51924b80-24a4-11ea-9a23-7be866482113.jpg)

---
* ### Blood Cells annotation/classification via context menu

![contextmenu](https://user-images.githubusercontent.com/7229266/71325626-58b95980-24a4-11ea-9e6b-da9d20ad49d6.jpg)

---
* ### Clinically significant blood cell morphology documentation
![morph](https://user-images.githubusercontent.com/7229266/71325638-81d9ea00-24a4-11ea-93e0-dc63e4d55868.jpg)

---
* ### Final report for Doctors/Providers
![final](https://user-images.githubusercontent.com/7229266/71325648-8ef6d900-24a4-11ea-8540-070d38f193e8.jpg)


**Author:**
---
Sukra Bhandari
