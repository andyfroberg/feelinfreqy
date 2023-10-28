# from flask_login import UserMixin, LoginManager
import flask_login
# from werkzeug.security import generate_password_hash, check_password_hash
import werkzeug.security
from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime, timedelta


db = SQLAlchemy()
login_manager = flask_login.LoginManager()


class UserModel(flask_login.UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = werkzeug.security.generate_password_hash(password)
    
    def check_password(self, password):
        return werkzeug.security.check_password_hash(self.password_hash, password)
    
    def __repr__(self):  # Add repr, str, etc. dunders for all classes?
        return f'user_id_{self.id}'


class Playlist(flask_login.UserMixin, db.Model):
    playlist_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    playlist_name = db.Column(db.String(128), nullable=False)
    playlist_mood = db.Column(db.String(128), nullable=False)
    songs = db.relationship('Song', backref='playlist')


class Song(flask_login.UserMixin, db.Model):
    song_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    song_title = db.Column(db.String(128), nullable=False)
    song_artist = db.Column(db.String(128), nullable=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.playlist_id'))



@login_manager.user_loader
def load_user(id):
    return UserModel.query.get(int(id))