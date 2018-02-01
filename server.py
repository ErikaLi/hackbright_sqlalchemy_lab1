"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import (Flask, render_template, redirect, request, flash,
                   session)

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

    return render_template("homepage.html")


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<movie_id>", methods=["GET"])
def display_movie(movie_id):
    """Display info for a certain movie"""

    movie = Movie.query.get(movie_id)
    return render_template("movie_profile.html", movie=movie)


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/users/<user_id>", methods=["GET"])
def display_user(user_id):
    """Display info of a certain user"""

    user = User.query.get(user_id)
    return render_template("user_profile.html", user=user)


@app.route('/register', methods=["GET"])
def register_form():
    """Display registration form"""

    return render_template('register_form.html')


@app.route('/register', methods=["POST"])
def register_process():
    """Process registration form"""

    email = request.form['email']
    password = request.form['password']
    current_user = User.query.filter(User.email == email).first()

    if current_user:
        flash("This email is already in use.")
        return redirect("/")
    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Successfully registered!")
        return redirect("/")


@app.route('/login', methods=["GET"])
def login_form():
    """Display login form"""

    return render_template('login_form.html')


@app.route('/login', methods=["POST"])
def login_process():
    """Process login form"""

    email = request.form['email']
    password = request.form['password']
    current_user = User.query.filter(User.email == email).first()

    if current_user and password == current_user.password:

        session['current_user'] = current_user.user_id
        flash("Successfully logged in!")
        return redirect("/users/" + str(current_user.user_id))
    else:
        flash("Invalid log in, please try again or register as a new user")
        return redirect("/")


@app.route('/logout', methods=["GET"])
def logout_process():
    """Process logout form"""

    session.pop("current_user")
    flash("Successfully logged out!")

    return redirect("/")


@app.route('/rate', methods=['POST'])
def rate_movie():
    """Add or update rating for a movie by a certain user."""
    movie_id = request.form['movie_id']
    rating = request.form['rating']
    user_id = session.get('current_user')
    current_rating = Rating.query.filter(Rating.movie_id == movie_id,
                                         Rating.user_id == user_id).first()
    if current_rating:
        # update if we already have a rating
        current_rating.score = rating
    else:
        new_rating = Rating(movie_id=movie_id, user_id=user_id, score=rating)
        db.session.add(new_rating)
    db.session.commit()
    flash("Your rating was added!")
    return redirect("/movies/" + str(movie_id))


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
