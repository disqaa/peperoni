from app import create_app
from app.extensions import db
from app.models import Product, Ingredient

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()

    cheese   = Ingredient(name="Сыр моцарелла",   price=0.5)
    sauce    = Ingredient(name="Томатный соус",   price=0.3)
    pepperoni= Ingredient(name="Пепперони",       price=0.7)
    mushrooms= Ingredient(name="Грибы",           price=0.6)
    olives   = Ingredient(name="Оливки",          price=0.4)
    basil    = Ingredient(name="Базилик",         price=0.2)
    shrimp   = Ingredient(name="Креветки",        price=1.0)
    chili    = Ingredient(name="Острый перец",    price=0.3)
    bacon    = Ingredient(name="Бекон",           price=0.8)
    ham      = Ingredient(name="Ветчина",         price=0.6)
    chicken  = Ingredient(name="Курица",          price=0.7)
    beef     = Ingredient(name="Говядина",        price=0.8)
    salad    = Ingredient(name="Салат",           price=0.4)
    cucumber = Ingredient(name="Огурцы",          price=0.5)
    onion    = Ingredient(name="Лук",             price=0.3)

    pizzas = [
        Product(name="Маргарита",
                description="Классика: соус, моцарелла, базилик.",
                price=7.99,
                image_url="pizza4.jpg",
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
                image_url="grib.jpg",
                category="веган",
                ingredients=[sauce, cheese, mushrooms]),

        Product(name="4 Сыра",
                description="Моцарелла, горгонзола, пармезан, чеддер.",
                price=10.49,
                image_url="cheese.jpg",
                category="сырная",
                ingredients=[sauce, cheese]),

        Product(name="Гавайская",
                description="Курица, ананас, сыр.",
                price=9.99,
                image_url="anan.jpg",
                category="мясная",
                ingredients=[sauce, cheese, bacon]),

        Product(name="Острая Мексиканская",
                description="Халапеньо, пепперони, острый перец.",
                price=10.99,
                image_url="pizza3.jpg",
                category="острая",
                ingredients=[sauce, cheese, pepperoni, chili]),

        Product(name="С креветками",
                description="Томатный соус, креветки, моцарелла.",
                price=11.99,
                image_url="krev.jpg",
                category="морепродукты",
                ingredients=[sauce, cheese, shrimp]),

        Product(name="Веган",
                description="Овощи гриль, томаты, оливки.",
                price=9.29,
                image_url="pizza2.jpg",
                category="веган",
                ingredients=[sauce, olives, mushrooms]),

        Product(name="Бекон BBQ",
                description="Соус BBQ, бекон, лук красный.",
                price=11.49,
                image_url="photo_2025-05-25_01-24-28.jpg",
                category="мясная",
                ingredients=[sauce, cheese, bacon, chili]),
        Product(name="Мясная",
                description = "Полный фарш: фарш говяжий, охотничьи колбаски, пепперони.",
                price = 7.99,
                image_url = "meet.jpg",
                category = "мясная",
                ingredients = [pepperoni, bacon, ham, beef, cheese]),
        Product(name="Бургер-пицца",
                description = "Вы думали это вкусно-и-точка? А не тут то было!",
                price = 10.99,
                image_url = "burger.jpg",category = "мясная",
                ingredients = [pepperoni, chicken, sauce, cucumber, cheese]),
        Product(name="Крестьянская",
                description = "Не как в 16-17 веке, но тоже неплохо, к тому же ее не отменить",
                price = 9.52,
                image_url = "krest.jpg",
                category = "мясная",
                ingredients = [bacon, mushrooms, cheese, beef]),
        Product(name="Песто",
                description = "Когда в желудке есть место, не скупитесть пиццой Песто!",
                price = 9.09,
                image_url = "pesto.jpg",
                category = "веган",
                ingredients = [salad, sauce, cheese]),
        Product(name="Капрезе",
                description = "Будто лето в Италии решило поселиться прямо у вас на языке!",
                price = 10.99,
                image_url = "kapreze.jpg",
                category = "веган",
                ingredients = [cheese, olives, sauce, basil]),
        Product(name="Диабло",
                description = "Если есть лишние 15 минут на уборную, то это луяший вариант",
                price = 10.99,
                image_url = "diablo.jpg",
                category = "острая",
                ingredients = [chili, sauce, basil, beef, cheese]),

    ]

    db.session.add_all([cheese, sauce, pepperoni, mushrooms, olives, basil, shrimp, chili, bacon])
    db.session.add_all(pizzas)
    db.session.commit()
    print("✓ БД заполнена пиццами")
