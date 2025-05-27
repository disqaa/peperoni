from app import create_app
from app.extensions import db
from app.models import Product, Ingredient

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()

    cheese   = Ingredient(name="Сыр моцарелла",  price=0.5)
    sauce    = Ingredient(name="Томатный соус",   price=0.3)
    pepperoni= Ingredient(name="Пепперони",       price=0.7)
    mushrooms= Ingredient(name="Грибы",           price=0.6)
    olives   = Ingredient(name="Оливки",          price=0.4)
    basil    = Ingredient(name="Базилик",         price=0.2)
    shrimp   = Ingredient(name="Креветки",        price=1.0)
    chili    = Ingredient(name="Острый перец",    price=0.3)
    bacon    = Ingredient(name="Бекон",           price=0.8)

    pizzas = [
        Product(name="Маргарита",
                description="Классика: соус, моцарелла, базилик.",
                price=7.99,
                image_url="pizza2.jpg",
                category="веган",
                ingredients=[sauce, cheese, basil]),

        Product(name="Пепперони",
                description="Пикантная пепперони и сыр.",
                price=9.49,
                image_url="pizza7.jpg",
                category="мясная",
                ingredients=[sauce, cheese, pepperoni]),

        Product(name="Грибная",
                description="Моцарелла и ароматные грибы.",
                price=8.99,
                image_url="photo_2025-05-25_01-24-28.jpg",
                category="веган",
                ingredients=[sauce, cheese, mushrooms]),

        Product(name="4 Сыра",
                description="Моцарелла, горгонзола, пармезан, чеддер.",
                price=10.49,
                image_url="pizza4.jpg",
                category="сырная",
                ingredients=[sauce, cheese]),

        Product(name="Гавайская",
                description="Курица, ананас, сыр.",
                price=9.99,
                image_url="pizza7.jpg",
                category="мясная",
                ingredients=[sauce, cheese, bacon]),

        Product(name="Острая Мексиканская",
                description="Халапеньо, пепперони, острый перец.",
                price=10.99,
                image_url="pizza7.jpg",
                category="острая",
                ingredients=[sauce, cheese, pepperoni, chili]),

        Product(name="С креветками",
                description="Томатный соус, креветки, моцарелла.",
                price=11.99,
                image_url="pizza7.jpg",
                category="морепродукты",
                ingredients=[sauce, cheese, shrimp]),

        Product(name="Веган",
                description="Овощи гриль, томаты, оливки.",
                price=9.29,
                image_url="pizza7.jpg",
                category="веган",
                ingredients=[sauce, olives, mushrooms]),

        Product(name="Бекон BBQ",
                description="Соус BBQ, бекон, лук красный.",
                price=11.49,
                image_url="pizza7.jpg",
                category="мясная",
                ingredients=[sauce, cheese, bacon, chili]),
    ]

    db.session.add_all([cheese, sauce, pepperoni, mushrooms, olives, basil, shrimp, chili, bacon])
    db.session.add_all(pizzas)
    db.session.commit()
    print("✓ БД заполнена 9 пиццами")
