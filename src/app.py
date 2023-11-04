#!/usr/local/bin/python3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from forms import LoginForm, RegisterForm, PasswordChangeForm, UserFilterForm
import flask_login
from models import db, login_manager, UserModel, Playlist, Song, load_user
import json
import os
from dotenv import load_dotenv
from random import choice
import openai


app = Flask(__name__)

# Setup environment
load_dotenv()
app.secret_key = os.getenv("FLASK_APP_SECRET_KEY", default=None)
openai.api_key = os.getenv("OPEN_AI_API_KEY", default=None)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///freqy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)
with app.app_context():
    db.create_all()

# Initialize the login manager
login_manager.init_app(app)


def addUser(email, password):
    user = UserModel()
    user.set_password(password)
    user.email = email
    user.username = "A"
    db.session.add(user)
    db.session.commit()


def verify_user_logged_in():
    logged_in = False
    username = None
    if flask_login.current_user.is_authenticated:
        logged_in = True
        username = flask_login.current_user.username
    return logged_in, username


@login_manager.unauthorized_handler
def handle_unauthorized_login_attempt():
    form = LoginForm()
    flash('Please login to access this page', 'alert-danger')
    return render_template('login.html',form=form)


def valid_form(method, form):
    return request.method == "POST" and form.validate_on_submit()


def get_user(current_user):
    return UserModel.query.filter_by(id=current_user.id)


############ ROUTES ###########
@app.route('/', methods=['GET'])
def home():
    # logged_in, username = verify_user_logged_in()
    # return render_template('home.html', logged_in=logged_in, username=username)
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(formdata=None)
    if valid_form(request, form):
        user = UserModel.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid login. Please enter valid login credentials.', 'alert-danger')
            return render_template('login.html',form=form)
        flask_login.login_user(user)
        session['email'] = form.email.data
        return redirect(url_for('my_playlists'))
    else:
        # flash('Please enter a valid email and password', 'alert-danger')
        return render_template('login.html',form=form)
    

@app.route('/logout', methods=['GET', 'POST'])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    session.pop('email', None)
    return redirect(url_for('home'))


@app.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    logged_in, username = verify_user_logged_in()
    if logged_in:
        user = UserModel.query.filter_by(username=flask_login.current_user.username).first()
        user = get_user(flask_login.current_user)
        flash('You have already signed up for an acount.', 'alert-danger')
        return redirect(url_for('home'))
    form = RegisterForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            if form.password.data != form.confirmPassword.data:
                flash('Passwords do not match', 'alert-danger')
            else:
                flash('Something went wrong in registration', 'alert-danger')
            return render_template('signup.html',form=form)
        user = UserModel.query.filter_by(email=form.email.data).first()
        if user is None:
            if form.password.data == form.confirmPassword.data:
                addUser(form.email.data, form.password.data)  # Need username validation?
                flash('Registration successful', 'alert-success')
                session['email'] = form.email.data
                user = UserModel.query.filter_by(email=form.email.data).first()
                flask_login.login_user(user)
                return render_template('my-playlists.html', logged_in=logged_in, username=username)  # add "playlists=playlists" - new users will not have playlists yet.
            else:
                flash('Passwords do not match', 'alert-danger')
                return render_template('signup.html',form=form)
        else:
            flash('Email already registered', 'alert-danger')
            return render_template('signup.html',form=form)    
    return render_template('signup.html',form=form, logged_in=logged_in, username=username)


@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    user_filter_form = UserFilterForm()
    users = UserModel.query.all()
    logged_in, username = verify_user_logged_in()
    # Check if the user has searched for an event by title
    if user_filter_form.validate_on_submit():
        filtered_users = []
        for user in users:
            if request.form['query'].lower() in str(user.username).lower():
                filtered_users.append(user)
            users = filtered_users
        return render_template('leaderboard.html', user_filter_form=user_filter_form, users=users, 
                               logged_in=logged_in, username=username)
    return render_template('leaderboard.html', user_filter_form=user_filter_form, users=users, 
                           logged_in=logged_in, username=username)


