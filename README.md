# E-Wallet

# Relate to Exercise 1
#### FLASK RESTX BOILER-PLATE WITH JWT

### Require environments
Python 3.10.3
PostgreSQL

### Terminal commands
Note: make sure you have `pip` and `virtualenv` installed.

    > python3 -m venv env

    > source env/bin/activate

    > pip install -r requirements.txt

Make sure to run the initial migration commands to update the database.
    
    > flask db init

    > flask db migrate

    > flask db upgrade

Run the application:

    > flask run

### Viewing the app ###

    Open the following url on your browser to view swagger documentation
    http://127.0.0.1:5000/


### Using Postman ####

    Authorization header is in the following format:

    Key: Authorization
    Value: "token_generated_during_login"

    For testing authorization, url for getting all user requires an admin token while url for getting a single
    user by public_id requires just a regular authentication.


### Full description and guide ###
https://medium.freecodecamp.org/structuring-a-flask-restplus-web-service-for-production-builds-c2ec676de563


# E-wallet (Exercise 2)
### Terminal commands
Note: make sure you have `pip` and `virtualenv` installed.

    > python3 -m venv env

    > source env/bin/activate

    > pip install -r requirements.txt

Run the application:

    > python3 main.py

### Viewing the app ###

    You can test these APIs via Postman at the address http://127.0.0.1:8000/

### Note: Make sure you run both applications in order to make them interact with each others.