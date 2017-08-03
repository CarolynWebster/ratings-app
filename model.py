"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from correlation import pearson

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)


    def similarity(self, other_user):
        """Finds common movies this user and another user"""

        # make a dict to hold the users ratings
        this_user_ratings = {}

        #create list to hold shared ratings
        shared_ratings = []

        #build the dictionary of ratings for this user
        for rating in self.ratings:
            this_user_ratings[rating.movie_id] = rating.score

        #look at ratings from another user and if the movie id is in
        #this users dictionary - add both scores as a tuple to shared rating list
        for m_id in other_user.ratings:
            if m_id.movie_id in this_user_ratings:
                #get this user's score and other user's score
                user_score = this_user_ratings[m_id.movie_id]
                other_score = m_id.score
                #add to the list as a tuple
                shared_ratings.append((user_score, other_score))

        #return list of shared ratings
        if shared_ratings:
            return pearson(shared_ratings)

        else:
            return 0.0


    def predict_rating(self, movie):
        """Predict user's rating of a movie."""

        #get list of ratings objects for the selected movie
        other_ratings = movie.ratings

        #build a list of tuples holding the pearson similarity for the user
        #who made the rating and the rating object itself
        similarities = [
            (self.similarity(r.user), r)
            for r in other_ratings
        ]

        #sort them by highest similarities at the front of the list
        similarities.sort(reverse=True)

        #if the similarity score is greater than 0
        # add the tuple to the similarities list
        similarities = [(sim, r) for sim, r in similarities
                        if sim > 0]

        # if no similarities exist, this person has very unique taste, return none
        if not similarities:
            return None

        # go through the tuples in similarities and get the sum of all the ratings
        # after you multiply the rating against their similarity
        numerator = sum([r.score * sim for sim, r in similarities])

        #go through the tuples in similarities and get the sum of all similarities
        denominator = sum([sim for sim, r in similarities])

        # divide those to get predictive rating
        return numerator/denominator


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id,
                                               self.email)


# Put your Movie and Rating model classes here.
class Movie(db.Model):
    """Movie information"""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(90), nullable=False)
    released_at = db.Column(db.DateTime)
    imdb_url = db.Column(db.String(150))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Movie movie_id=%s title=%s>" % (self.movie_id,
                                               self.title)


class Rating(db.Model):
    """Ratings of movies by users"""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer, nullable=False)

    #define relationship with user table
    user = db.relationship("User", backref=db.backref("ratings", order_by=rating_id))

    # Define relationship with movie table
    movie = db.relationship("Movie", backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Rating user_id=%s movie_id=%s score=%s>" % (self.user_id,
                                               self.movie_id, self.score)

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
