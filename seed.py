"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User
from model import Rating
from model import Movie
import datetime
from model import connect_to_db, db
from server import app


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
    print "Movie"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate movies
    Movie.query.delete()
    # Read u.item file and insert data
    for row in open("seed_data/u.item"):
        info = row.rstrip().split("|")
        movie_id = info[0]
        title_str = info[1]
        title_str = title_str.decode("latin-1")
        if title_str[-1] == ')':
            title = title_str[:-7]
        else:
            title = title_str

        released_str = info[2]
        if released_str:
            released_at = datetime.datetime.strptime(released_str, "%d-%b-%Y")
        else:
            released_at = None

        imdb_url = info[4]

        movie = Movie(movie_id=movie_id,
                      title=title,
                      released_at=released_at,
                      imdb_url=imdb_url)

        # We need to add to the session or it won't ever be stored
        db.session.add(movie)

    # Once we're done, we should commit our work
    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""

    print "Ratings"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate ratings
    Rating.query.delete()

    i = 0

    # Read u.data file and insert data
    for row in open("seed_data/u.data"):
        i += 1
        if i % 1000 == 0:
            print i

        info = row.rstrip().split("\t")
        # user_id, movie_id, score = row[:-1]
        user_id, movie_id, score, _ = info

        user_id = int(user_id)
        movie_id = int(movie_id)
        score = int(score)

        rating = Rating(user_id=user_id,
                        movie_id=movie_id,
                        score=score)

        # We need to add to the session or it won't ever be stored
        db.session.add(rating)

    # Once we're done, we should commit our work
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
