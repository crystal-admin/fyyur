# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
from unicodedata import name
from webbrowser import get
import psycopg2
import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

# ----------------------------------------------------------------------------#
# Connect to a local postgresql database
# ----------------------------------------------------------------------------#

app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String, nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    shows = db.relationship("Show", backref="venues", lazy=False, cascade="all, delete-orphan")

    # def __repr__(self):
    #     return f"<Venue id={self.id} name={self.name} city={self.city} state={self.city}> \n"


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    shows = db.relationship("Show", backref="artists", lazy=False, cascade="all, delete-orphan")


class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # def __repr__(self):
    #     return f"<Show id={self.id} artist_id={self.artist_id} venue_id={self.venue_id} start_time={self.start_time}"
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    #   data=[{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #       "id": 1,
    #       "name": "The Musical Hop",
    #       "num_upcoming_shows": 0,
    #     }, {
    #       "id": 3,
    #       "name": "Park Square Live Music & Coffee",
    #       "num_upcoming_shows": 1,
    #     }]
    #   }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #       "id": 2,
    #       "name": "The Dueling Pianos Bar",
    #       "num_upcoming_shows": 0,
    #     }]
    #   }]
            
    # data Array
    data = []
    results = Venue.query.distinct(Venue.city, Venue.state).all()
        
    # loop through the results
    for result in results:
        city_state_unit_record = {
                "city": result.city,
                "state": result.state
        }
        venues = Venue.query.filter_by(city=result.city, state=result.state).all()
            
        # loop to format each venue
        all_formatted_venues = []
        for venue in venues:
            all_formatted_venues.append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
            })
            
        # add the venues to the city state unit record object    
        city_state_unit_record["venues"] = all_formatted_venues
        data.append(city_state_unit_record)
                 
        return render_template('pages/venues.html', areas=data)
    

