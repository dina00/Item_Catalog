from flask import (
    Flask, render_template, request, redirect, url_for, jsonify, flash)
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items, Users
from flask import session as login_session
import random
import string
import os
import json

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests


app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# Configuration
# Fill in the variables with your client id
# and client secret provided by google
GOOGLE_CLIENT_ID = '''CLIENT_ID.apps.googleusercontent.com'''
GOOGLE_CLIENT_SECRET = 'CLIENT_SECRET'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Json pages
@app.route('/catalog/JSON')
def catalogJSON():
    catalog = session.query(Categories).all()
    return jsonify(catalog=[c.serialize for c in catalog])


@app.route('/catalog/<int:cat_id>/JSON')
def ItemsJSON(cat_id):
    category = session.query(Categories).filter_by(id=cat_id).one()
    items = session.query(Items).filter_by(cat_id=cat_id).all()
    return jsonify(items=[i.serialize for i in items])


# Flask-Login helper to retrieve a user from the Users db.
@login_manager.user_loader
def load_user(user_id):
    user = session.query(Users).filter_by(id=user_id).first()
    if user:
        return user
    return None

# The next part is concerned with signing in the user through Google
# DISCLAIMER: Sorces of the code related to this funtionality are the Google dev website and Real python Google sign in tutorial.
# https://realpython.com/flask-google-login/
# https://developers.google.com/identity/sign-in/web/sign-in
# -------------------------------------------------------------------------------------------------------


@app.route('/login')
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes to retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
# things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Find out what URL to hit to get tokens that allow you to ask for
# things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
# Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

# Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))
# After getting the tokens find and hit the URL
# from Google that gives the user's profile information,
# including their Google profile image and email.
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
# To make sure the user's email is verified,
# the user needs to be authenticated with Google,
# verify their email through Google.
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    # Create a user in your db with the information provided
    # by Google.
    user = Users(
        id=unique_id, name=users_name, email=users_email, picture=picture
    )

# If user doesn't exist, add it to the database.
    if not session.query(Users).filter_by(id=unique_id).scalar():
        user = Users(id=unique_id, name=users_name,
                     email=users_email, picture=picture)
        session.add(user)
        session.commit()

# Begin user session by logging the user in
    login_user(user)

# Send user back to the homepage.
    return redirect(url_for("catalog"))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('catalog'))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

# ----------------------------------------------------------------------------------------------------------
# Helper functions


def createUser(login_session):
    newUser = Users(id=login_session['id'], name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None

# -------------------------------------------------------------------------------------------------------
# This part is for linking urls with the website's pages, i.e routing.


# The homepage
@app.route('/')
@app.route('/catalog/')
def catalog():
    categories = session.query(Categories).all()
    if current_user.is_authenticated:
        return render_template('catalog_signedin.html', categories=categories)

    else:
        return render_template('catalog.html', categories=categories)

# Display items in a category
@app.route('/catalog/<int:cat_id>/')
def category(cat_id):
    category = session.query(Categories).filter_by(id=cat_id).one()
    items = session.query(Items).filter_by(cat_id=cat_id).all()
    return render_template('items.html', cat_id=cat_id, items=items,
                           category=category)

# Add a new item in a category
@app.route('/catalog/<int:cat_id>/new/', methods=['GET', 'POST'])
def addnewItem(cat_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    if request.method == 'POST':
        newItem = Items(
            name=request.form['name'],
            description=request.form['description'], cat_id=cat_id,
            user_id=current_user.get_id())
        session.add(newItem)
        session.commit()
        flash('The item has been successfully added.')
        return redirect(url_for('catalog'))
    else:
        return render_template('newitem.html', cat_id=cat_id)

# Edit an item
@app.route('/catalog/<int:cat_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(cat_id, item_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    editedItem = session.query(Items).filter_by(id=item_id).first()


    if current_user.get_id() != editedItem.user_id:
        flash('Not Authorized')
        return redirect(url_for('catalog'))

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']

        session.add(editedItem)
        session.commit()
        flash('The item has been successfully edited.')
        return redirect(url_for('catalog'))
    else:

        return render_template(
            'edititem.html', cat_id=cat_id, item_id=item_id, item=editedItem)

# Delete an item
@app.route('/catalog/<int:cat_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(cat_id, item_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    itemToDelete = session.query(Items).filter_by(id=item_id).first()
    if current_user.get_id() != itemToDelete.user_id:
        flash('Not Authorized')
        return redirect(url_for('catalog'))

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('The item has been successfully deleted.')
        return redirect(url_for('catalog'))
    else:
        return render_template('deleteitem.html', item=itemToDelete)

# -----------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(host='0.0.0.0', port=8000)
