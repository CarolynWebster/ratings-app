"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User
from model import Rating
from model import Movie

from model import connect_to_db, db
from server import app
from datetime import datetime


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    print "Movies"

    # make sure we don't duplicate rows
    Movie.query.delete()

    #read u.item file and pull data
    for row in open("seed_data/u.item"):
        row = row.rstrip()
        row = row.split("|")

        # unpack the necessary values
        movie_id = row[0]
        raw_title = row[1]
        raw_date = row[2]
        imdb_url = row[4]

        #remove the (Year) from the title
        #split based on a space and (
        title = raw_title[0:-7]

        #parses date string into a datetime object
        # %d = date %b = abbreviated month %Y = year
        if raw_date:
            released_at = datetime.strptime(raw_date, "%d-%b-%Y")
        else:
            released_at = None

        #instantiate movie object
        movie = Movie(movie_id=movie_id,
                      title=title,
                      released_at=released_at,
                      imdb_url=imdb_url)

        #prime movie to be added to the database
        db.session.add(movie)

    #commit all movies to the the movie database
    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""

    print "Ratings"

    #make sure we don't duplicate rows
    Rating.query.delete()

    for row in open("seed_data/u.data"):
        row = row.rstrip()

        #unpack row into variables
        user_id, movie_id, score, timestamp = row.split("\t")

        #instantiate rating object
        rating = Rating(user_id=user_id, movie_id=movie_id, score=score)

        #prime rating to be added to the db
        db.session.add(rating)

    #commit all rating to the ratings database
    db.session.commit()



def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