@app.route('/venues/search', methods=['POST'])
def search_venues():
 
    #   response={
    #     "count": 1,
    #     "data": [{
    #       "id": 2,
    #       "name": "The Dueling Pianos Bar",
    #       "num_upcoming_shows": 0,
    #     }]
    #   }

    # get the search term from the request
    search_term = request.form.get("search_term", "")
  
    # response object
    response = {}
  
    all_venues = list(Venue.query.filter(
        Venue.name.ilike(f"%{search_term}%") |
        Venue.state.ilike(f"%{search_term}%") |
        Venue.city.ilike(f"%{search_term}%") 
    ).all())
    response["count"] = len(all_venues)
  
    # empty array to hold each venue data
    response["data"] = []
  
    # looping through the venues data
    for venue in all_venues:
        venue_record = {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
        }
        # add the venue_record data to the response
        response["data"].append(venue_record)
       
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
    #   data1={
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #       "artist_id": 4,
    #       "artist_name": "Guns N Petals",
    #       "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #       "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    #   }
    #   data2={
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    #   }
    #   data3={
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #       "artist_id": 5,
    #       "artist_name": "Matt Quevedo",
    #       "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #       "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #       "artist_id": 6,
    #       "artist_name": "The Wild Sax Band",
    #       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #       "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #       "artist_id": 6,
    #       "artist_name": "The Wild Sax Band",
    #       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #       "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #       "artist_id": 6,
    #       "artist_name": "The Wild Sax Band",
    #       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #       "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    #   }

    # get the venue details using it's id
    data = Venue.query.get(venue_id)
  
    # get the venue genres
    # convert the venue data object to an array seperated by comma
    setattr(data, "genres", data.genres.split(","))
  
    # retrieve past shows
    get_past_shows = list(filter(lambda show: show.start_time < datetime.now(), data.shows))
  
    past_shows_buffer = []
    for show in get_past_shows:
        past_shows = {}
        past_shows["artist_name"] = show.artists.name
        past_shows["artist_id"] = show.artists.id
        past_shows["artist_image_link"] = show.artists.image_link
        past_shows["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        past_shows_buffer.append(past_shows)
      
    # sets the attribute of the past_shows property of data object to formatted object. 
    setattr(data, "past_shows", past_shows_buffer)
    setattr(data, "past_shows_count", len(get_past_shows))
      
    # retrieve all future shows
    get_future_shows = list(filter(lambda show: show.start_time > datetime.now(), data.shows))
    future_shows_buffer = []
    future_shows = {}
    for show in get_future_shows:
        future_shows["artist_name"] = show.artists.name
        future_shows["artist_id"] = show.artists.id
        future_shows["artist_image_link"] = show.artists.image_link
        future_shows["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        future_shows_buffer.append(future_shows)
      
    setattr(data, "upcoming_shows", future_shows)    
    setattr(data,"upcoming_shows_count", len(future_shows_buffer))
  
#   data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
    # get the form data
    form = VenueForm(request.form)

    # check form data validity
    if form.validate():
        try: 
            new_venue_record = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                # converting array to string separated by commas
                genres=",".join(form.genres.data), 
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data, 
                website=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
               
            )

            # handling transaction
            db.session.add(new_venue_record)
            db.session.commit()

            # flashing a message on successful creation of a new venue record
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')

        except Exception:
            # rollback to initial database state on unsuccessful insertion
            db.session.rollback()
            print(sys.exc_info())

            # flash an error message
            flash('An error occurred. Venue ' + data.name + ' could not be listed.')

        finally:
            # close the database transaction 
            db.session.close()
    
    # handles form data validity errors
    else:
        print("\n", form.errors)
        # flash the same error message 
        flash('An error occurred. Venue ' + data.name + ' could not be listed.')

    # return to home page after successful creation
    return render_template('pages/home.html')


# DELETE A VENUE
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        # get venue to delete using it's id
        venue = Venue.query.get(venue_id) 
        db.session.delete(venue)
        db.session.commit()
        
        # on successful delete flash a message
        flash("Venue " + venue.name + " was successfully deleted !")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Venue was not successfully deleted.")
    finally:
        db.session.close()

    # redirect to home 
    return redirect(url_for("index"))



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    #   data=[{
    #     "id": 4,
    #     "name": "Guns N Petals",
    #   }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #   }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #   }]

    data = db.session.query(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)



@app.route('/artists/search', methods=['POST'])
def search_artists():
  
    #   response={
    #     "count": 1,
    #     "data": [{
    #       "id": 4,
    #       "name": "Guns N Petals",
    #       "num_upcoming_shows": 0,
    #     }]
    #   }

    # get the search value from the request
    search_term = request.form.get('search_term', '')
    
    all_artists = Artist.query.filter(
        Artist.name.ilike(f"%{search_term}%") |
        Artist.city.ilike(f"%{search_term}%") |
        Artist.state.ilike(f"%{search_term}%")
    ).all()
    
    # response object 
    response = {
        "count": len(all_artists),
        "data": []
    }

    for artist in all_artists:
        artist_record = {}
        artist_record["name"] = artist.name
        artist_record["id"] = artist.id

        # initialize upcoming shows to 0
        upcoming_shows = 0
        
        for show in artist.shows:
            if show.start_time > datetime.now():
                # increment the upcoming_shows by 1
                upcoming_shows = upcoming_shows + 1
        artist_record["upcoming_shows"] = upcoming_shows

        response["data"].append(artist_record)
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
 
    #   data1={
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #       "venue_id": 1,
    #       "venue_name": "The Musical Hop",
    #       "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #       "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    #   }
    #   data2={
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #       "venue_id": 3,
    #       "venue_name": "Park Square Live Music & Coffee",
    #       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #       "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    #   }
    #   data3={
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #     "genres": ["Jazz", "Classical"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "432-325-5432",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [{
    #       "venue_id": 3,
    #       "venue_name": "Park Square Live Music & Coffee",
    #       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #       "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #       "venue_id": 3,
    #       "venue_name": "Park Square Live Music & Coffee",
    #       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #       "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #       "venue_id": 3,
    #       "venue_name": "Park Square Live Music & Coffee",
    #       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #       "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 3,
    #   }
    #   data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]

    # get a particular artist by id
    data = Artist.query.get(artist_id)
    setattr(data, "genres", data.genres.split(","))
  
    # retrieves artist past shows
    get_past_shows = list(filter(lambda show: show.start_time < datetime.now(), data.shows))
    past_shows_buffer = []
    for show in get_past_shows:
        past_show = {}
        past_show["venue_name"] = show.venues.name
        past_show["venue_id"] = show.venues.id
        past_show["venue_image_link"] = show.venues.image_link
        past_show["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

        past_shows_buffer.append(past_show)

        # update the past_shows and past_shows_count attributes with formatted data
        setattr(data, "past_shows", past_shows_buffer)
        setattr(data, "past_shows_count", len(get_past_shows))
      
      
        # retrieve the upcoming shows
        get_upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), data.shows))
        upcoming_shows_buffer = []
        for show in get_upcoming_shows:
            upcoming_shows = {}
            upcoming_shows["venue_name"] = show.venues.name
            upcoming_shows["venue_id"] = show.venues.id
            upcoming_shows["venue_image_link"] = show.venues.image_link
            upcoming_shows["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

            upcoming_shows_buffer.append(upcoming_shows)
          
        setattr(data, "upcoming_shows", upcoming_shows_buffer)
        setattr(data, "upcoming_shows_count", len(get_upcoming_shows))

        return render_template('pages/show_artist.html', artist=data)
 
 
 
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
    #   artist={
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    #   }
  artist = Artist.query.get(artist_id)
  form.genres.data = artist.genres.split(",") 
  return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  # get an instance of the Artist form with it's data
  form = ArtistForm(request.form)
  
  if form.validate():
        try:
            artist = Artist.query.get(artist_id)
            artist.name = form.name.data
            artist.city=form.city.data
            artist.state=form.state.data
            artist.phone=form.phone.data
            artist.genres=",".join(form.genres.data)
            artist.image_link=form.image_link.data
            artist.facebook_link=form.facebook_link.data
            artist.website_link=form.website_link.data
            artist.seeking_venue=form.seeking_venue.data
            artist.seeking_description=form.seeking_description.data
            
            #stage and save updated Artist data
            db.session.add(artist)
            db.session.commit()
            
            #flash a message on successful artist update
            flash("Artist " + artist.name + " was successfully edited!")
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash("Artist was not edited successfully.")
        finally:
            db.session.close()
  else:
        print("\n\n", form.errors)
        flash("Artist was not edited successfully.")
  return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
    #   venue={
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    #   }
    
  # query the venue model with a given venue id
  venue = Venue.query.get(venue_id)
  
  # split the genres data in contained in the form
  form.genres.data = venue.genres.split(",") 
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)



