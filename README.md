# Wire Form 
> Intial setup of a form built with the Django Framework


## Requirements  (Prerequisites)
Tools and packages required to successfully install this project.

* Python 3.8 and up you can it by running the following

`sudo add-apt-repository ppa:deadsnakes/ppa`
`sudo apt-get update`
`sudo apt-get install python3.8`
`sudo apt-get install pip`

## Installation and running the application

* Clone the application from Gitlab by entering the command below in your terminal
`git clone https://github.com/Rob-Tru-Treasury-Org/Truwires.git`

* create a virtual enviroment isolated for this application by entering 
	`$ python3 -m venv env`

	You may need to install venv package with the command
		`sudo apt install python3-venv`
	if issues installing, try upgrading ubuntu
		`sudo apt update`
		`sudo apt upgrade`

* now you should see a new `env` folder in the same directory that contains the cloned repo

* activate your isolated virtual enviroment with command
	`source env/bin/activate`


---
### Setup Database

open a new terminal window, and run
`$ sudo apt-get install postgresql`

navigate to your root directory with
`$ cd /`
navigate to the following folder
`$ cd etc/postgresql/14/main `
and edit the following file with command
`$ sudo nano pg_hba.conf`

replace value "peer" with "trust" in the first uncommented line, under `#Database Administrative login by Unix domain socket`

then, ctrl-s to save and ctrl-x exit

Now start postgres, or restart if it was already running
`$ sudo service postgresql start`

login to postgres
`$ psql -U postgres`

run SQL queries below to create DB
```bash
CREATE DATABASE wireformdb;

ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE wireformdb TO postgres;

ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';
```


logout with `$ \q`

login to the new db with:
`$ psql -U postgres -d wireformdb`
 
then run sql query to add domain data to DB
 ```bash 
 INSERT INTO public.creditunions_creditunion (schema_name, name, phone_number, email, logo, created_on, footer_color, form_color, header_color, buttons_color, allow_international_wires)  
VALUES('main1', 'test', '1234567890', 'test@test.com', 'images/logo.png', '2024-01-03', '#000000', '#000000', '#000000', '#000000', true);  
  
INSERT INTO public.creditunions_domain (folder, is_primary, redirect_to_primary, domain, tenant_id)  
VALUES('', false,false, 'main.localhost', 1);
```


---


You can switch back to the previous terminal or open a new one, just be sure to navigate to the new directory you created and activate your isolated virtual enviroment with the command:
	`$ source env/bin/activate`

cd into the cloned repo `cd truwires`

* Install the Dependecies for this application
	`$ pip install -r requirements.txt`
	
	 may need to install pip
	 `$ sudo apt-get install pip`
	 
	or, may need to install libpq-dev with 
	`$ sudo apt-get install libpq-dev`

* You'll need to get the settings.py file from another dev, and save this file to the wireform folder 

* Enter the command below to start the development server
	`$ python3.8 manage.py migrate`
	`$ python3.8 manage.py runserver`


navigating to "main.localhost:8000" in your browser should display the login page

will need to click signup to create an admin user
username for initial admin user should be 'admin1' 
and enter a valid email address you can access to confirm registration

navigate to "main.localhost:8000/admin" in your browser to access the admin dashboard



## Running after initial setup

After initial setup you'll just need to:

1. start postgres
`$ sudo service postgresql start`

2. navigate to the parent folder `~/tru-wires` of the repo (which should now contain an env folder) and activate your isolated virtual enviroment with the command:
`$ source env/bin/activate`

3. then you can navigate into the repo `$ cd truwires`

4. run the server `$ python3.8 manage.py runserver` (depending on installation, may require `$ python3 manage.py runserver`)

5. and navigate to "main.localhost:8000" in your browser to access the app


## Running Tests
`$ python3 manage.py test` to conduct a generalized Test for the app 


 
