# # ----------------------------------------------------------------------------#
# # Imports
# #
# # ----------------------------------------------------------------------------#

# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate


# app = Flask(__name__)
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)


# class Venue(db.Model):
#     __tablename__ = 'Venue'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     city = db.Column(db.String(120), nullable=False)
#     state = db.Column(db.String(120), nullable=False)
#     address = db.Column(db.String(120), nullable=False)
#     phone = db.Column(db.String(120))
#     genres = db.Column(db.String, nullable=False)
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     website = db.Column(db.String(120))
#     seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
#     seeking_description = db.Column(db.String(500))
#     created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
#     shows = db.relationship("Show", backref="venues", lazy=False, cascade="all, delete-orphan")


# class Artist(db.Model):
#     __tablename__ = 'Artist'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     city = db.Column(db.String(120), nullable=False)
#     state = db.Column(db.String(120), nullable=False)
#     phone = db.Column(db.String(120))
#     genres = db.Column(db.String(120), nullable=False)
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     website = db.Column(db.String(120))
#     seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
#     seeking_description = db.Column(db.String(500))
#     created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
#     shows = db.relationship("Show", backref="artists", lazy=False, cascade="all, delete-orphan")


# class Show(db.Model):
#     __tablename__ = "Show"

#     id = db.Column(db.Integer, primary_key=True)
#     artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
#     venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
#     start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
