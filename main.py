import random
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm.exc import NoResultFound


app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
api_key = "SALAMALEYKUM"


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    all_cafes = db.session.execute(db.select(Cafe))
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes.scalars()])


# HTTP GET - Read Record
@app.route("/search", methods=["POST", "GET"])
def search_cafe_by_location():
    query_loc = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_loc))
    print(result)
    all_cafes = result.scalars().all()
    if all_cafes:
        return jsonify(cafe=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry we dont have a cafe at that location."})


@app.route("/search_name", methods=["POST", "GET"])
def search_by_name():
    query_name = request.args.get("name")
    result = db.session.execute(db.select(Cafe).where(Cafe.name == query_name))
    print(result)
    cafe = result.scalar()
    print(cafe)
    if cafe:
        return jsonify(response={f"cafe": [cafe.to_dict()]})
    else:
        return jsonify(response={"Not found": "Cafe with that name doesn't exists in the database"})


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.args.get("name"),
        map_url=request.args.get("map_url"),
        img_url=request.args.get("img_url"),
        location=request.args.get("location"),
        seats=request.args.get("seats"),
        has_toilet=bool(request.args.get("has_toilet")),
        has_wifi=bool(request.args.get("has_wifi")),
        has_sockets=bool(request.args.get("has_sockets")),
        can_take_calls=bool(request.args.get("can_take_calls")),
        coffee_price=str(request.args.get("coffee_price")),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={
        "Success": "Successfully added new cafe"
    })


# HTTP PUT/PATCH - Update Record
@app.route("/update_price/<int:cafe_id>", methods=["PATCH", "PUT"])
def update_cafe_data(cafe_id):
    try:
        data = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar_one()
        data.coffee_price = request.args.get("new_price")
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the cafe data in the database"})
    except NoResultFound:
        return jsonify(response={"Not Found": "Sorry, there is no cafe with such id."})


# HTTP DELETE - Delete Record
@app.route("/delete/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    if request.args.get("api_key") == "Davlatbek is best data scientist":
        data = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        if data:
            db.session.delete(data)
            db.session.commit()
            return jsonify(response={"Success": f"Successfully deleted the cafe data with id: {cafe_id}"})
        else:
            return jsonify(response={"Not Found": f"Sorry, cafe with id {cafe_id} does not exist in database."})
    else:
        return jsonify(response={"Authentication error": "Sorry, wrong api key"})


if __name__ == '__main__':
    app.run(debug=True)
