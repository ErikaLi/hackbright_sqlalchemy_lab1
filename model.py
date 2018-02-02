"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import correlation
# import doctest

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "\n<User user_id={} email={}>".format(self.user_id,
                                                     self.email)

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(10), nullable=True)

    def similarity(self, other):
        """Return Pearson rating for user compared to other user."""

        u_ratings = {}
        paired_ratings = []

        for r in self.ratings:
            u_ratings[r.movie_id] = r

        for r in other.ratings:
            u_r = u_ratings.get(r.movie_id)
            if u_r:
                paired_ratings.append((u_r.score, r.score))

        if paired_ratings:
            return correlation.pearson(paired_ratings)

        else:
            return 0.0

    def predict_rating(self, movie):
        """Based on other users who have rated a given movie, predict this user's score"""

        # get a list of other users who have rated the selected movie
        other_users = [rating.user for rating in movie.ratings]

        import pdb; pdb.set_trace()
        # initiate an empty list
        positive_sim = []
        negative_sim = []

        # loop through the list of users who have rated the movie,
        # calculate pearson similarity value
        # append a tuple of the pearson value and the user object to the comparison list
        for other_user in other_users:
            sim = self.similarity(other_user)
            rating = Rating.query.filter_by(movie_id=movie.movie_id,
                                            user_id=other_user.user_id).one()

        # FIX THIS
        # if users who rated this movie did not rate any movies that this user rated, sims will be 0,
        # and it will throw a division by 0 error
            if sim > 0:
                positive_sim.append(tuple([sim, rating.score]))
            else:
                negative_sim.append(tuple([sim, rating.score]))

        numerator_pos = sum([r * sim for sim, r in positive_sim])
        numerator_neg = sum([abs(r-6) * -sim for sim, r in negative_sim])

        denominator = sum([abs(sim) for sim, r in positive_sim]) + sum([abs(sim) for sim, r in negative_sim])

        return (numerator_pos + numerator_neg) / denominator


# Put your Movie and Rating model classes here.
class Movie(db.Model):
    """Movie table."""

    __tablename__ = "movies"

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "\n<Movie movie_id={} title={}>".format(self.movie_id,
                                                       self.title)

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(512), nullable=True)


class Rating(db.Model):
    """Movie ratings by a user"""

    __tablename__ = "ratings"

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "\n<Rating rating_id={} movie_id={} user_id={} score={}>".format(self.rating_id,
                                                                                self.movie_id,
                                                                                self.user_id,
                                                                                self.score)

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    movie = db.relationship('Movie', backref='ratings')
    user = db.relationship('User', backref='ratings')


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def test(user_id, movie_id):
    """Test the prediction function!"""

    u = User.query.get(user_id)
    m = Movie.query.get(movie_id)

    return u.predict_rating(m)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
