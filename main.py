from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/all")
def get_all():
    all_cafes = db.session.query(Cafe).all()
    if all_cafes:
        list_cafes = [cafe.to_dict() for cafe in all_cafes]
        return jsonify(cafes=list_cafes)
    else:
        return jsonify(error={"Not Found": "No cafes available."})


@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    cafe_details = random_cafe.to_dict()
    return jsonify(cafe=cafe_details)


@app.route("/search")
def search_by_loc():
    cafe_loc = request.args.get("loc")
    searched_cafe = db.session.query(Cafe).filter_by(location=cafe_loc).first()
    if searched_cafe:
        return jsonify(cafe=searched_cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record
@app.route("/add", methods=['GET', 'POST'])
def add_cafe():
    if request.method == 'POST':
        try:
            new_cafe = Cafe(
                name=request.form["name"],
                location=request.form["location"],
                coffee_price=request.form["coffee_price"],
                seats=request.form["seats"],
                map_url=request.form["map_url"],
                img_url=request.form["img_url"],
                has_toilet=bool(request.form["has_toilet"]),
                has_wifi=bool(request.form["has_wifi"]),
                has_sockets=bool(request.form["has_sockets"]),
                can_take_calls=bool(request.form["can_take_calls"])
            )
            db.session.add(new_cafe)
            db.session.commit()
            return jsonify(response={"Success": "Successfully added new cafe"})
        except:
            return jsonify(response={"error": "Couldn't add cafe"}), 400
    return render_template("add.html")


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe_to_update = db.session.query(Cafe).get(cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price!"}), 200
    else:
        return jsonify(error={"Error": "Cafe with this id doesn't exist"}), 404


# HTTP DELETE
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 401


if __name__ == '__main__':
    app.run(debug=True)
