from .database import db
from datetime import datetime

CURRENT_TIMESTAMP =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    login_date = db.Column(db.String, default=CURRENT_TIMESTAMP)
    playtime= db.Column(db.String, default=0)
    pwd = db.Column(db.String, nullable=False, unique=True)
    status = db.Column(db.Integer, nullable=False, default=1)

class Creator(db.Model):
    __tablename__ = 'Creator'
    cr_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    date = db.Column(db.String, default= CURRENT_TIMESTAMP)
    followers = db.Column(db.Integer, default=0)
    rating= db.Column(db.Numeric, default= -1)
    user_id = db.Column(db.Integer,   db.ForeignKey("User.user_id"), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)

class Admin(db.Model):
    __tablename__ = 'Admin'
    admin_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name= db.Column(db.Integer, nullable=False)
    admin_pwd= db.Column(db.String, nullable=False, unique=True)
    date= db.Column(db.String, default=CURRENT_TIMESTAMP)

class Song(db.Model):
    __tablename__ = 'Song'
    song_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genre= db.Column(db.String, nullable=False)
    Rating= db.Column(db.Numeric, default=0)
    play_time= db.Column(db.Integer, nullable=False, default=0)
    duration= db.Column(db.Numeric, nullable=False)
    date= db.Column(db.String, default= CURRENT_TIMESTAMP)
    cr_id = db.Column(db.Integer, db.ForeignKey("Creator.cr_id"), primary_key=True, nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey("Album.album_id"), primary_key=True, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)

class Album(db.Model):
    __tablename__= 'Album'
    album_id= db.Column(db.Integer, autoincrement=True, primary_key=True)
    name= db.Column(db.String, nullable=False)
    date= db.Column(db.String, nullable=False, default= CURRENT_TIMESTAMP)
    likes= db.Column(db.Integer, default=0)
    song_qty = db.Column(db.Integer, default=0)
    cr_id = db.Column(db.Integer, db.ForeignKey("Creator.cr_id"), primary_key=True, nullable=False)
    songs = db.relationship("Song")
    status = db.Column(db.Integer, nullable=False, default=1)

class Playlist(db.Model):
    __tablename__= 'Playlist'
    pl_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name= db.Column(db.String, nullable=False)
    date= db.Column(db.String, default= CURRENT_TIMESTAMP)
    qty= db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer,   db.ForeignKey("User.user_id"), primary_key=True, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)

class PlaylistRelation(db.Model):
    __tablename__= 'PlaylistRelation'
    pr_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pl_id= db.Column(db.Integer,   db.ForeignKey("Playlist.pl_id"), primary_key=True, nullable=False)
    song_id = db.Column(db.Integer,   db.ForeignKey("Song.song_id"), primary_key=True, nullable=False)
    user_id = db.Column(db.Integer,   db.ForeignKey("User.user_id"), primary_key=True, nullable=False)
    date= db.Column(db.String, default= CURRENT_TIMESTAMP)

class UserCreatorFollowers(db.Model):
    __tablename__= 'UserCreatorFollowers'
    user_id = db.Column(db.Integer,   db.ForeignKey("User.user_id"), primary_key=True, nullable=False)
    cr_id = db.Column(db.Integer, db.ForeignKey("Creator.cr_id"), primary_key=True, nullable=False)
    date = db.Column(db.String, default= CURRENT_TIMESTAMP)
