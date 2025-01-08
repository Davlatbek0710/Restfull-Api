import random
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm.exc import NoResultFound

# Initialize the Flask app
app = Flask(__name__)


# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Connect to the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'  # Database URI
db = SQLAlchemy(model_class=Base)  # Initialize SQLAlchemy with custom base
db.init_app(app)  # Bind SQLAlchemy to the Flask app

# API key for authentication (should be stored securely in a real-world app)
api_key = "SALAMALEYKUM"


# Cafe TABLE Configuration
class Cafe(db.Model):
    # Table columns with type annotations and constraints
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

    # Convert the model instance to a dictionary for JSON serialization
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# Create the database tables if they don't exist
with app.app_context():
    db.create_all()


# Root route to serve the homepage
@app.route("/")
def home():
    return render_template("index.html")  # Render the homepage


# Route to fetch a random cafe
@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))  # Fetch all cafes
    all_cafes = result.scalars().all()  # Convert query result to list
    random_cafe = random.choice(all_cafes)  # Pick a random cafe
    return jsonify(cafe=random_cafe.to_dict())  # Return as JSON


# Route to fetch all cafes
@app.route("/all")
def get_all_cafes():
    all_cafes = db.session.execute(db.select(Cafe))  # Fetch all cafes
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes.scalars()])  # Return all cafes as JSON


# Route to search cafes by location
@app.route("/search", methods=["POST", "GET"])
def search_cafe_by_location():
    query_loc = request.args.get("loc")  # Get location from query params
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_loc))  # Query by location
    all_cafes = result.scalars().all()  # Get matching cafes
    if all_cafes:
        return jsonify(cafe=[cafe.to_dict() for cafe in all_cafes])  # Return matching cafes
    else:
        return jsonify(error={"Not Found": "Sorry we dont have a cafe at that location."})  # Error response


# Route to search a cafe by name
@app.route("/search_name", methods=["POST", "GET"])
def search_by_name():
    query_name = request.args.get("name")  # Get cafe name from query params
    result = db.session.execute(db.select(Cafe).where(Cafe.name == query_name))  # Query by name
    cafe = result.scalar()  # Fetch single result
    if cafe:
        return jsonify(response={f"cafe": [cafe.to_dict()]})  # Return matching cafe
    else:
        return jsonify(response={"Not found": "Cafe with that name doesn't exist in the database"})  # Error response


# Route to add a new cafe
@app.route("/add", methods=["POST"])
def add_cafe():
    # Create a new cafe instance from query parameters
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
    db.session.add(new_cafe)  # Add the new cafe to the database session
    db.session.commit()  # Commit changes to the database
    return jsonify(response={"Success": "Successfully added new cafe"})  # Success response


# Route to update cafe data (price)
@app.route("/update_price/<int:cafe_id>", methods=["PATCH", "PUT"])
def update_cafe_data(cafe_id):
    try:
        # Find the cafe by ID
        data = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar_one()
        data.coffee_price = request.args.get("new_price")  # Update coffee price
        db.session.commit()  # Commit changes
        return jsonify(response={"success": "Successfully updated the cafe data in the database"})  # Success response
    except NoResultFound:
        return jsonify(response={"Not Found": "Sorry, there is no cafe with such id."})  # Error response


# Route to delete a cafe by ID
@app.route("/delete/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    if request.args.get("api_key") == "Davlatbek is best data scientist":  # Check API key
        data = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()  # Find cafe by ID
        if data:
            db.session.delete(data)  # Delete the cafe
            db.session.commit()  # Commit changes
            return jsonify(response={"Success": f"Successfully deleted the cafe data with id: {cafe_id}"})  # Success
        else:
            return jsonify(
                response={"Not Found": f"Sorry, cafe with id {cafe_id} does not exist in database."})  # Error
    else:
        return jsonify(response={"Authentication error": "Sorry, wrong api key"})  # Authentication error


# Run the app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
