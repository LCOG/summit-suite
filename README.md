# Summit Suite Backend Readme

## License

This project is licensed under the [Elastic License 2.0](https://www.elastic.co/licensing/elastic-license).

You are free to use, modify, and distribute this software. You may **not** provide 
it to third parties as a hosted or managed service. That right is reserved exclusively 
to Lane Council of Governments (LCOG).

Python 3.12.2 

# Run the backend locally
# MacOS
`source ../env/bin/activate && ./manage.py runserver`
# Windows
`..\env_20230705\Scripts\activate; .\manage.py runserver`

# Setting up the backend for the first time
1) Ensure that .env file is in place (in OneDrive). Ensure settings are such that sqlite db is used
2) Create a python virtualenv
MacOS 
  Ensure pyenv is installed `brew install pyenv`
  Install latest python version `pyenv install 3.13.9`
  Create virtualenv `~/.pyenv/versions/3.12.2/bin/python -m venv env_20240412`
Windows `python -m venv env_20230705`
3) Activate virtualenv
MacOS `source ./env/bin/activate`
Windows `.\env_20230705\Scripts\activate`
4) Install requirements
MacOS `pip install -r ./code/requirements.txt`
Windows `python -m pip install -r .\code\requirements-windows.txt`
5) Run migrations
MacOS `./manage.py migrate`
Windows `python .\manage.py migrate`
6) Create a superuser
MacOS `./manage.py createsuperuser --username=USERNAME`
Windows `python .\manage.py createsuperuser --username=USERNAME`
7) Run commands to import employees and reviews from Caselle
8) Add settings_local.py file from an existing install
9) Run the backend locally
MacOS `./manage.py runserver`
Windows `python .\manage.py runserver`

# Install Elastic Beanstalk CLI
https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html
Manually install the CLI using pip. Modify environment variable PATH from instructions.

## New submissions API (mileage reimbursement)

The backend now includes a reusable submissions domain with mileage reimbursement as its first hard-coded form type.

Primary endpoints:
- `GET /api/v1/submission` - list submissions visible to the current user
- `GET /api/v1/mileage-submission` - list mileage submissions
- `POST /api/v1/mileage-submission` - create a mileage submission with rows
- `PUT /api/v1/mileage-submission/<pk>/approve` - approve a submitted mileage request
- `GET /api/v1/submission-role` - list configurable approval roles for the current organization
