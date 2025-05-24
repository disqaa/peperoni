from app import create_app
from app.extensions import db
from app.models import Product, Ingredient

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()


    cheese      = Ingredient(name="Сыр моцарелла", price=0.5)
    sauce       = Ingredient(name="Томатный соус", price=0.5)
    pepperoni   = Ingredient(name="Пепперони", price=0.5)
    mushrooms   = Ingredient(name="Грибы", price=0.5)
    olives      = Ingredient(name="Оливки", price=0.5)


    margherita = Product(
        name="Маргарита",
        description="Классика: томатный соус, сыр моцарелла, базилик.",
        price=7.99,
        image_url="/static/images/photo_2025-05-25_01-24-28.jpg",
        ingredients=[sauce, cheese]
    )

    pepperoni_pizza = Product(
        name="Пепперони",
        description="Щедрая порция пепперони и моцареллы.",
        price=9.49,
        image_url="/static/images/",
        ingredients=[sauce, cheese, pepperoni]
    )

    fungi = Product(
        name="чиназес",
        description="Чесночные, веселые грибы, грибы, томатный соус и сыр.",
        price=8.99,
        image_url="/static/images/.jpg",
        ingredients=[sauce, cheese, mushrooms]
    )

    db.session.add_all([margherita, pepperoni_pizza, fungi, olives])  # olives отдельно
    db.session.commit()
    print("Данные загружены, все ура")
