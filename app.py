# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
import sqlite3

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
    genre = fields.Nested(GenreSchema)
    director = fields.Nested(DirectorSchema)


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
            movies = db.session.query(Movie).filter(Movie.director_id == int(director_id),
                                                    Movie.genre_id == int(genre_id)).all()
            if movies:
                return movies_schema.dump(movies), 200
            else:
                return "Таких режиссёра и жанра не существует", 404
        elif director_id:
            movies = db.session.query(Movie).filter(Movie.director_id == int(director_id)).all()
            if movies:
                return movies_schema.dump(movies), 200
            else:
                return "Такого режиссёра не существует", 404
        elif genre_id:
            movies = db.session.query(Movie).filter(Movie.genre_id == int(genre_id)).all()
            if movies:
                return movies_schema.dump(movies), 200
            else:
                return "Такого жанра не существует", 404
        else:
            movies = db.session.query(Movie).all()
            return movies_schema.dump(movies), 200

    def post(self):
        post_data = request.json
        movie = Movie(**post_data)
        try:
            db.session.add(movie)
            db.session.commit()
        except sqlite3.OperationalError:
            db.session.rollback()
            return "Не удалось добавить фильм", 404
        else:
            return "Фильм добавлен", 201


@movies_namespace.route("/<int:id>")
class MovieView(Resource):
    def get(self, id):
        movie = db.session.query(Movie).get(id)
        if movie:
            return movie_schema.dump(movie), 200
        else:
            return "Такого фильма не существует", 404

    def put(self, id):
        put_data = request.json
        movie = db.session.query(Movie).get(id)
        if movie:
            try:
                movie.title = put_data.get("title")
                movie.description = put_data.get("description")
                movie.trailer = put_data.get("trailer")
                movie.year = put_data.get("year")
                movie.rating = put_data.get("rating")
                movie.genre_id = put_data.get("genre_id")
                movie.director_id = put_data.get("director_id")
                db.session.add(movie)
                db.session.commit()
            except sqlite3.OperationalError:
                db.session.rollback()
                return "Не удалось изменить фильм", 404
            else:
                return "Фильм изменён", 200
        else:
            return "Такого фильма не существует", 404

    def delete(self, id):
        movie = db.session.query(Movie).get(id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return "Фильм удалён", 200
        else:
            return "Такого фильма не существует", 404


@directors_namespace.route("/")
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director).all()
        return directors_schema.dump(directors), 200

    def post(self):
        post_data = request.json
        director = Director(**post_data)
        try:
            db.session.add(director)
            db.session.commit()
        except sqlite3.OperationalError:
            db.session.rollback()
            return "Не удалось добавить режиссёра", 404
        else:
            return "Режиссёр добавлен", 201


@directors_namespace.route("/<int:id>")
class DirectorView(Resource):
    def get(self, id):
        director = db.session.query(Director).get(id)
        if director:
            return director_schema.dump(director), 200
        else:
            return "Такого режиссёра не существует", 404

    def put(self, id):
        put_data = request.json
        director = db.session.query(Director).get(id)
        if director:
            try:
                director.name = put_data.get("name")
                db.session.add(director)
                db.session.commit()
            except sqlite3.OperationalError:
                db.session.rollback()
                return "Не удалось изменить режиссёра", 404
            else:
                return "Режиссёр изменён", 200
        else:
            return "Такого режиссёра не существует", 404

    def delete(self, id):
        director = db.session.query(Director).get(id)
        if director:
            db.session.delete(director)
            db.session.commit()
            return "Режиссёр удалён", 200
        else:
            return "Такого режиссёра не существует", 404


@genres_namespace.route("/")
class GenresView(Resource):
    def get(self):
        genres = db.session.query(Genre).all()
        return genres_schema.dump(genres), 200

    def post(self):
        post_data = request.json
        genre = Genre(**post_data)
        try:
            db.session.add(genre)
            db.session.commit()
        except sqlite3.OperationalError:
            db.session.rollback()
            return "Не удалось добавить жанр", 404
        else:
            return "Жанр добавлен", 201


@genres_namespace.route("/<int:id>")
class GenreView(Resource):
    def get(self, id):
        genre = db.session.query(Genre).get(id)
        if genre:
            return genre_schema.dump(genre), 200
        else:
            return "Такого жанра не существует", 404

    def put(self, id):
        put_data = request.json
        genre = db.session.query(Genre).get(id)
        if genre:
            try:
                genre.name = put_data.get("name")
                db.session.add(genre)
                db.session.commit()
            except sqlite3.OperationalError:
                db.session.rollback()
                return "Не удалось изменить жанр", 404
            else:
                return "Жанр изменён", 200
        else:
            return "Такого жанра не существует", 404

    def delete(self, id):
        genre = db.session.query(Genre).get(id)
        if genre:
            db.session.delete(genre)
            db.session.commit()
            return "Жанр удалён", 200
        else:
            return "Такого жанра не существует", 404


if __name__ == '__main__':
    app.run(debug=True)
