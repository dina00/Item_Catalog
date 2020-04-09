# Item Catalog
## Intro

This is a simple website built using **Python-Flask framework** in the back-end and **HTML** and **CSS** in the front-end. It displays the items in the database, allows editing and adding of items of signed in users. Users are signed in using OAuth and Google Sign-In.


## What you need beforehand

- Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads), [Vagrant](https://www.vagrantup.com/downloads.html) and [Git](https://git-scm.com/downloads).
- Follow the instructions on this [link](https://github.com/udacity/fullstack-nanodegree-vm) to get your Vagrant virtual enviroment up and running. 
- Install [Flask](https://pypi.org/project/Flask/).
- Install [requests](https://pypi.org/project/requests/).
- Install [oauthlib](https://pypi.org/project/oauthlib/).
- Install [Flask-Login](https://pypi.org/project/Flask-Login/).
- Install [pyOpenSSL](https://www.pyopenssl.org/en/stable/install.html).
- Download the files in this repo to the catalog folder in the vagrant folder.
- You need a Google Client ID and Secret Client ID for the Google sign to work, configure the project from [here](https://developers.google.com/identity/sign-in/web/sign-in). 


## Instructions

1. To run this project ```cd``` into the ```vagrant``` directory then ```cd``` into the ```catalog``` directory.
2. Fill out the Client ID and Secret Client ID in the ```application.py``` , ```catalog.html```, and ```login.html```.
3. Run the files in this order: ```python database_setup.py```, ```python load_database_data.py```, ```python application.py```.
4. Type [http://localhost:8000/](http://localhost:8000/) into your browser.


## JSON endpoints

- Returns the categories in the catalog.
```/catalog/JSON```
- Returns the JSON of an item.
```/catalog/<int:cat_id>/JSON```

######  DISCLAIMER: Sources of the code related to the Google sign in funtionality are the Google dev website and Real python Google sign in tutorial.
- [https://realpython.com/flask-google-login/](https://realpython.com/flask-google-login/).
- [https://developers.google.com/identity/sign-in/web/sign-in](https://developers.google.com/identity/sign-in/web/sign-in).

