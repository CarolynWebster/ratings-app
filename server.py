"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    # if the user_email is stored in the session
    # toggle log in/log out text
    if 'user_email' in session:
        btn_text = "Log Out"
    else:
        btn_text = "Log In"

    return render_template('homepage.html', btn_text=btn_text)


@app.route('/users')
def show_users():
    """Show list of users"""

    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/movies')
def show_movies():
    """Show list of movies"""

    # get list of all movies, ordered by their title, and offset by 1
    # bc there is no movie with a 0 id
    movies = Movie.query.order_by(Movie.title).offset(1).all()
    return render_template('movies.html', movies=movies)


@app.route('/movies/<movie_id>')
def show_movie_info(movie_id):
    """Gets info and ratings for a specific movie"""

    movie = Movie.query.filter(Movie.movie_id == movie_id).first()
    #ratings = movie.ratings

    #movie_url = "movies/" + str(movie_id)

    return render_template('movie-info.html', movie=movie)


@app.route('/register', methods=["GET"])
def show_reg_form():
    """Show form to register user"""

    return render_template('registration.html')


@app.route('/register', methods=['POST'])
def register_user():
    """Checks db for user and adds user if new"""

    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")

    #check if user exists in db
    user_check = User.query.filter_by(email=email).first()
    if user_check:
        #let us know user exists already
        flash('You have already registered. Please log in.')
        return redirect('/login')
    else:
        #create user
        user = User(email=email,
                    password=password,
                    age=age,
                    zipcode=zipcode)
        #prime user to be added to db
        db.session.add(user)
        #commit user to db
        db.session.commit()

        return redirect("/")


@app.route('/login', methods=["GET"])
def show_login():
    """Log in existing user"""

    return render_template('/login.html')


@app.route('/logout')
def logout_user():
    """Logs a user out"""

    # clear email from the session
    session.clear()

    # tell the user they are logged out
    flash("You have successfully logged out")

    return redirect('/')


@app.route('/login', methods=["POST"])
def handle_login():
    """Check is user is registered"""

    # get email and password info
    email = request.form.get("email")
    password = request.form.get("password")

    #check if user is in db
    user_check = User.query.filter_by(email=email).first()

    #if user already exists check the password
    if user_check:
        if user_check.password == password:
            #set flash message telling them login successful
            flash("You have successfully logged in")
            #add user's email to the session
            session['user_email'] = email
            #get the url for that user's info
            user_url = "/users/" + str(user_check.user_id)
            #send them to their own page
            return redirect(user_url)
        else:
            # tell them the password doesn't match
            flash("That password does not match our records.")
            # redirect back to login so they can try again
            return redirect("/login")
    else:
        flash("No user is registered with that email. Please register.")
        return redirect('/register')



@app.route('/users/<user_id>')
def load_user_info(user_id):
    """Load info about a specific user"""

    user = User.query.filter(User.user_id == user_id).first()
    if user:
        user_age = user.age
        user_zip = user.zipcode
        user_movies = user.ratings
        return render_template('/user-info.html', user=user)
    else:
        return "No user exists with that ID. <a href='/users'>Go back to users list</a>"



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(port=5000, host='0.0.0.0')
