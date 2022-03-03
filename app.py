#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import distinct
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import Venue, Artist, Show, db_setup
from sqlalchemy.orm import load_only


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
db = db_setup(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    try:
        current_time = datetime.now()  # .strftime('%Y-%m-%d %H:%S:%M')
        city_state = db.session.query(distinct(Venue.city), Venue.state).all()

        for location in city_state:
            city = location[0]
            state = location[1]

            city_data = {"city": city, "state": state, "venues": []}
            venues = Venue.query.filter_by(city=city, state=state).all()

            for venue in venues:
                upcoming_shows = len(Show.query.filter(Show.venue_id == venue.id).filter(
                    Show.start_time > current_time).all())
                venue_data = {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": upcoming_shows,
                }
                city_data["venues"].append(venue_data)
            data.append(city_data)
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return render_template("pages/home.html")

    finally:
        db.session.close()
        return render_template("pages/venues.html", areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Implements search on venues with partial string search. Case-insensitive.

    search = request.form['search_term']
    venues = Venue.query.filter(Venue.name.ilike(f'%{search}%'))
    venue_list = []
    for venue in venues:
        item = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(Show.query.filter(Show.venue_id == venue.id).filter(
                Show.start_time > datetime.now()).all())
        }
        venue_list.append(item)
    
    response = {
        "count":len(venue_list),
        "data": venue_list
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    data = {}
    try:
        current_time = datetime.now()
        venue = Venue.query.get(venue_id)

        if venue is None:
            return not_found_error(404)

        shows = Show.query.filter(Show.venue_id == venue_id).all()

        upcoming_shows = []
        past_shows = []

        for show in shows:
            artist = Artist.query.get(show.artist_id)
            upcoming_shows_num = len(Show.query.filter(Show.artist_id == artist.id).filter(
                Show.start_time > current_time).all())
            show_data = {
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "num_upcoming_shows": upcoming_shows_num,
                "start_time": str(show.start_time)  # .strftime("%d/%m/%Y, %H:%M")
            }
            if show.start_time > current_time:
                upcoming_shows.append(show_data)
            else:
                past_shows.append(show_data)

 
        data = {"id": venue_id,
                "name": str(venue.name),
                "genres": venue.genres,
                "address": venue.address,
                "city": venue.city,
                "state": venue.state,
                "phone": venue.phone,
                "website": venue.website,
                "facebook_link": venue.facebook_link,
                "seeking_talent": venue.seeking_talent,
                "seeking_description": venue.seeking_description,
                "image_link": venue.image_link,
                "past_shows": past_shows,
                "upcoming_shows": upcoming_shows,
                "past_shows_count": len(past_shows),
                "upcoming_shows_count": len(upcoming_shows),
                }

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return render_template("pages/home.html")

    finally:
        db.session.close()
        return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
      new_venue = Venue(
        name = request.form.get('name'),
        genres = request.form.getlist('genres'),
        city = request.form.get('city'),
        state = request.form.get('state'),
        address = request.form.get('address'),
        phone = request.form.get('phone'),
        image_link = request.form.get('image_link'),
        facebook_link = request.form.get('facebook_link'),
        website = request.form.get('website_link'),
        seeking_talent = (request.form['seeking_talent'] == 'y'),
        seeking_description = request.form.get('seeking_description'),
      )

      db.session.add(new_venue)
      db.session.commit()

      db.session.refresh(new_venue)
      flash("Venue " + new_venue.name + " was successfully listed!")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(
            "An error occurred. Venue "
            + request.form.get("name")
            + " could not be listed."
        )
    finally:
        db.session.close()
        return redirect(url_for("show_venue", venue_id=new_venue.id))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        return render_template("pages/home.html")

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    #  return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    fields = ["id", "name"]
    artists_data = db.session.query(Artist).options(load_only(*fields)).all()

    return render_template("pages/artists.html", artists=artists_data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Implements search on artists with partial string search. 
    search = request.form['search_term']
    artists = Artist.query.filter(Artist.name.ilike(f'%{search}%'))
    artist_list = []
    for artist in artists:
        item = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(Show.query.filter(Show.artist_id == artist.id).filter(
                Show.start_time > datetime.now()).all())
        }
        artist_list.append(item)
    
    response = {
        "count":len(artist_list),
        "data": artist_list
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = {}
    try:
        current_time = datetime.now()  # datetime.now().strftime('%Y-%m-%d %H:%S:%M')
        artist = db.session.query(Artist).get(artist_id)

        if artist is None:
            return not_found_error(404)

        shows = db.session.query(Show).filter_by(artist_id=artist_id).all()

        upcoming_shows = []
        past_shows = []

        for show in shows:
            venue = Venue.query.get(show.venue_id)

            show_data = {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time)
            }
            if show.start_time > current_time:
                upcoming_shows.append(show_data)
            else:
                past_shows.append(show_data)

        data = {"id": artist.id,
                "name": artist.name,
                "genres": artist.genres,
                "city": artist.city,
                "state": artist.state,
                "phone": artist.phone,
                "website": artist.website,
                "facebook_link": artist.facebook_link,
                "seeking_venue": artist.seeking_venue,
                "seeking_description": artist.seeking_description,
                "image_link": artist.image_link,
                "past_shows": past_shows,
                "upcoming_shows": upcoming_shows,
                "past_shows_count": len(past_shows),
                "upcoming_shows_count": len(upcoming_shows),
                }

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return render_template("pages/home.html")

    finally:
        db.session.close()
        return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm(request.form)

    try:
        artist = Artist.query.get(artist_id)
        if artist is None:
             return not_found_error(404)

        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.image_link.data =  artist.image_link

    except:
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for("index"))

    finally:
        db.session.close()

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  try:
    artist = Artist.query.get(artist_id)
    if artist is None:
        return not_found_error(404)

    artist.name = request.form.get("name")
    artist.genres = request.form.getlist('genres')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.website = request.form.get('website')
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link = request.form.get('image_link')
    artist.seeking_venue = (request.form['seeking_venue'] == 'y')
    artist.seeking_description = request.form.get('seeking_description')
        
    db.session.add(artist)
    db.session.commit()       
    flash("This artist info was successfully updated!")
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(
            "An error occurred. Artist "
            + request.form.get("name")
            + " could not be updated."
    )
    return redirect(url_for("index"))

  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm(request.form)
    try:
        venue = Venue.query.get(venue_id)
        if venue is None:
             return not_found_error(404)

        form.name.data = venue.name
        form.genres.data = venue.genres
        form.address.data = venue.address
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.website_link.data = venue.website
        form.facebook_link.data = venue.facebook_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
        form.image_link.data =  venue.image_link

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for("index"))

    finally:
        db.session.close()
        return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    try:
        venue = Venue.query.get(venue_id)

        venue.name = request.form.get("name")
        venue.genres = request.form.getlist("genres")
        venue.city = request.form.get("city")
        venue.state = request.form.get("state")
        venue.address = request.form.get("address")
        venue.phone = request.form.get("phone")
        venue.facebook_link = request.form.get("facebook_link")
        venue.seeking_talent = (request.form["seeking_talent"] == 'y')
        venue.seeking_description = request.form.get("seeking_description")
        venue.image_link =  request.form.get("image_link")

        db.session.add(venue)
        db.session.commit()

        flash("This venue was successfully updated!")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(
            "An error occurred. Venue "
            + request.form.get("name")
            + " could not be updated."
        )

    finally:
        db.session.close()
        return redirect(url_for("show_venue", venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        new_artist = Artist(
            name = request.form.get("name"), 
            city = request.form.get("city"), 
            state = request.form.get("state"), 
            phone = request.form.get("phone"), 
            genres = request.form.getlist("genres"), 
            website = request.form.get("website"),
            image_link = request.form.get("website"),
            facebook_link=request.form.get("facebook_link"),
            seeking_venue = (request.form['seeking_venue'] == 'y'),
            seeking_description = request.form.get("seeking_description"),
        )
        db.session.add(new_artist)
        db.session.commit()

        db.session.refresh(new_artist)
        flash("Artist " + new_artist.name + " was successfully listed!")

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(
            "An error occurred. Venue "
            + request.form.get("name")
            + " could not be listed."
        )

    finally:
        db.session.close()
        return redirect(url_for('show_artist', artist_id=new_artist.id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows

    data = []
    try:
        shows = db.session.query(Show).all()

        for show in shows:
            artist = Artist.query.get(show.artist_id)

            show_data = {
                "venue_id": show.venue_id,
                "venue_name": Venue.query.get(show.venue_id).name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }

            data.append(show_data)
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong, please try again.")

    finally:
        return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        artist_id = request.form.get("artist_id")
        venue_id = request.form.get("venue_id")
        start_time = request.form.get("start_time")

        new_show = Show(
            artist_id=artist_id, venue_id=venue_id, start_time=start_time
        )

        db.session.add(new_show)
        db.session.commit()

        db.session.refresh(new_show)
        flash("The show was successfully listed!")

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(
            "An error occurred. The show have not be listed."
        )

    finally:
        db.session.close()
        return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