@app.route('/my-playlists', methods=['GET', 'POST'])
def my_playlists():
    logged_in, username = verify_user_logged_in()
    if logged_in:
        playlists = get_playlists()
        return render_template('my-playlists.html', logged_in=logged_in, username=username, playlists=playlists)
    return redirect(url_for('login'))


@app.route('/change_password', methods=["GET", "POST"])
@flask_login.login_required
def change_password():
    logged_in = True
    username = flask_login.current_user.username
    passwordChangeForm = PasswordChangeForm()
    user = UserModel.query.filter_by(username=username).first()
    if passwordChangeForm.validate_on_submit() and logged_in:
        new_password = request.form['newPassword']
        user.set_password(new_password)
        db.session.commit()
        return redirect(url_for('reminders'))
    return render_template('change_password.html', passwordChangeForm=passwordChangeForm, 
                           logged_in=logged_in, username=username)


########## API Routes #############
####### Playlist Routes ###########
@app.route('/api/playlists', methods=['GET'])
def get_playlists():
    """
    Retrieves all playlists stored in the playlists db table.
    """
    return {
        "playlists": [
            {
                "playlist_id": "0001",
                "playlist_name": "Energetic Classic Rock",
                "songs": [
                        {
                            "song_id": "0000001",
                            "artist": "Led Zeppelin",
                            "title": "Stairway to Heaven",
                        },
                        {
                            "song_id": "0000002",
                            "artist": "Credence Clearwater Revival",
                            "title": "Fortunate Son",
                        },
                ],
            }
        ],
    }


@app.route('/api/playlists', methods=['POST'])
def create_playlist(mood=None, name=None):
    moods = ['happy', 'sad', 'anxious', 'energetic', 'calm']
    if not mood:
        mood = choice(moods)

    # ask gpt for some songs to match the mood
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Your job is to help a user create music playlists of songs based on a user's mood."},
            {"role": "user", "content": f"Can you create a playlist of 10 songs that fit the mood of {mood}? "}
        ]
    )


    if not name:
        # ask gpt to create a playlist name based on the songs
        pass


@app.route('/api/playlists/:id', methods=['GET'])
def get_playlist_by_id():
    pass


@app.route('/api/playlists/:id', methods=['PUT'])
def update_playlist_by_id(playlist_id):
    pass


@app.route('/api/playlists/:id', methods=['DELETE'])
def delete_playlist_by_id(playlist_id):
    pass


######## Song Routes ###########
@app.route('/api/playlists/:id/songs', methods=['GET'])
def get_songs_in_playlist():
    """
    Retrieves all songs in a specific playlist.
    """
    pass


@app.route('/api/playlists/:id/songs', methods=['POST'])
def add_song_to_playlist():
    """
    Adds a song to a specific playlist.
    """
    pass


@app.route('/api/playlists/:id/songs/:song_id', methods=['GET'])
def get_song_in_playlist():
    """
    Retrieves a single song in a specific playlist.
    """
    pass


@app.route('/api/playlists/:id/songs/:song_id', methods=['PUT'])
def update_song_in_playlist():
    """
    Updates a song's title and/or artist in a specific playlist.
    """
    pass


@app.route('/api/playlists/:id/songs/:song_id', methods=['DELETE'])
def delete_song_in_playlist():
    """
    Deletes a song from a specific playlist.
    """
    pass


######## Utility Routes ###########
@app.route('/api/generate_playlist_name', methods=['POST'])
def generate_playlist_name():
    """
    Uses OpenAI API to generate a playlist name based on a user's mood.
    """
    pass


####### ERROR PAGES ###########
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    # Default flask port (5000) is used in newer macOS releases for sharing features.
    app.run(host='0.0.0.0', debug='false', port=5001)  