@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
 
    # retrieve the form data from request
    form = VenueForm(request.form)
    
    # checks for form validity
    if form.validate():
        try:
            venue = Venue.query.get(venue_id) #get the value of the venue by venue id

            venue.name = form.name.data
            venue.city=form.city.data
            venue.state=form.state.data
            venue.address=form.address.data
            venue.phone=form.phone.data
            venue.genres=",".join(form.genres.data)
            venue.image_link=form.image_link.data
            venue.facebook_link=form.facebook_link.data
            venue.website_link=form.website_link.data
            venue.seeking_talent=form.seeking_talent.data
            venue.seeking_description=form.seeking_description.data
            
            # stage changes and save using SQLAlchemy Transaction API
            db.session.add(venue)
            db.session.commit()

            # on successful edit, flash a success message
            flash("Venue " + form.name.data + " edited successfully")
            
        except Exception:
            db.session.rollback() #on unsuccessful edit, rollback changes
            print(sys.exc_info())
            flash("An error occurred Venue was not edited successfully.")
        finally:
            db.session.close()
    else: 
        print("\n", form.errors)
        flash("An error occurred Venue was not edited successfully.")
    return redirect(url_for('show_venue', venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    form = ArtistForm(request.form)
  
    # checks form validation
    if form.validate():
        try: 
            new_artist_record = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                # converting array to string separated by commas
                genres=",".join(form.genres.data),  
                facebook_link=form.facebook_link.data,
                website=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
            )
           
            # handle database transaction 
            db.session.add(new_artist_record)
            db.session.commit() 
            
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!') 
            
        except Exception:
            
            db.session.rollback()
            flash('An error occurred. Artist ' + data.name + ' could not be listed.')
            
        finally:
            db.session.close()
    else:
        # if there is a validation error, flash a message
        print(form.errors)
        flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        
    #render the home page
    return render_template('pages/home.html')



#DELETE ARTIST
@app.route("/artists/<artist_id>/delete", methods=["GET"])
def delete_artist(artist_id):
    try:
        #get the Artist to delete by id
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
        #on successful delete, flash a message
        flash("Artist " + artist.name+ " was successfully deleted !")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Artist was not successfully deleted .")
    finally:
        db.session.close()

    return redirect(url_for("index"))



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    
    #   data=[{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    #   }]

  # data array
  data = []
  
  # query data from the show model
  shows = Show.query.all()
  for show in shows:
      temp = {}
      temp["venue_id"] = show.venues.id
      temp["venue_name"] = show.venues.name
      temp["artist_id"] = show.artists.id
      temp["artist_name"] = show.artists.name
      temp["artist_image_link"] = show.artists.image_link
      temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      
      data.append(temp)
      
  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # get the show form data from request
  form = ShowForm(request.form)
  
  # checking show form data validation
  if form.validate():
        try:
          new_show_record = Show(
               artist_id=form.artist_id.data,
               venue_id=form.venue_id.data,
               start_time=form.start_time.data
          )
          
          # handle database transactions
          db.session.add(new_show_record)
          db.session.commit()
          
          # on successful db insert, flash success
          flash('Show was successfully listed!')
        except Exception:
            db.session.add(new_show_record)
            print(sys.exc_info())
            flash('An error occurred. Show could not be listed.')
        finally:
            db.session.close()
  else:
        db.session.close()
        flash('An error occurred. Show could not be listed.')

  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''