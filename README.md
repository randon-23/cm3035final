# cm3035final
ADW - eLearning
# NOTE: all shell commands are displayed as follows: ###command###

# Prerequisites:
Development was done on Windows 11 OS
Python 3.11 isntalled
Node.js installed
Windows Subsystem for Linux (WSL) for Redis set up (This was done by installing Ubuntu for Windows from Microsoft Store)

# Python/Django setup
Create a virtual environment to isolate all the project dependencies which are going to be installed
Once the virtual environment is set up using the command ###python -m venv your_venv_name###. To activate
virtual environment on Windows, use the command ###.\your_venv_name\Scripts\Activate.ps1. All project dependencies
will be installed from the requirements.txt file via the command ###pip install -r requirements.txt###.

# Node.js setup
Independently of the Python environment, ensure Node.js and npm(Node Package Manager) are installed. Once Node.js installed, 
running the command ###npm install### will install all node dependenceies/modules associated with Tailwind (frontend framework used)

# Redis setup for Windows (using WSL for Redis server)
To install redis on the newly installed Ubuntu for Windows, the redis-server is installed within the Linux distribution.
First run command ###sudo apt udpate###, then ###apt list --upgradable###, and then ###sudo apt upgrade###. Once all default
packages are installed and updated in the Linux distribution, then redis-server is installed by running the
command ###sudo apt install redis-server###. Once the server is installed, the redis-server is started by running the
command ###sudo service redis-server start###. To ensure the service is running, the command ###redis-cli ping### should
return PONG. To ensure Redis starts automatically with the WSL Linux distribution instance, pass the
command ###sudo systemctl enable redis-server.service###

# Migrations and database set up
The project requirements stipulate the need for teacher and students accounts set up in the SQLite3 database. If this
was not the case, the .sqlite3 file won't be included in the submission and a new .sqlite3 file will be created by
running the command ###python manage.py migrate### which would run the migrations. However, given this is not the case
the command only needs to be run just in case, and account credentials will be included in the report. Admin credentials
would also need to be set up using ###python manage.py createsuperuser### if no .sqlite3 is set up, but once again,
this is not the case with this submission

# Running the server
Use the command ###python manage.py runserver### to start up the server. This will start a development server which serves
the Django project along with an ASGI Daphne routing implementation for websocket functionality.

# Running celery app
In addition to the django server currently running. We also need to run the messaging/queueing service 'Celery'. This can
be done by activating a Celery worker in a seperate terminal to handle the background tasks via the following 
command ###celery --app=elearning.celery:app worker --loglevel=INFO --pool=solo###