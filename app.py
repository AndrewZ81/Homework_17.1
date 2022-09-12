# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["RESTX_JSON"] = {'ensure_ascii': False}
db = SQLAlchemy(app)


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre = fields.Pluck(GenreSchema, "name")
    director = fields.Pluck(DirectorSchema, "name")


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

api = Api(app)
movies_namespace = api.namespace("movies")
genres_namespace = api.namespace("genres")
directors_namespace = api.namespace("directors")


@movies_namespace.route("/")
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")
        if director_id and genre_id:
            movies = Movie.query.filter(Movie.director_id == int(director_id),
                                        Movie.genre_id == int(genre_id)).all()
            if movies:
                return movies_schema.dump(movies), 200
            else:
                return "Такого director_id и genre_id не существует", 404
        elif director_id:
            movies = Movie.query.filter(Movie.director_id == int(director_id)).all()
            if movies:
                return movies_schema.dump(movies), 200
            else:
                return "Такого director_id не существует", 404
        elif genre_id:
            movies = Movie.query.filter(Movie.genre_id == int(genre_id)).all()
            if movies:
                return movies_schema.dump(movies), 200
            else:
                return "Такого genre_id не существует", 404
        else:
            movies = Movie.query.all()
            return movies_schema.dump(movies), 200


@movies_namespace.route("/<int:id>")
class MovieView(Resource):
    def get(self, id):
        movie = db.session.query(Movie).get(id)
        if movie:
            return movie_schema.dump(movie), 200
        else:
            return "Такого ID не существует", 404


if __name__ == '__main__':
    app.run(debug=True)
