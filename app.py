#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from flask_migrate import Migrate
from config import *
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')
  
app.jinja_env.filters['datetime'] = format_datetime
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#----------------------------------------------------------------------------#
@app.route('/venues')
def venues():
  query = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  data = []
  cities = []
  for venue in query :
    if venue.city not in cities:
      city_venues = Venue.query.filter_by(city=venue.city).all()
      venues = []
      city = {
      'city': venue.city,
      'state': venue.state,
      'venues': city_venues
      }
      data.append(city)

  return render_template('pages/venues.html', areas=data)
#--------------------------------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  data = []
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  for venue in venues:
    data.append ({
      "id": venue.id,
      "name": venue.name,
    })

  response = {
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#---------REQUIRED------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  past_shows = []
  upcoming_shows = []
  venue_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id)

  for show in venue_shows:
    artist_id = show.artist_id
    artist = Artist.query.get(show.artist_id)
    if datetime.now() > show.start_time:
      past_shows.append({
        "artist_id": artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
    else:
      upcoming_shows.append({
        "artist_id": artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })  
  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)

  data = {
    "id": venue.id,
    "name": venue.name,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "genres": venue.genres,
    "website": venue.website,
    "image_link": venue.image_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "past_shows": past_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows": upcoming_shows,
    "upcoming_shows_count": upcoming_shows_count
  }
  return render_template('pages/show_artist.html', artist=data)
#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    venue = Venue()
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')  
    venue.website = request.form.get('website')  
    venue.seeking_talent = request.form.get('seeking_talent')  
    venue.seeking_description = request.form.get('seeking_description')  
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be deleted!')
  else:
    flash('Venue was successfully deleted.')
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  data = []
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  for artist in artists:
    data.append ({
      "id": artist.id,
      "name": artist.name,
    })

  response = {
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  past_shows = []
  upcoming_shows = []
  artist_shows = artist.shows
  for show in artist_shows:
    venue_id = show.venue_id
    venue = Venue.query.get(show.venue_id)

    if datetime.now() > show.start_time:
      past_shows.append({
        "venue_id": venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
    else:
      upcoming_shows.append({
        "venue_id": venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)

  data = {
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "genres": artist.genres,
    "website": artist.website,
    "image_link": artist.image_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "past_shows": past_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows": upcoming_shows,
    "upcoming_shows_count": upcoming_shows_count
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('website') 
    artist.seeking_venue = request.form.get('seeking_venue')   
    artist.seeking_description = request.form.get('seeking_description')    
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. not successfully updated')
    else:
      flash('Successfully Updated')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False  
  try: 
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website = request.form.get('website')
    venue.seeking_talent = request.form.get('seeking_talent')
    venue.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      flash('An error occurred. not successfully updated')
    else:
      flash('Successfully Updated')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)
  
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    artist = Artist()
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('website')
    artist.seeking_venue = request.form.get('seeking_venue')
    artist.seeking_description = request.form.get('seeking_description')
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  shows = Show.query.all()
  shows_data = []
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    shows_data.append ({
      'artist_id': artist.id,
      'venue_id': venue.id,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      'artist_name': artist.name,
      'venue_name': venue.name,
      'artist_image_link': artist.image_link  
    })
  return render_template('pages/shows.html', shows=shows_data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    show = Show()
    show.artist_id = request.form.get('artist_id')
    show.venue_id = request.form.get('venue_id')
    show.start_time = request.form.get('start_time')
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')
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
